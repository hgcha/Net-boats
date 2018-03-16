#-*-coding:utf-8 -*-
import time
import serial
import sys
from math import degrees, radians, atan, atan2, sin, cos, pi, asin, sqrt

sys.path.append('.')
import os.path
from Adafruit_PWM_Servo_Driver import PWM

#initialize variable
anglePWM = 320

#initialize setting
pwm = PWM(0x40)
pwm.setPWMFreq(46)                        # Set frequency to 60 Hz

def SpeedWrite(speed, config_speed): #desire speed
	pwm.setPWM(1, 0, speed*30+config_speed)
	# pwm.setPWM(1, 0, speed*33+268)
	print('##############################################Speed Change')
	print('speed : %d' %(speed))

def AngleWrite(angle): #control angleS
	if angle == 2 :
		anglePWM = 320
	elif angle == 3 :
		anglePWM = 190
	elif angle == 1 :
		anglePWM = 450
	pwm.setPWM(0, 0, anglePWM)
		# pwm.setPWM(0, 0, 32850 + angle*150)
	print('##############################################Angle Change')

def locate() :
	gps = open("gpsValue.txt",'r')
	gpsvalue = gps.read()
	gpsparsed = gpsvalue.split()
	processed_Lati = float(gpsparsed[0])
	processed_Long = float(gpsparsed[1])
	gps.close()
	return processed_Lati, processed_Long

def getYaw():
	while True:
		yaw=open("yawValue.txt",'r')
		yawvalue = yaw.read()

		if(yawvalue==None or yawvalue==" " or yawvalue==""):
			yaw.close()
			time.sleep(0.1)
		else:
			YAW = float(yawvalue)
			yaw.close()
			return radians(YAW)	

def UtmToDistance(Dlati, Dlong, dest_lati, Clati): 
	#get distance between current pos and dest pos 
	R = 6371000.0
	a = sin(Dlati/2)**2 + cos(dest_lati)*cos(Clati)*sin(Dlong/2)**2
	c = 2*atan2(sqrt(a), sqrt(1-a))
	distance = R*c

	# print("distance: %f" % distance)
	return distance