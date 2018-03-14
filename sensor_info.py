#-*-coding:utf-8 -*-
import time
import serial
import sys, getopt
from math import degrees, radians, atan, atan2, sin, cos, pi, asin, sqrt

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

# ser = serial.Serial('/dev/ttyACM0', 9600) #gps serial port
# ser.close()
# ser.open()

# serYaw = serial.Serial('/dev/ttyAMA0', 57600)
# serYaw.close()
# serYaw.open()

def SpeedWrite(speed): #desire speed
	pwm.setPWM(1, 0, speed*30+285)
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

# def gpsMutexLock() :
# 	gpsMutex = open("gpsMutex.txt", 'r')
# 	while True :
# 		if gpsMutex.readline() == "0" :
# 			gpsMutex.close()
# 			break
# 		time.sleep(0.01)
# 	gpsMutex = open("gpsMutex.txt", 'w')
# 	gpsMutex.write("1")
# 	gpsMutex.close()

# def gpsMutexUnLock() :
# 	gpsMutex = open("gpsMutex.txt", 'w')
# 	gpsMutex.write("0")
# 	gpsMutex.close()

# def yawMutexLock() :
# 	yawMutex = open("yawMutex.txt", 'r')
# 	while True :
# 		if yawMutex.readline() == "0" :
# 			yawMutex.close()
# 			break
# 		time.sleep(0.01)
# 	yawMutex = open("yawMutex.txt", 'w')
# 	yawMutex.write("1")
# 	yawMutex.close()

# def yawMutexUnLock() :
# 	yawMutex = open("yawMutex.txt", 'w')
# 	yawMutex.write("0")
# 	yawMutex.close()

# def locate(): #gps return lati,long
# 	# return (37.582454, 127.026945)		#신공학관 우측
# 	# return (37.583243, 127.027523)		#또랑 앞
# 	gpsMutexLock()
# 	if ser.isOpen() == False :
# 		ser.open()
# 	ser.flush()
# 	while True:
# 		data = ser.readline()
# 		if data.startswith('$GNGLL') == True:
# 			gpgga = data
# 			location = gpgga.split(',')
# 			GGAprotocolHeader_s = location[0]
# 			Latitude_s = location[1]
# 			NS_s = location[2] # North or South
# 			Longitude_s = location[3]
# 			EW_s = location[4] # East or West
# 			# print 'Header: %s' % GGAprotocolHeader_s
# 			# print 'Time: %s' % UTCTime_s
# 			# print 'Laitutude: %s' % Latitude_s
# 			# print 'NS : %s' % NS_s
# 			# print 'Longitude: %s' % Longitude_s
# 			# print 'EW : %s' % EW_s
# 			if len(Latitude_s[:2]) == 0 :		# if GPS signal is founded, exit the function. else, repeat GPS finding sequence 
# 				print('GPS signal is not found\n')
# 			else :
# 				print('GPS signal is found\n')
# 				break
# 	# calculated Latitude, Longitude
# 	processed_Lati = float(Latitude_s[:2]) + float(Latitude_s[2:])/60.0 # calculated Latitude, Longitude
# 	processed_Long = float(Longitude_s[:3]) + float(Longitude_s[3:])/60.0
# 	# print ("lati : %s, long :%s " %(processed_Lati,processed_Long))
# 	ser.close()
# 	gpsMutexUnLock()
# 	return (processed_Lati, processed_Long)

def locate() :
	# return 36.1234, 123.1234
	while True :
		gps = open("gpsValue.txt",'r')
		gpsvalue = gps.read()
		gpsparsed = gpsvalue.split(' ')
		# print("======")
		# print (gpsparsed[0])
		# print("======")
		# print (gpsparsed[1])
		# print(gpsparsed[0])
		
		if gpsparsed[0].startswith('37') == True :
			processed_Lati = float(gpsparsed[0])
			processed_Long = float(gpsparsed[1])
			gps.close()
			return processed_Lati, processed_Long
		else :
			print("GPS signal is not found.")
			gps.close()
		time.sleep(0.1)

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


# def getYaw(): #gps return lati,long
# 	global serYaw
# 	if serYaw.isOpen() == False :
# 		yawMutexLock()
# 		serYaw.open()
# 	serYaw.flush()
# 	while True:
# 		data = serYaw.readline()
# 		if data.startswith('#YPR=') == True:
# 			serYaw.close()
# 			yawMutexUnLock()
# 			print(data)
# 			yprRaw = data
# 			ypr = yprRaw.split(',')
# 			YAW = ypr[0]
# 			PITCH = float(ypr[1])
# 			ROLL = float(ypr[2])
# 			YAW = float(YAW[5:])
# 			if YAW < 0 :
# 				YAW = YAW + 360
# 			# print ('YAW: %f' % YAW)
# 			# print ('PITCH: %f' %PITCH)
# 			# print ('ROLL: %f' % ROLL)
# 			return radians(YAW)

def UtmToDistance(Dlati, Dlong, dest_lati, Clati): 
	#get distance between current pos and dest pos 
	R = 6371000.0
	a = sin(Dlati/2)**2 + cos(dest_lati)*cos(Clati)*sin(Dlong/2)**2
	c = 2*atan2(sqrt(a), sqrt(1-a))
	distance = R*c

	# print("distance: %f" % distance)
	return distance