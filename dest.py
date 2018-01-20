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
ser = serial.Serial('/dev/ttyACM0', 9600) #gps serial port

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
	print "lati : %s, long :%s " %(processed_Lati,processed_Long)
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

	# offset_x = (max_x + min_x)/2	#offset value 측정
	# offset_y = (max_y + min_y)/2

	print("Initializing Success.\n")

	offset_x = 6	#offset value 측정
	offset_y = 50

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
		(Clati, Clong) = locate() #gps func -> radians
		# Clati = 37.583176
		# Clong = 127.026015

		#change degree to radians
		rdest_lati = radians(dest_lati)
		rdest_long = radians(dest_long)
		rClati = radians(Clati)
		rClong = radians(Clong)

		Dlati = rdest_lati - rClati #diffrence current latitude and destination latitude
		Dlong = rdest_long - rClong  #diffrence current longitude and destination longitude
		# print "rCLati :%f, rCLong:%f" %(rClati, rClong)
		# print "Dlati :%f, Dlong :%f" %(Dlati, Dlong)

		dist = UtmToDistance(Dlati, Dlong, rdest_lati, rClati)

		if dist <=5 :#between current pos - dest pos <= 5m
			state = 1

		else :
			Gdegree = XYtoDegree(Dlati,Dlong) #goal Degree 
			#print "Gdegree :%f" %(Gdegree)
			TurnHead(Gdegree)	
			print "out Turn head"
			#go straight during 10sec	
			AngleWrite(2)
			SpeedWrite(1)
			time.sleep(1) #would be change(according to distance)
			
	elif state ==1:
		print "state 1"
		# Gdegree = 0 #just look north direction
		# TurnHead(Gdegree)
		AngleWrite(2)
		SpeedWrite(0)
		state =2
		
def UtmToDistance(Dlati, Dlong, dest_lati, Clati): 
	#get distance between current pos and dest pos 
	R = 6371000.0
	a = sin(Dlati/2)**2 + cos(dest_lati)*cos(Clati)*sin(Dlong/2)**2
	c = 2*atan2(sqrt(a), sqrt(1-a))
	distance = R*c

	print "distance: %f" %(distance)
	return distance

def XYtoDegree(Dlati, Dlong) : #
	if Dlati>0:
		if Dlong >=0:
			return degrees(atan(Dlong/Dlati))
		else :
			return degrees(atan(Dlong/Dlati) +2*pi)
	elif Dlati<0:
		return degrees(atan(Dlong/Dlati) + pi)
	else :
		if Dlong >=0:
			return degrees(pi/2)
		else :
			return degrees(3*pi/2)
def AdjustAngle (Gdegree) :
	erroranagle = 10 #later need to set  
	angleneg = Gdegree-erroranagle
	anglepos = Gdegree+erroranagle
	if angleneg < 0 :
		angleneg = 360 + angleneg
	if anglepos >= 360:
		anglepos = anglepos - 360

	return (anglepos, angleneg)	

def TurnHead(Gdegree):
	#set heading 
	heading = getYaw()
	Ddegree = Gdegree - degrees(heading) #diffrence heading and goal Degree
	(anglepos, angleneg) =AdjustAngle(Gdegree)
	
	print "heading :%f, Ddegree:%f" %(heading, Ddegree)
	#until heading equal goal degree
	while degrees(heading) < angleneg or degrees(heading) >= anglepos :
		#set direction
		if (Ddegree <0 and abs(Ddegree)< 180) or (Ddegree >= 0 and abs(Ddegree)>= 180) :
			angle = 1 #turn left
		elif (Ddegree >=0 and abs(Ddegree)< 180) or (Ddegree < 0 and abs(Ddegree) >= 180) :
			angle = 3 #turn right

	 	AngleWrite(angle)
		SpeedWrite(1)
		heading = getYaw()
		Ddegree = Gdegree -degrees(heading)
		
		print "heading %f, Ddegree %f" %(heading,Ddegree)
		print "Gdegree %f  angleneg %f  anglepos %f" %(Gdegree,angleneg, anglepos)
		print "angle %d" %angle

###최초에 init_imu() 를 이용해 initialize 한 뒤, getYaw()함수를 사용해야 함.

[offset_x, offset_y] = init_imu()

# while state!=2 :
# 	getYaw()

while state!=2:
	GotoDest(37.584997, 127.026266) #가고자하는 위치 입력
if state ==2:
	SpeedWrite(0)
	AngleWrite(2)
# 창의관 : 37.583057, 127.026141
# 하스/헬스장쪽 : 37.584676, 127.025642
# 하스/과도입구쪽 : 37.584997, 127.026266
# 부산 : 35.174325, 129.002584
# 제2공 : 37.583145, 127.027652
