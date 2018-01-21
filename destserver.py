#-*-coding:utf-8 -*-
from sensor_info import * 
from socketIO_client import SocketIO, LoggingNamespace
import json
from math import degrees, radians, atan, atan2, sin, cos, pi, asin, sqrt

#initialize variable
speed = 0
angle = 2
state = 0

baseGps = {"lat": None, "lng": None}

boatinfo = {"id": int(sys.argv[1]),
            "gps": {"lat" = None, "lng" = None}
            "targetGPS": {"lat" = None, "lng" = None}
            "speed": None,
            "heading": None,
            "isMoving": False,
            "isStopped": False}

def GotoDest(dest_lati, dest_long):	
	global boatinfo 
	global state
	global speed
	global angle
	speed = 0
	SpeedWrite(speed)
  
	if state ==0:
		print("state 0")
		Clati, Clong = locate() #gps func -> radians
		boatinfo["gps"]["lat"] = Clati
		boatinfo["gps"]["lng"] = Clong
		# Clati = 37.583176
		# Clong = 127.026015

		#change degree to radians
		rdest_lati = radians(dest_lati)
		rdest_long = radians(dest_long)
		rClati = radians(Clati)
		rClong = radians(Clong)

		Dlati = rdest_lati - rClati #diffrence current latitude and destination latitude
		Dlong = rdest_long - rClong #diffrence current longitude and destination longitude
		# print "rCLati :%f, rCLong:%f" %(rClati, rClong)
		# print "Dlati :%f, Dlong :%f" %(Dlati, Dlong)

		dist = UtmToDistance(Dlati, Dlong, rdest_lati, rClati)

		if dist <= 5:#between current pos - dest pos <= 5m
			state = 1

		else:
			Gdegree = XYtoDegree(Dlati,Dlong) #goal Degree 
			#print "Gdegree :%f" %(Gdegree)
			TurnHead(Gdegree)	
			print("out Turn head")
			#go straight during 10sec	
			AngleWrite(2)
			SpeedWrite(1)
			time.sleep(1) #would be change(according to distance)
			
	elif state ==1:
		print("state 1")
		Gdegree = 0 #just look north direction
		TurnHead(Gdegree)
		state =2
		
def UtmToDistance(Dlati, Dlong, dest_lati, Clati): 
	#get distance between current pos and dest pos 
	R = 6371000.0
	a = sin(Dlati/2)**2 + cos(dest_lati)*cos(Clati)*sin(Dlong/2)**2
	c = 2*atan2(sqrt(a), sqrt(1-a))
	distance = R*c

	print("distance: %f" % distance)
	return distance

def XYtoDegree(Dlati, Dlong): #
	if Dlati > 0:
		if Dlong >= 0:
			return degrees(atan(Dlong/Dlati))
		else :
			return degrees(atan(Dlong/Dlati) + 2*pi)
	elif Dlati<0:
		return degrees(atan(Dlong/Dlati) + pi)
	else :
		if Dlong >=0:
			return degrees(pi/2)
		else :
			return degrees(3*pi/2)

def AdjustAngle (Gdegree) :
	erroranagle = 10 #later need to set  
	angleneg = Gdegree - erroranagle
	anglepos = Gdegree + erroranagle
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
		
		print("heading %f, Ddegree %f" % (heading, Ddegree))
		print("Gdegree %f, angleneg %f, anglepos %f" % (Gdegree, angleneg, anglepos))
		print("angle %d" % angle)

def DoingBoat(err, data) :
	global boatinfo
	if err == None and boatinfo["id"] == data["id"]:
		boatinfo["targetGps"] = data["targetGps"]
		boat.emit("boat-received", boatinfo)
		dest_lati = boatinfo["targetGps"]["lat"]  
		dest_long = boatinfo["targetGps"]["lnt"]

		if boat["isStopped"] == False:
			boatinfo["isMoving"] = True
			print("I am going to move to lat: %s and lnt: %s!" % (dest_lati, dest_long))
	else:
		print("Error occured while DoingBoat.")

def StartAgain(err, data):
	global boatinfo
	if err == None and boatinfo["id"] == data["id"] and boatinfo[isStopped] == True:
		boatinfo["targetGps"] = data["targetGps"]
		boatinfo["isStopped"] = False
		boatinfo["isMoving"] = True
		boat.emit("boat-received", boatinfo, Check)
		DoingBoat(err, data)
	else:
		print("Error occured while StartAgain.")
		print(err)

		# halin cha
		
# 창의관 : 37.583057, 127.026141
# 하나스퀘어 : 37.584676, 127.025642
# 부산 : 35.174325, 129.002584

def Stop(err, data):
	global boatinfo
	if err == None and boatinfo["id"] == data["id"]:
		boatinfo["speed"] = 0
		boatinfo["isMoving"] = False
		boatinfo["isStopped"] = True
		boat.emit("boat-received", boatinfo)
		SpeedWrite(0)
	else:
		print("Error occured while Stop")
		print(err)

def on_connect():
	print("connect")

def on_disconnect():
	print('disconnect')

def on_reconnect():
	print('reconnect')

def CheckPing(err, data):
	global PingSent
	if data == None:
		print("Server didn't respond to boat-ping.")
	else:
		if err != None:
			print(err)
			print("Error occured while boat-ping.")
		else:
			print("Server successfully responded to boat-ping.")
			last_ping = time.time()
			PingSent = True

def CheckSensor(err, data):
	global SensorSent
	if data == None:
		print("Server didn't respond to boat-sensor.")
	else:
		if err != None:
			print(err)
			print("Error occured while boat-sensor.")
		else:
			print("Server successfully responded to boat-sensor.")
			last_sensor = time.time()
			SensorSent = True

def SetBase(err, data):
	global baseGps_lat
	global baseGps_lng
	baseGps_lat = data["data"]["lat"]
	baseGps_lng = data["data"]["lng"]

def GoToBase(err, data):
	global boatinfo
	if err == None:
		boatinfo["targetGps"] = {"lat" : data["lat"], "lng" : data["lng"]}
		boat.emit("boat-received", boatinfo)
		dest_lati = boatinfo["targetGps"]["lat"]  
		dest_long = boatinfo["targetGps"]["lnt"]

		if boat["isStopped"] == False:
			boatinfo["isMoving"] = True
			print("I am going to move to lat: %s and lnt: %s!" % (dest_lati, dest_long))
	else:
		print("Error occured while GoToBase.")

def GoToBase_init(lat, lng):
	global boatinfo
	boatinfo["targetGps"] = baseGps
	dest_lati = boatinfo["targetGps"]["lat"]  
	dest_long = boatinfo["targetGps"]["lnt"]
	boatinfo["isMoving"] = True
	print("I am going to move to lat: %s and lnt: %s!" % (dest_lati, dest_long))

###최초에 init_imu() 를 이용해 initialize 한 뒤, getYaw()함수를 사용해야 함.
[offset_x, offset_y] = init_imu()
print("waiting for connection...")
boat = SocketIO('192.168.1.121', 8080, LoggingNamespace)
boat.on('connect', on_connect)
boat.on('disconnect', on_disconnect)
boat.on('reconnect', on_reconnect)

boat.on('boat-base', GoToBase)
boat.on('boat-move', DoingBoat)
boat.on('boat-resume', StartAgain)
boat.on('boat-stop', Stop)

boat-emit("boat-base", boatinfo, SetBase)
boat.emit('boat-ping', boatinfo, CheckPing)
boat.emit('boat-sensor', boatinfo, CheckSensor)
while True:
	if time.time() > last_ping + 5 and CheckPing == True:
		CheckPing = False
		boat.emit('boat-ping', boatinfo, CheckPing)

	if time.time() > last_sensor + 10 and CheckSensor == True:
		CheckSensor = False
		boat.emit('boat-sensor', boatinfo, CheckSensor)