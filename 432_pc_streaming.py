import socket
import struct
import numpy as np
import cv2
import pickle
import time

HOST_RPI = '192.168.137.129'  # Raspberry Pi IP 주소
PORT = 8089

client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_cam.connect((HOST_RPI, PORT))

t_now = time.time()
t_prev = time.time()
cnt_frame = 0

try:
    while True:
        # 명령 전송 (12: 센서 읽기 및 영상 요청)
        cmd = 12
        cmd_byte = struct.pack('!B', cmd)
        client_cam.sendall(cmd_byte)

        # 센서 데이터 수신
        rl_byte = client_cam.recv(1)
        if len(rl_byte) < 1:
            print("Failed to receive sensor data.")
            break
        rl = struct.unpack('!B', rl_byte)
        right, left = (rl[0] & 2) >> 1, rl[0] & 1
        print(f"Sensor Data - Right: {right}, Left: {left}")

        # 영상 데이터 길이 수신
        data_len_bytes = client_cam.recv(4)
        if len(data_len_bytes) < 4:
            print("Failed to receive data length.")
            break
        data_len = struct.unpack('!L', data_len_bytes)[0]

        # 영상 데이터 수신
        frame_data = b""
        while len(frame_data) < data_len:
            packet = client_cam.recv(data_len - len(frame_data))
            if not packet:
                print("Failed to receive full frame data.")
                break
            frame_data += packet

        # 영상 데이터 디코딩
        try:
            frame = pickle.loads(frame_data)
            np_data = np.frombuffer(frame, dtype=np.uint8)
            frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
            if frame is None:
                print("Failed to decode frame.")
                continue
        except Exception as e:
            print(f"Error decoding frame: {e}")
            continue

        # 영상 출력
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame2 = cv2.resize(frame, (320, 240))
        cv2.imshow('frame', frame2)

        # ESC 키 입력 시 종료
        key = cv2.waitKey(1)
        if key == 27:
            break

        # FPS 계산
        cnt_frame += 1
        t_now = time.time()
        if t_now - t_prev >= 1.0:
            t_prev = t_now
            print(f"Frame Count: {cnt_frame}")
            cnt_frame = 0

except KeyboardInterrupt:
    print("Interrupted by user.")
finally:
    client_cam.close()
    cv2.destroyAllWindows()
