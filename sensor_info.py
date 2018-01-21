#-*-coding:utf-8 -*-
import wiringpi2 as wiringpi
import FaBo9Axis_MPU9250
import time
import serial
import sys
from math import atan, sin, cos, pi, asin, sqrt

#initialize setting
wiringpi.wiringPiSetup() #initialize wiringPi
wiringpi.pinMode(23, 2) # alternative function = PWM
wiringpi.pinMode(26, 2) # alternative function = PWM
wiringpi.pwmSetMode(0) 
wiringpi.pwmSetRange(12000)
wiringpi.pwmWrite(23, 700)
wiringpi.pwmWrite(26, 900)
mpu9250 = FaBo9Axis_MPU9250.MPU9250() #mpu9250 initialize
ser = serial.Serial('/dev/ttyACM0', 9600) #gps serial port

def SpeedWrite(speed): #desire speed
	if speed > 10:
		print("speed cannot be greater than 10.")
	elif speed > 0:
		wiringpi.pwmWrite(23, 880+(speed-1)*10)
	elif speed == 0:
		wiringpi.pwmWrite(23, 700)

def AngleWrite(angle): #control angle
	if angle == 1: #left
		wiringpi.pwmWrite(26, 1200)
	elif angle == 2: #center
		wiringpi.pwmWrite(26, 900)
	elif angle == 3: #right
		wiringpi.pwmWrite(26, 500)
	else:
		print("1: left, 2: center, 3: right")

	# 900 = center
	# 500 = right
	# 1200 = left

def locate(): #gps return lati,long
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
			break
	# calculated Latitude, Longitude
	processed_Lati = float(Latitude_s[:2]) + float(Latitude_s[2:])/60.0 # calculated Latitude, Longitude
	processed_Long = float(Longitude_s[:3]) + float(Longitude_s[3:])/60.0
	# print "lati : %s, long :%s " %(processed_Lati,processed_Long)
	return processed_Lati, processed_Long

def readAll():
	accel = mpu9250.readAccel()
	# print " ax = " , ( accel['x'] )
	# print " ay = " , ( accel['y'] )
	# print " az = " , ( accel['z'] )

	gyro = mpu9250.readGyro()
	# print " gx = " , ( gyro['x'] )
	# print " gy = " , ( gyro['y'] )
	# print " gz = " , ( gyro['z'] )

	mag = mpu9250.readMagnet()
	# print " mx = " , ( mag['x'] )
	# print " my = " , ( mag['y'] )
	# print " mz = " , ( mag['z'] )
		
	return accel, gyro, mag

def init_imu():
	count_amount = 100
	max_x = 0
	min_x = 1000
	max_y = 0
	min_y = 1000
	i = 0
		
	while i < count_amount :
		[accel, gyro, mag] = readAll()
		if mag['x'] > max_x :
			max_x = mag['x']
		elif mag['x'] < min_x :
			min_x = mag['x']
		if mag['y'] > max_y :
			max_y = mag['y']
		elif mag['y'] < min_y :
			min_y = mag['y']
		print("x = %d %d \n y = %d %d\n" % (max_x, min_x, max_y, min_y))
		print("process : %d/%d" % (i , count_amount)) 
		i = i + 1
		time.sleep(0.1)

	offset_x = (max_x + min_x)/2	#offset value 측정
	offset_y = (max_y + min_y)/2

	print("Initializing Success.\n")
	return offset_x, offset_y

def getYaw() :
	global offset_x, offset_y
	time.sleep(0.3)
	[accel, gyro, mag] = readAll()
	x = mag['x'] - offset_x
	y = mag['y'] - offset_y

	if accel['x'] > 1 :
		accel['x'] = 1
	elif accel['x'] < -1 :
		accel['x'] = -1
	if accel['y'] > 1 :
		accel['y'] = 1
	elif accel['y'] < -1 :
		accel['y'] = -1
	
	theta = asin(accel['x'])
	low = asin(accel['y'])

	#theta = asin(accel['x'] / sqrt(accel['y']*accel['y'] + accel['z']*accel['z']))
	#low = asin(accel['y'] / sqrt(accel['x']*accel['x'] + accel['z']*accel['z']))

	x = x*cos(theta) + y*sin(low) * sin(theta) - mag['z'] * cos(low) * sin(theta)
	y = y * cos(low) + mag['z'] * sin(theta)

	yaw = atan(y / x) * 180 / pi
			
	if(mag['x'] >= 0 and mag['y'] > 0) :
		real_yaw = yaw
	elif(mag['x'] < 0 and mag['y'] >= 0) :
		real_yaw = yaw + 180
	elif(mag['x'] <= 0 and mag['y'] < 0) :
		real_yaw = yaw + 180
	elif(mag['x'] >= 0 and mag['y'] <= 0) :
		real_yaw = 360 + yaw

	if real_yaw < 0:
		real_yaw = 360 + real_yaw

	print("getYaw %d" % real_yaw)
	return radians(real_yaw)