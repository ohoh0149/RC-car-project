import socket
import struct
import cv2
import pickle
import RPi.GPIO as GPIO
import threading
from motor_control import *

GPIO.setmode(GPIO.BCM)	

initMotor()
	
speedFwd = 30 # speed for 0~90
speedCurve = 60 # speed for 0~90

DOs = [26,27]

for DO in DOs:
	GPIO.setup(DO, GPIO.IN)

VIDSRC = 'v4l2src device=/dev/video0 ! video/x-raw,width=160,height=120,framerate=20/1 ! videoscale ! videoconvert ! jpegenc ! appsink'

cap=cv2.VideoCapture(VIDSRC, cv2.CAP_GSTREAMER)

HOST = ''
PORT = 8089

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

server.bind((HOST, PORT))
print('Socket bind complete')

server.listen(10)
print('Socket now listening')

server_cam, addr = server.accept()
server_mot, addr = server.accept()
print('New Client.')

flag_exit = False
def mot_main() :

	while True:
		
		rl_byte = server_mot.recv(1)
		rl = struct.unpack('!B', rl_byte)
	
		right, left = (rl[0] & 2)>>1, rl[0] & 1
		# print(right, left)
		if not right and not left :
			goForward(speedFwd)
		elif not right and left :
			turnRight(speedCurve)
		elif right and not left :
			turnLeft(speedCurve)

		if flag_exit: break

motThread = threading.Thread(target=mot_main)
motThread.start()

try:

	while True:	

		cmd_byte = server_cam.recv(1)
		cmd = struct.unpack('!B', cmd_byte)
		# print(cmd[0])
		if cmd[0]==12 :		

			# capture sensor data
			right = GPIO.input(DOs[0])
			left  = GPIO.input(DOs[1])
			# print(right, left)
		
			# capture camera data
			ret,frame=cap.read()

			# prepare sensor data 		
			rl = right<<1|left<<0
			rl_byte = struct.pack("!B", rl)
			
			# Serialize frame
			data = pickle.dumps(frame)
		
			# send sensor + camera data
			data_size = struct.pack("!L", len(data)) 
			server_cam.sendall(rl_byte + data_size + data)
			
except KeyboardInterrupt:
	pass
except ConnectionResetError:
	pass
except BrokenPipeError:
	pass
except:
	pass

flag_exit = True
motThread.join()
	
server_cam.close()
server_mot.close()
server.close()

exitMotor()
GPIO.cleanup()