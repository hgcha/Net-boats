#-*-coding:utf-8 -*-

import wiringpi2 as wiringpi
import FaBo9Axis_MPU9250
import time
import serial
import sys
from math import degrees, radians, atan, atan2, sin, cos, pi, asin, sqrt

#initialize setting
wiringpi.wiringPiSetup() #initialize wiringPi
wiringpi.pinMode(23, 2) # alternative function = PWM
wiringpi.pinMode(26, 2) # alternative function = PWM
wiringpi.pwmSetMode(0) 
wiringpi.pwmSetRange(12000)
wiringpi.pwmWrite(23, 700)
wiringpi.pwmWrite(26, 900)
mpu9250 = FaBo9Axis_MPU9250.MPU9250() #mpu9250 initialize
ser = serial.Serial('/dev/ttyAMA0', 9600) #gps serial port

#initialize variable
speed = 0
angle = 2
state = 0

def SpeedWrite(speed): #desire speed
	if speed > 10:
		print 'speed cannot be greater than 10.'
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
		print "1: left, 2: center, 3: right"

	# 900 = center
	# 500 = right
	# 1200 = left

# def locate(): #gps return lati,long
# 	while True:
#     	data = ser.readline()
#     	if data.startswith('$GPGGA') == True:
#         	gpgga = data
#         	location = gpgga.split(',')
#         	GGAprotocolHeader_s = location[0]
#         	UTCTime_s = location[1]
#         	Latitude_s = location[2]
#         	NS_s = location[3] # North or South
#         	Longitude_s = location[4]
#         	EW_s = location[5] # East or West
        
#         	# print 'Header: %s' % GGAprotocolHeader_s
#         	# print 'Time: %s' % UTCTime_s
#         	# print 'Laitutude: %s' % Latitude_s
#         	# print 'NS : %s' % NS_s
#         	# print 'Longitude: %s' % Longitude_s
#         	# print 'EW : %s' % EW_s
#         	# print
#         	break

# 	processed_Lati = float(Latitude_s[:2]) + float(Latitude_s[2:])/60.0 # calculated Latitude, Longitude
# 	processed_Long = float(Longitude_s[:3]) + float(Longitude_s[3:])/60.0
# 	print "lati : %s, long :%s " %(poscessed_Lati,processed_Long)
# 	return (processed_Lati, processed_Long)


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
		print("x = %d %d \n y = %d %d\n") % (max_x, min_x, max_y, min_y)
		print("process : %d/%d") % (i , count_amount) 
		i = i + 1
		time.sleep(0.1)

	offset_x = (max_x + min_x)/2	#offset value 측정
	offset_y = (max_y + min_y)/2

	print("Initializing Success.\n")
	return offset_x, offset_y

def getYaw() :
	global offset_x, offset_y
	[accel, gyro, mag] = readAll()
	x = mag['x'] - offset_x
	y = mag['y'] - offset_y

	#theta = asin(accel['x'] / sqrt(accel['y']*accel['y'] + accel['z']*accel['z']))
	#low = asin(accel['y'] / sqrt(accel['x']*accel['x'] + accel['z']*accel['z']))
	theta = asin(accel['x'])
	low = asin(accel['y'])

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

	if(real_yaw<0) :
		real_yaw = 360 + real_yaw
	print "getYaw %d" %real_yaw
	return radians(real_yaw)

def GotoDest(dest_lati, dest_long):
	global state
	global speed
	global angle
	speed =0
	SpeedWrite(speed)
  
	if state ==0:
		print "state 0"
		#(Clati, Clong) = locate() #gps func
		Clati = 37.583057 
		Clong = 127.026141
		Dlati = radians(dest_lati) - radians(Clati)  #diffrence current latitude and destination latitude
		Dlong = radians(dest_long) - radians(Clong)  #diffrence current longitude and destination longitude
		print "CLati :%f, CLong:%f" %(Clati, Clong)
		print "Dlati :%f, Dlong :%f" %(Dlati, Dlong)

		dist = UtmToDistance(Dlati, Dlong, dest_lati, Clati)
		print "dist %f" %dist

		if dist <=5 :#between current pos - dest pos <= 5m
			state =1

		else :
			Gdegree = XYtoDegree(Dlati,Dlong) #goal Degree 
			print "Gdegree :%f" %(Gdegree)
			TurnHead(Gdegree)	

			#go straight during 10sec	
			AngleWrite(2)
			SpeedWrite(1)
			time.sleep(1) #would be change(according to distance)

					
	elif state ==1:
		print "state 1"
		Gdegree = 0 #just look north direction
		TurnHead(Gdegree)
		state =2
		
def UtmToDistance(Dlati, Dlong, dest_lati, Clati): 
	#get distance between current pos and dest pos 
	R = 6373000.0
	a = sin(Dlati/2)**2 + cos(dest_lati)*cos(Clati)*sin(Dlong/2)**2
	c = 2*atan2(sqrt(a), sqrt(1-a))
	distance = R*c
	print "Result: %f" %(distance)
	return distance

def XYtoDegree(Dlati, Dlong) :
	if Dlati>0:
		if Dlong >=0:
			return atan(Dlong/Dlati)
		else :
			return atan(Dlong/Dlati) +2*pi
	elif Dlati<0:
		return atan(Dlong/Dlati) + pi
	else :
		if Dlong >=0:
			return pi/2
		else :
			return 3*pi/2

	
def TurnHead(Gdegree):
	#set heading 
	heading = getYaw()#mpu9250(yaw) : between 0 to 360 => radians
	Ddegree = degrees(Gdegree)-degrees(heading) #diffrence heading and goal Degree
	error = 0.02

	print "heading :%f, Ddegree:%f" %(heading, Ddegree)

	if (Ddegree <0 and abs(Ddegree)>= 180) or (Ddegree >= 0 and abs(Ddegree)< 180) :
		angle = 1 #turn left
	elif (Ddegree >=0 and abs(Ddegree)>= 180) or (Ddegree < 0 and abs(Ddegree)< 180) :
		angle = 3 #turn right
	
	print "angle change  %d" %angle
	#set direction
	#until heading equal goal degree
	while heading <= Gdegree-Gdegree*error and heading >= Gdegree+Gdegree*error:
	 	AngleWrite(angle)
		SpeedWrite(1)
		heading = getYaw()
		Ddegree = degrees(Gdegree)-degrees(heading)
		print "heading %f, Ddegree %f" %(heading,Ddegree)
		print "angle %d" %angle


###최초에 init_imu() 를 이용해 initialize 한 뒤, getYaw()함수를 사용해야 함.

[offset_x, offset_y] = init_imu()

while True:
	GotoDest(35.174325, 129.002584)

# 창의관 : 37.583057, 127.026141
# 하나스퀘어 : 37.584676, 127.025642
# 부산 : 35.174325, 129.002584