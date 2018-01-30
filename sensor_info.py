#-*-coding:utf-8 -*-
import time
import serial
import sys, getopt
from math import atan, sin, cos, pi, asin, sqrt, radians

sys.path.append('.')
import os.path
from Adafruit_PWM_Servo_Driver import PWM

#initialize variable
current_speed = 0
current_angle = 0
anglePWM = 320

#initialize setting
pwm = PWM(0x40)
pwm.setPWMFreq(46)                        # Set frequency to 60 Hz

ser = serial.Serial('/dev/ttyACM0', 9600) #gps serial port
ser.close()
ser.open()
serYaw = serial.Serial('/dev/ttyAMA0', 57600, timeout=1)
serYaw.close()
serYaw.open()


def SpeedWrite(speed): #desire speed
	global current_speed
	if current_speed != speed :
		current_speed = speed
		pwm.setPWM(1, 0, speed*20+284)
		# pwm.setPWM(1, 0, speed*33+268)
		print('##############################################Speed Change')
		print('speed : %d' %(speed))

def AngleWrite(angle): #control angle
	global current_angle, anglePWM
	if angle == 2 :
		anglePWM = 320
	elif angle == 3 :
		anglePWM = 190
	elif angle == 1 :
		anglePWM = 450
	if current_angle != angle :
		current_angle = angle
		pwm.setPWM(0, 0, anglePWM)
		# pwm.setPWM(0, 0, 32850 + angle*150)
		print('##############################################Angle Change')

def locate(): #gps return lati,long
	# return (37.583243, 127.027523)
	ser.flushInput()
	while True:
		data = ser.readline()
		if data.startswith('$GNGLL') == True:
			gpgga = data
			location = gpgga.split(',')
			GGAprotocolHeader_s = location[0]
			Latitude_s = location[1]
			NS_s = location[2] # North or South
			Longitude_s = location[3]
			EW_s = location[4] # East or West
			# print 'Header: %s' % GGAprotocolHeader_s
			# print 'Time: %s' % UTCTime_s
			# print 'Laitutude: %s' % Latitude_s
			# print 'NS : %s' % NS_s
			# print 'Longitude: %s' % Longitude_s
			# print 'EW : %s' % EW_s
			if len(Latitude_s[:2]) == 0 :		# if GPS signal is founded, exit the function. else, repeat GPS finding sequence 
				print('GPS signal is not found\n')
			else :
				print('GPS signal is found\n')
				break
	# calculated Latitude, Longitude
	processed_Lati = float(Latitude_s[:2]) + float(Latitude_s[2:])/60.0 # calculated Latitude, Longitude
	processed_Long = float(Longitude_s[:3]) + float(Longitude_s[3:])/60.0
	print ("lati : %s, long :%s " %(processed_Lati,processed_Long))
	return (processed_Lati, processed_Long)

def getYaw(): #gps return lati,long
	global serYaw
	serYaw.flushInput()
	while True:
		data = serYaw.readline()
		if data.startswith(b'#YPR=') == True:
			yprRaw = data
			ypr = yprRaw.split(b',')
			YAW = ypr[0]
			PITCH = float(ypr[1])
			ROLL = float(ypr[2])
			YAW = float(YAW[5:])
			if YAW < 0 :
				YAW = YAW + 360
			print ('YAW: %f' % YAW)
			print ('PITCH: %f' %PITCH)
			print ('ROLL: %f' % ROLL)
			return radians(YAW)