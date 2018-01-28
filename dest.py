#-*-coding:utf-8 -*-
import time
import serial
import sys, getopt
from math import degrees, radians, atan, atan2, sin, cos, pi, asin, sqrt

sys.path.append('.')
import RTIMU
import os.path
from Adafruit_PWM_Servo_Driver import PWM


#initialize setting


#initialize variable
speed = 0
current_speed = 0
angle = 2
current_angle = 0
state = 0
anglePWM = 320

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
		pwm.setPWM(1, 0, speed*20+280)
		# pwm.setPWM(1, 0, speed*33+268)
		print('##############################################Speed Change')
		print('speed : %d') %(speed)

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


def init_imu():
	global imu, poll_interval, SETTINGS_FILE, s
	SETTINGS_FILE = "RTIMULib"

	print("Using settings file " + SETTINGS_FILE + ".ini")
	if not os.path.exists(SETTINGS_FILE + ".ini"):
		print("Settings file does not exist, will be created")

	s = RTIMU.Settings(SETTINGS_FILE)
	imu = RTIMU.RTIMU(s)

	print("IMU Name: " + imu.IMUName())

	if (not imu.IMUInit()):
		print("IMU Init Failed")
		sys.exit(1)
	else:
		print("IMU Init Succeeded")

	# this is a good time to set any fusion parameters
	imu.setSlerpPower(0.02)
	imu.setGyroEnable(True)
	imu.setAccelEnable(True)
	imu.setCompassEnable(True)

	poll_interval = imu.IMUGetPollInterval()
	print("Recommended Poll Interval: %dmS\n" % poll_interval)

def getYaw(): #gps return lati,long
	global serYaw
	serYaw.flushInput()
	while True:
		data = serYaw.readline()
		if data.startswith('#YPR=') == True:
			yprRaw = data
			ypr = yprRaw.split(',')
			YAW = ypr[0]
			PITCH = float(ypr[1])
			ROLL = float(ypr[2])
			YAW = float(YAW[5:])
			if YAW < 0 :
				YAW = YAW + 360
			print 'YAW: %f' % YAW
			print 'PITCH: %f' %PITCH
			print 'ROLL: %f' % ROLL
			return radians(YAW)


def GotoDest(dest_lati, dest_long):
	global state, speed, angle
	start_time = time.time() 
	if state ==0:
		print ("state 0")
		(Clati, Clong) = locate() #gps func -> radians
		# time.sleep(1)
		# Clati = 37.583120
		# Clong = 127.027510

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

		if dist <= 3 :#between current pos - dest pos <= 5m
			state = 1
		
		else :
			Gdegree = XYtoDegree(Dlati,Dlong) #goal Degree 
			#print "Gdegree :%f" %(Gdegree)
			
			TurnHead(Gdegree)	
			print ("out Turn head")
			#go straight during 0.1sec
			AngleWrite(2)
			SpeedWrite(1)
		
	elif state ==1:
		print ("state 1")
		# Gdegree = 0 #just look north direction
		# TurnHead(Gdegree)
		AngleWrite(2)
		SpeedWrite(0)
		state =2
	print("---GotoDest : %s seconds ---" %(time.time() - start_time))
	
		
def UtmToDistance(Dlati, Dlong, dest_lati, Clati): 
	start_time_UtmToDistance = time.time() 
	#get distance between current pos and dest pos 
	R = 6371000.0
	a = sin(Dlati/2)**2 + cos(dest_lati)*cos(Clati)*sin(Dlong/2)**2
	c = 2*atan2(sqrt(a), sqrt(1-a))
	distance = R*c

	print ("distance: %f") %(distance)
	print("---start_time_UtmToDistance : %s seconds ---" %(time.time() - start_time_UtmToDistance))
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
	erroranagle = 20 #later need to set  
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
	print ("heading :%f, Ddegree:%f") %(heading, Ddegree)
	#until heading equal goal degree

	if (anglepos - angleneg >= 0) == True :
		while degrees(heading) < angleneg or degrees(heading) >= anglepos :
			#set direction
			if (Ddegree <0 and abs(Ddegree)< 180) or (Ddegree >= 0 and abs(Ddegree)>= 180) :
				angle = 1 #turn left
			elif (Ddegree >=0 and abs(Ddegree)< 180) or (Ddegree < 0 and abs(Ddegree) >= 180) :
				angle = 3 #turn right
			AngleWrite(angle)
			SpeedWrite(1)
			heading = getYaw()

			(anglepos, angleneg) =AdjustAngle(Gdegree)			#question
			Ddegree = Gdegree - degrees(heading)
			print ("heading %f, Ddegree %f") %(heading,Ddegree)
			print ("Gdegree %f  angleneg %f  anglepos %f") %(Gdegree,angleneg, anglepos)
			print ("angle %d") %angle
	else :
		while not(degrees(heading) > angleneg or degrees(heading) <= anglepos) :
			#set direction
			if (Ddegree <0 and abs(Ddegree)< 180) or (Ddegree >= 0 and abs(Ddegree)>= 180) :
				angle = 1 #turn left
			elif (Ddegree >=0 and abs(Ddegree)< 180) or (Ddegree < 0 and abs(Ddegree) >= 180) :
				angle = 3 #turn right
			AngleWrite(angle)
			SpeedWrite(1)
			heading = getYaw()

			(anglepos, angleneg) =AdjustAngle(Gdegree)			#question
			Ddegree = Gdegree - degrees(heading)
			print ("heading %f, Ddegree %f") %(heading,Ddegree)
			print ("Gdegree %f  angleneg %f  anglepos %f") %(Gdegree,angleneg, anglepos)
			print ("angle %d") %angle

def init_control() :
	for i in range(1) :
		AngleWrite(1)
		SpeedWrite(1)
		time.sleep(1)
		AngleWrite(2)
		SpeedWrite(0)
		time.sleep(1)
		AngleWrite(3)
		time.sleep(1)
	SpeedWrite(0)
	AngleWrite(2)


init_control()

# while state!=2 :
# 	getYaw()

# for i in range(190,10000,5):
# 	pulse = i# + 33100
# 	pwm.setPWM(0, 0, pulse)
# 	print(pulse)
# 	time.sleep(1)

# for speed in range(10) :
# 	SpeedWrite(speed)
# 	print(speed)
# 	time.sleep(2)

# while (True):
#   # Change speed of continuous servo on channel O
# 	AngleWrite(1)
# 	SpeedWrite(1)
# 	time.sleep(2)
# 	print(1)
# 	AngleWrite(2)
# 	time.sleep(2)
# 	print(2)
# 	AngleWrite(3)
# 	time.sleep(2)
# 	SpeedWrite(0)
# 	print(3)

while state!=2:
	GotoDest(37.583243, 127.027523) #가고자하는 위치 입력
if state ==2:
	SpeedWrite(0)
	AngleWrite(2)
# 창의관 : 37.583057, 127.026141
# 하스/헬스장쪽 : 37.584676, 127.025642
# 하스/과도입구쪽 : 37.584997, 127.026266
# 부산 : 35.174325, 129.002584
# 제2공 : 37.583243, 127.027523
# 남문 : 37.583160, 127.027510