#-*-coding:utf-8 -*-
from sensor_info import * 
import time
import sys
import json

# from math import degrees, radians, atan, atan2, sin, cos, pi, asin, sqrt


#initialize variable
angle = 2
state = 0
Dlati = 0
Dlong = 0

def GotoDest(dest_lati, dest_long):	
	global state, speed, angle
	global Dlati, Dlong
	if state == 0:
		SpeedWrite(1, speed)
		# print("state 0")
		try:
			Clati, Clong = locate() #gps func -> radians
		except Exception as ex: 
			print("error1", ex)	
		# Clati = 37.583176
		# Clong = 127.026015
		# print("Clati",Clati)
		# print("Clong",Clong)
		#change degree to radians
		rdest_lati = radians(dest_lati)
		rdest_long = radians(dest_long)
		rClati = radians(Clati)
		rClong = radians(Clong)

		Dlati = rdest_lati - rClati #diffrence current latitude and destination latitude
		Dlong = rdest_long - rClong  #diffrence current longitude and destination longitude
		# print ("rCLati :%f, rCLong:%f" %(rClati, rClong))
		# print ("Dlati :%f, Dlong :%f" %(Dlati, Dlong))
		dist = UtmToDistance(Dlati, Dlong, rdest_lati, rClati)
		print('distance: %f' %dist)

		if dist <= 3:#between current pos - dest pos <= 3m
			state = 1
			# print("===============================================================================================================")

		else:
			Gdegree = XYtoDegree(Dlati,Dlong) #goal Degree 
			#print ("Gdegree :%f" %(Gdegree))
			TurnHead(Gdegree)	
			# print("out Turn head")
			#go straight during 10sec	
			AngleWrite(2)
			SpeedWrite(1, speed)
			# time.sleep(1) #would be change(according to distance)
			
	elif state == 1:
		# print("state 1")
		print("arrived dest")
		AngleWrite(2)
		SpeedWrite(0, speed)
		state = 2

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

def AdjustAngle (Gdegree):
	global speed
	erroranagle = 10 #later need to set  
	angleneg = Gdegree-erroranagle
	anglepos = Gdegree+erroranagle
	if angleneg < 0 :
		angleneg = 360 + angleneg
	if anglepos >= 360:
		anglepos = anglepos - 360

	return (anglepos, angleneg)	

def TurnHead(Gdegree):
	global speed
	#set heading 
	global Dlati, Dlong
	try:
		heading = getYaw()
	except Exception as ex: # 에러 종류
		print("error2", ex)
	# print("heading1: %f" %degrees(heading))
	Ddegree = Gdegree - degrees(heading) #diffrence heading and goal Degree
	(anglepos, angleneg) =AdjustAngle(Gdegree)
	nowtime = time.time()
	print("time : %f" % nowtime)
	# print("heading: %f, Ddegree: %f" % (heading, Ddegree))

	#until heading equal goal degree
	if (anglepos - angleneg >= 0) == True :
		while degrees(heading) < angleneg or degrees(heading) >= anglepos :
			#set direction
			if (Ddegree <0 and abs(Ddegree)< 180) or (Ddegree >= 0 and abs(Ddegree)>= 180) :
				angle = 1 #turn left
			elif (Ddegree >=0 and abs(Ddegree)< 180) or (Ddegree < 0 and abs(Ddegree) >= 180) :
				angle = 3 #turn right
			AngleWrite(angle)
			SpeedWrite(1, speed)
			try:
				heading = getYaw()
			except Exception as ex: # 에러 종류
				print("error3", ex)
			# print("heading2: %f" %degrees(heading))
			Gdegree = XYtoDegree(Dlati,Dlong)
			(anglepos, angleneg) =AdjustAngle(Gdegree)
			Ddegree = Gdegree - degrees(heading)
			# print ("heading %f, Ddegree %f" %(heading,Ddegree))
			# print ("Gdegree %f  angleneg %f  anglepos %f" %(Gdegree,angleneg, anglepos))
			# print ("angle %d" %angle)
			nowtime = time.time()
			print("time : %f" % nowtime)
	else :
		while not(degrees(heading) > angleneg or degrees(heading) <= anglepos) :
			#set direction
			if (Ddegree <0 and abs(Ddegree)< 180) or (Ddegree >= 0 and abs(Ddegree)>= 180) :
				angle = 1 #turn left
			elif (Ddegree >=0 and abs(Ddegree)< 180) or (Ddegree < 0 and abs(Ddegree) >= 180) :
				angle = 3 #turn right
			AngleWrite(angle)
			SpeedWrite(1, speed)
			try:
				heading = getYaw()
			except Exception as ex: # 에러 종류
				print("error4", ex)
			# print("heading3: %f" %degrees(heading))
			Gdegree = XYtoDegree(Dlati,Dlong)
			(anglepos, angleneg) =AdjustAngle(Gdegree)
			Ddegree = Gdegree - degrees(heading)
			# print ("heading %f, Ddegree %f" %(heading,Ddegree))
			# print ("Gdegree %f  angleneg %f  anglepos %f") %(Gdegree,angleneg, anglepos)
			# print ("angle %d" %angle)
			nowtime = time.time()
			print("time : %f" % nowtime)

def untilDest(dest_lati, dest_long) :
	global speed	
	while state!=2:
		# print("until dest")
		GotoDest(dest_lati, dest_long) #가고자하는 위치 입력
	if state == 2:
		# print("state 2")
		SpeedWrite(0, speed)
		AngleWrite(2)
		return 0

json_data = open("config.json").read()
data = json.loads(json_data)
speed = data["PWM"]

slati = float(sys.stdin.readline())
slong = float(sys.stdin.readline())
sys.stdout.flush()
untilDest(slati,slong)