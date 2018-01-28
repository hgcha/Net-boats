#-*-coding:utf-8 -*-
from sensor_info import * 
from destserver import dest_lati, dest_long
import time
from math import degrees, radians, atan, atan2, sin, cos, pi, asin, sqrt

#initialize variable
speed = 0
angle = 2
state = 0

def GotoDest(dest_lati, dest_long):	
	global state,speed,angle
  
	if state ==0:
		print("state 0")
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
		# print ("rCLati :%f, rCLong:%f" %(rClati, rClong))
		# print ("Dlati :%f, Dlong :%f" %(Dlati, Dlong))

		dist = UtmToDistance(Dlati, Dlong, rdest_lati, rClati)

		if dist <= 3:#between current pos - dest pos <= 5m
			state =1

		else:
			Gdegree = XYtoDegree(Dlati,Dlong) #goal Degree 
			#print ("Gdegree :%f" %(Gdegree))
			TurnHead(Gdegree)	
			print("out Turn head")
			sys.stdout.flush()
			#go straight during 10sec	
			AngleWrite(2)
			SpeedWrite(1)
			# time.sleep(1) #would be change(according to distance)
			
	elif state ==1:
		print("state 1")
		print("arrived dest")
		sys.stdout.flush()
		AngleWrite(2)
		SpeedWrite(0)
		state =2
		
def UtmToDistance(Dlati, Dlong, dest_lati, Clati): 
	#get distance between current pos and dest pos 
	R = 6371000.0
	a = sin(Dlati/2)**2 + cos(dest_lati)*cos(Clati)*sin(Dlong/2)**2
	c = 2*atan2(sqrt(a), sqrt(1-a))
	distance = R*c

	print("distance: %f" % distance)
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
	print("heading: %f, Ddegree: %f" % (heading, Ddegree))

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

			Gdegree = XYtoDegree(Dlati,Dlong)
			(anglepos, angleneg) =AdjustAngle(Gdegree)
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

			Gdegree = XYtoDegree(Dlati,Dlong)
			(anglepos, angleneg) =AdjustAngle(Gdegree)
			Ddegree = Gdegree - degrees(heading)
			print ("heading %f, Ddegree %f") %(heading,Ddegree)
			print ("Gdegree %f  angleneg %f  anglepos %f") %(Gdegree,angleneg, anglepos)
			print ("angle %d") %angle

def untilDest(dest_lati, dest_long) :	
	while state!=2:
		GotoDest(dest_lati, dest_long) #가고자하는 위치 입력
	if state ==2:
		SpeedWrite(0)
		AngleWrite(2)
		return state	

slati =float(sys.stdin.readline())
slong =float(sys.stdin.readline())
print(slati, slong)
untilDest(slati,slong)	