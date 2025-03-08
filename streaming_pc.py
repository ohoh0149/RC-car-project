import cv2
import requests
import numpy as np

# MJPEG 스트리밍 URL
url = 'http://192.168.137.129:8089/stream.mjpg'

# 스트리밍을 받기 위한 HTTP 요청
stream = requests.get(url, stream=True)

bytes_data = b''

for chunk in stream.iter_content(chunk_size=1024):
    bytes_data += chunk
    # JPEG 이미지의 시작과 끝을 찾기
    a = bytes_data.find(b'\xff\xd8')  # JPEG 시작
    b = bytes_data.find(b'\xff\xd9')  # JPEG 끝

    if a != -1 and b != -1:
        jpg = bytes_data[a:b+2]
        bytes_data = bytes_data[b+2:]
        # 이미지를 디코딩하여 프레임으로 변환
        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

        # 이미지를 윈도우에 표시
        cv2.imshow('MJPEG Stream', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
