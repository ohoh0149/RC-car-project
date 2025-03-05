import time
import Function_Library_2 as LiDAR

port = '/dev/cu.SLAB_USBtoUART'
env=LiDAR.libLIDAR('/dev/cu.SLAB_USBtoUART')


env.init()
env.getState()


# 아두이노 세팅
arduino_port = '/dev/cu.usbmodem1201'
ser = LiDAR.libARDUINO()
comm = ser.init(arduino_port, 9600)

max_range=2000
count=0
flag=0


# LiDAR 객체 재생성을 위한 함수
def reset_lidar(env, port):
    try:
        env.stop()  # LiDAR를 중단
        env.lidar.disconnect()  # LiDAR 연결을 끊음
    except Exception as e:
        print(f"Error during stop or disconnect: {e}")

    time.sleep(0.5)  # 약간의 대기 시간 추가
    return LiDAR.libLIDAR(port)  # LiDAR 객체를 재생성


comm.write(int(13).to_bytes(1, "little"))

ack="No"
# ack가 'OK'일 때까지 반복 대기(필요하다면)
while ack != "OK":
    ack = comm.readline().decode().strip()



env=reset_lidar(env,port)
while True:
    print("flag",flag)

    if flag==1:
        break
    for scan in env.scanning():

        right_count=len(env.getAngleDistanceRange(scan, 88,92,150,max_range))
        print(right_count)
        if right_count>=3:
            flag=1
            break



env = reset_lidar(env, port)  # LiDAR 객체 재생성
while True:
    print("flag",flag)
    if flag==2:
        break

    for scan in env.scanning():
        right_count = len(env.getAngleDistanceRange(scan, 88, 92, 150, max_range))
        print(right_count)

        if right_count==0:
            flag=2
            # 1 전송 후 아두이노 한테 제어권
            comm.write(int(1).to_bytes(1, "little"))

            break

ack="No"
# ack가 'OK'일 때까지 반복 대기(필요하다면)
while ack != "OK":
    ack = comm.readline().decode().strip()




env = reset_lidar(env, port)  # LiDAR 객체 재생성
#각도 확인
for scan in env.scanning():

    pos_list = env.getAngleDistanceRange(scan, 135, 225,3000,20000)
    # [[각도,거리],[각도,거리],[각도,거리],[각도,거리],  ]
    print(pos_list)
    pos_list.sort()
    a1=pos_list[0][0]
    a2=pos_list[-1][0]
    val=(a2+a1)//2
    comm.write(int(val).to_bytes(1, "little"))
    break

    print(val)

ack="No"
# ack가 'OK'일 때까지 반복 대기(필요하다면)
while ack != "OK":
    ack = comm.readline().decode().strip()







env = reset_lidar(env, port)  # LiDAR 객체 재생성

while True:
    print("flag",flag)

    if flag == 3:
        break
    for scan in env.scanning():
        right_count = len(env.getAngleDistanceRange(scan, 88, 92, 150, max_range))
        print(right_count)

        if right_count >=3 :
            flag = 3

            break




env = reset_lidar(env, port)  # LiDAR 객체 재생성
while True:
    print("flag",flag)
    if flag == 4:
        break
    for scan in env.scanning():
        right_count = len(env.getAngleDistanceRange(scan, 88, 92, 150, max_range))
        print(right_count)

        if right_count == 0:
            flag = 4
            # 2 전송 후 아두이노 한테 제어권
            comm.write(int(2).to_bytes(1, "little"))
            print("send")

            break