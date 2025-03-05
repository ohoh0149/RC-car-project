import cv2
import math
from time import sleep
from future.utils import tobytes
from scipy.constants import point
from sympy import false
from ultralytics import YOLO
import Function_Library as fl

########### 비디오 ############
# video_path = "camera_view_outerlane.mp4"  # 동영상 파일 경로
# cap = cv2.VideoCapture(video_path)

########### 카메라 ############
cap = cv2.VideoCapture(0)  # 맥북의 기본 카메라에 접근
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 10)

# YOLOv8 모델 불러오기
model = YOLO("12k_cross.pt")  # .pt 파일 경로 중요!

# 아두이노 세팅
arduino_port = '/dev/cu.usbmodem1201' # 이거 상황에 따라 바꿔야
ser = fl.libARDUINO()
comm = ser.init(arduino_port, 9600)

# 아두이노에 5 보내면서 시작: 차량을 직진시킴
comm.write(int(5).to_bytes(1,"little"))

# 아두이노로부터 받았는지 여부
received = False

# 아두이노로부터 들어온 값
ack="OK"

# rcx 처음이라면
first_rcx_flag=True

# crosswalk 탐지 횟수
crosswalk_stack=0

while True:
    # ack가 'OK'일 때까지 반복 대기 (필요할 때만)
    if not received:
        while ack != "OK":
            ack = comm.readline().decode().strip()
        received=True

    # received 받지 못했다면
    if not received:
        continue

    # 카메라로부터 화면 읽어오기
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO 모델로 객체 분할
    results = model(frame, task='segment')  # segmentation task 수행

    # None 이면 다시 탐색
    if results[0].masks is None:
        continue

    # lane 정보를 담을 딕셔너리 생성
    lane_dict = {}

    # 독립 보장
    for i, mask in enumerate(results[0].masks.xy):  # .xy, .xyn
        idx = results[0].boxes.cls[i].item()  # 어떤 객체인지 (0: lane1, 1: lane2, ...)
        conf = results[0].boxes.conf[i].item()  # 정확도 (0 ~ 1)

        # 각 lane별로 가장 높은 confidence를 가진 segment만 선택
        if idx not in lane_dict or lane_dict[idx][0] < conf:
            lane_dict[idx] = (conf, mask)

    # list에 값이 없을 때를 대비
    notFound = False

    # 필터링 했는데 값이 없을 경우 대비
    if lane_dict is None:
        continue

    # 필터링된 lane 정보로 이미지 시각화
    for k in lane_dict.items():
        idx = k[0]  # idx가 0=횡단보도, 1=lane2
        xy_coords = k[1][1]

        # 어떤 객체인지 출력 (debug)
        # print("idx:", idx)

        my_list = []
        for xy_coord in xy_coords:  # 각 좌표마다
            x, y = xy_coord
            my_list.append((x, y))

        # 리스트 정렬 (y 내림차순)
        my_list.sort(key=lambda x: x[1], reverse=True)

        # idx 0이면 횡단보도이므로, crosswalk 탐색할지 여부 확인
        if idx == 0 and crosswalk_stack <= 3:
            _, min_y = min(my_list, key=lambda pair: pair[1])
            _, max_y = max(my_list, key=lambda pair: pair[1])

            if max_y - min_y > 100:  # max와 min의 차이를 통해 멈출지 여부 결정
                crosswalk_stack += 1

            if crosswalk_stack == 3: # 5번 스택이 쌓이면 진짜로 멈춰야 함
                comm.write(int(5).to_bytes(1, "little"))
                ack = "0"

                while ack != "OK":
                    ack = comm.readline().decode().strip()

                sleep(2)

                comm.write(int(11).to_bytes(1, "little")) # 아두이노에게 보낸 11이 3초간 멈추라는 의미
                crosswalk_stack += 1  # 앞으론 if문 안들어오게

                print("crosswalk ########")

                # 전송 끝남 - received 비활성화
                received = False

                # ack 초기화 해야 OK 올때까지 기다리니까
                ack = "0"

                notFound = True # 다시 처음으로 돌아가기 위함
                break

        # 상위 5개 원소만 가져오기
        top_list = my_list[:5]
        top_values = [point[0] for point in top_list]

        # 최하단 중앙
        cdx, cdy = (max(top_values) + min(top_values)) / 2.0, 470

        # y가 280~300 사이인 점들만 필터링
        filtered_my_list = [(x, y) for x, y in my_list if 280 <= y <= 300]

        # 필터링된 값이 없으면
        if not filtered_my_list:
            # print("not filtered")
            notFound=True
            break

        # 리스트 정렬 (x 내림차순)
        filtered_my_list.sort(reverse=True)

        # 모든 필터링된 점 표시 (debug)
        # for fx,fy in filtered_my_list:
        #     cv2.circle(frame, (int(fx), int(fy)), 5, (0, 0, 255), -1)

        # 중앙의 가장 오른쪽 좌표
        rcx, rcy = filtered_my_list[0]

        # 오른쪽 차선이 안 보일 때 대비: rcx 수정
        if first_rcx_flag:
            first_rcx_flag=False
        else:
            if abs(bef_rcx-rcx)>200:
                rcx=530
        bef_rcx=rcx

        # rcx, rcy 기본값 표시
        cv2.circle(frame, (int(rcx), int(rcy)), 20, (0, 0, 255), -1)

        base_x = rcx - 150 # 기본 시프트 정도
        delta_x = rcx - 470 # 기준점과의 차이
        weight_x = 0.1 # 델타의 가중치

        # rcx 재계산
        rcx = base_x + weight_x * delta_x

        # rcx, rcy 보정값 표시
        cv2.circle(frame, (int(rcx), int(rcy)), 20, (0, 0, 255), -1)

        # 두 점(cd, rc) 잇는 선 표시
        cv2.line(frame, (int(cdx), int(cdy)), (int(rcx), int(rcy)), (0, 255, 0), thickness=2)

        # 중앙 기준선 표시
        cv2.line(frame, (320, 0), (320, 480), (0, 0, 0), thickness=2)

        # 각도 계산 전처리 (degree): 왼쪽이 +, 오른쪽이 -
        points_dx = cdx - rcx
        points_dy = cdy - rcy

        # 0으로 나누면 안됨
        if points_dy==0:
            notFound=True
            break

        # arctan로 각도 계산
        points_angle = round(math.degrees(math.atan(points_dx / points_dy)), 2)

        # 오프셋 계산: 왼쪽이 -, 오른쪽이 +
        middle_offset = cdx - (320 - points_angle * 1.2)

        # 각도와 오프셋을 바탕으로 steering_angle 결정
        k_1 = 0.5
        k_2 = 0.25
        k_3 = 0.8

        # offset이 음수 : 차가 오른쪽으로 치우침 : steeing_angle이 커져야 한다
        steering_angle = k_3 * (k_1 * points_angle - k_2 * middle_offset)

        # default 값?
        serial_command = 0

        # steering angle에 따라 명령 결정
        if steering_angle >= 21:
            serial_command = 1
        elif steering_angle >= 15:
            serial_command = 2
        elif steering_angle >= 9:
            serial_command = 3
        elif steering_angle >= 3:
            serial_command = 4
        elif steering_angle >= -3:
            serial_command = 5
        elif steering_angle >= -9:
            serial_command = 6
        elif steering_angle >= -15:
            serial_command = 7
        elif steering_angle >= -21:
            serial_command = 8
        else:
            serial_command = 9

        # 아두이노에 데이터 전송
        # print("send1")
        comm.write(int(serial_command).to_bytes(1, "little"))
        # print("send2",serial_command)

        # ack가 OK일때까지 기다려야하므로
        ack="0"

        # 전송 끝남 - received 비활성화
        received = False

        # serial_command 표시
        cv2.putText(frame, "CMD: " + str(serial_command), (480, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 0), 1, cv2.LINE_AA)

        # 혹시라도 for문 안에 2개 있을까봐
        break

    # 이중 for문 탈출용
    if notFound:
        continue

    # 검출 결과 영상에 시각화
    annotated_frame = results[0].plot()

    # 화면에 출력
    cv2.imshow("YOLOv8 Segmentation", annotated_frame)

    # 'q' 키를 누르면 종료 (+ 아두이노에게 12 = 정지 명령 내리기)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        comm.write(int(12).to_bytes(1, "little"))
        break

    # print("complete")

# 종료 및 자원 정리
cap.release()
cv2.destroyAllWindows()