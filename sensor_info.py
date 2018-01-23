#-*-coding:utf-8 -*-
import wiringpi2 as wiringpi
import FaBo9Axis_MPU9250
import time
import serial
from math import atan, sin, cos, pi, asin, sqrt

#initialize variable
yaw_offset = 0
offset_x = 0
offset_y = 0
offset_z = 0

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
		print ('speed cannot be greater than 10.')
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
		print ("1: left, 2: center, 3: right")

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
			if len(Latitude_s[:2]) == 0 :		# if GPS signal is founded, exit the function. else, repeat GPS finding sequence 
				print('GPS signal is not found\n')
			else :
				print('GPS signal is found\n')
				break
	# calculated Latitude, Longitude
	processed_Lati = float(Latitude_s[:2]) + float(Latitude_s[2:])/60.0 # calculated Latitude, Longitude
	processed_Long = float(Longitude_s[:3]) + float(Longitude_s[3:])/60.0
	print ("lati : %s, long :%s ") %(processed_Lati,processed_Long)
	return (processed_Lati, processed_Long)

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
	global offset_x, offset_y, offset_z, yaw_offset
	# count_amount = 100
	# max_x = 0
	# min_x = 1000
	# max_y = 0
	# min_y = 1000
	# i = 0
		
	# while i < count_amount :
	# 	[accel, gyro, mag] = readAll()
	# 	if mag['x'] > max_x :
	# 		max_x = mag['x']
	# 	elif mag['x'] < min_x :
	# 		min_x = mag['x']
	# 	if mag['y'] > max_y :
	# 		max_y = mag['y']
	# 	elif mag['y'] < min_y :
	# 		min_y = mag['y']
	# 	print("x = %d %d \n y = %d %d\n") % (max_x, min_x, max_y, min_y)
	# 	print("process : %d/%d") % (i , count_amount) 
	# 	i = i + 1
	# 	time.sleep(0.1)

	# offset_x = (max_x + min_x)/2	#offset value calculate
	# offset_y = (max_y + min_y)/2

	offset_x = 5.483	# previously calculated offset value 
	offset_y = 15.173
	offset_z = -18.9185

	yaw_offset = degrees(getYaw()) #sequence of init Yaw
	print('yaw_offset : %d') %(yaw_offset)
	print("Initializing Complete.")

def getYaw() :
	global offset_x, offset_y, offset_z, yaw_offset
	time.sleep(0.3)
	[accel, gyro, mag] = readAll()
	x = mag['x'] - offset_x
	y = mag['y'] - offset_y
	z = mag['z'] - offset_z

	norm = sqrt(accel['x']*accel['x'] + accel['y']*accel['y'] + accel['z']*accel['z'])
	accel['x'] /= norm
	accel['y'] /= norm
	accel['z'] /= norm

	pitch = asin(-accel['x'])
	roll = asin(accel['y']/cos(pitch))

	print('pitch = %f , roll = %f') %(pitch,roll)
	
	x = x*cos(pitch) + z*sin(pitch)
	y = x*sin(roll)*sin(pitch) + y*cos(roll) - z*sin(roll)*cos(pitch)
	z = -x*cos(roll)*sin(pitch) + y*sin(roll) + z*cos(roll)*cos(pitch)

	print('x = %f , y = %f , z = %f') %(x,y,z)

	yaw = atan2(y,x) * 180 / pi

	print('raw_yaw : %f') %yaw

	# if(x > 0 and y >= 0) :
	# 	real_yaw = yaw
	# elif(x < 0) :
	# 	real_yaw = yaw + 180
	# elif(x > 0 and y < 0) :
	# 	real_yaw = yaw + 360

	if y <0 :
		real_yaw = yaw + 360
	else :
		real_yaw = yaw

	print('fix by mag yaw : %f') %real_yaw

	real_yaw = real_yaw - yaw_offset

	if real_yaw < 0 :
		real_yaw += 360

	print ("getYaw %d") %real_yaw
	return radians(real_yaw)
