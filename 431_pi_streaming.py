import socket
import struct
import pickle
import RPi.GPIO as GPIO
from threading import Thread
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
import io
GPIO.setmode(GPIO.BCM)

DOs = [26, 27]

for DO in DOs:
    GPIO.setup(DO, GPIO.IN)

HOST = ''
PORT = 8089

# 소켓 서버 초기화
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

server.bind((HOST, PORT))
print('Socket bind complete')

server.listen(10)
print('Socket now listening')

server_cam, addr = server.accept()
print('New Client connected.')

# Picamera2 초기화
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (160, 120)}))

output = None
frame_buffer = None

def start_camera_stream():
    """Picamera2를 사용하여 프레임을 캡처하고 MJPEG 데이터로 저장."""
    global frame_buffer
    encoder = JpegEncoder()
    picam2.start_recording(encoder, FileOutput(frame_buffer))

def capture_frame():
    """프레임 데이터를 전역 버퍼에서 반환."""
    global frame_buffer
    if frame_buffer is not None:
        return frame_buffer.getvalue()
    return None

# MJPEG 스트림을 별도 쓰레드로 실행
frame_buffer = io.BytesIO()
Thread(target=start_camera_stream, daemon=True).start()

try:
    while True:
        cmd_byte = server_cam.recv(1)
        cmd = struct.unpack('!B', cmd_byte)

        if cmd[0] == 12:
            # 센서 데이터 캡처
            right = GPIO.input(DOs[0])
            left = GPIO.input(DOs[1])
            print(f"Sensor Data - Right: {right}, Left: {left}")

            # 프레임 데이터 캡처
            frame = capture_frame()
            if frame is None:
                print("Frame not available yet.")
                continue

            # 센서 데이터 준비
            rl = right << 1 | left << 0
            rl_byte = struct.pack("!B", rl)

            # 프레임 직렬화
            data = pickle.dumps(frame)

            # 센서 + 프레임 데이터 전송
            data_size = struct.pack("!L", len(data))
            server_cam.sendall(rl_byte + data_size + data)

except KeyboardInterrupt:
    print("Server interrupted. Cleaning up.")
finally:
    picam2.stop_recording()
    server_cam.close()
    server.close()
    GPIO.cleanup()
