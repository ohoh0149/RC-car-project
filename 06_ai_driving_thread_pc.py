import socket
import struct
import numpy as np
import cv2
import pickle
import time
from tensorflow.keras.models import load_model
import tensorflow as tf
import threading
import queue

HOST_RPI = '192.168.137.246'
PORT = 8089

client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_mot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_cam.connect((HOST_RPI, PORT))
client_mot.connect((HOST_RPI, PORT))

t_now = time.time()
t_prev = time.time()
cnt_frame = 0

model = load_model('model.h5')

names = ['forward', 'right', 'left', 'forward']

NUM_MESSAGES = 10
mq = [queue.Queue(NUM_MESSAGES), queue.Queue(NUM_MESSAGES)]

flag_exit = False
def cnn_main(args) :

	print(args)

	while True:

		frame = mq[args].get()

		image = frame
		image = image/255

		image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
		# print(image_tensor.shape)

		# Add dimension to match with input mode
		image_tensor = tf.expand_dims(image_tensor, 0)
		# print(image_tensor.shape)

		y_predict = model.predict(image_tensor)
		y_predict = np.argmax(y_predict,axis=1)
		# print(names[y_predict[0]], y_predict[0])

		# send y_predict
		cmd = y_predict[0].item()
		cmd = struct.pack('B', cmd)
		client_mot.sendall(cmd)

		if flag_exit: break

cnnThread_0 = threading.Thread(target=cnn_main, args=(0,))
cnnThread_0.start()
cnnThread_1 = threading.Thread(target=cnn_main, args=(1,))
cnnThread_1.start()

fn = 0

try:

	while True:

		# 센서 읽어, 영상 보내
		cmd = 12
		cmd_byte = struct.pack('!B', cmd)
		client_cam.sendall(cmd_byte)

		# 센서값 받기
		rl_byte = client_cam.recv(1)
		# rl = struct.unpack('!B', rl_byte)

		# right, left = (rl[0] & 2)>>1, rl[0] & 1
		# print(right, left)

		# 영상 받기
		data_len_bytes = client_cam.recv(4)
		data_len = struct.unpack('!L', data_len_bytes)

		frame_data = client_cam.recv(data_len[0], socket.MSG_WAITALL)

		# Extract frame
		frame = pickle.loads(frame_data)

		# 영상 출력
		np_data = np.frombuffer(frame, dtype='uint8')
		frame = cv2.imdecode(np_data,1)
		frame = cv2.rotate(frame, cv2.ROTATE_180)
		frame2 = cv2.resize(frame, (320, 240))
		cv2.imshow('frame', frame2)

		mq[fn%2].put(frame)
		fn += 1

		key = cv2.waitKey(1)
		if key == 27:
			break

		cnt_frame += 1
		t_now = time.time()
		if t_now - t_prev >= 1.0 :
			t_prev = t_now
			print("frame count : %f" %cnt_frame)
			cnt_frame = 0

except:
	pass

flag_exit = True
cnnThread_0.join()
cnnThread_1.join()

client_cam.close()
client_mot.close()