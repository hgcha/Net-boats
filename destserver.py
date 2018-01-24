#-*-coding:utf-8 -*-
from sensor_info import *
from socketIO_client import SocketIO, LoggingNamespace 
import json
import sys
import subprocess

#initialize variable
boatProcess = None
dest_lati =0.0
dest_long =0.0
PingSent = False
SensorSent = False
baseGps = {"lat": None, "lng": None}
boatinfo = {"id": int(sys.argv[1]),
            "gps": {"lat" : None, "lng" : None},
            "targetGps": {"lat" : None, "lng" : None},
            "speed": None,
            "heading": None,
            "isMoving": False,
            "isStopped": False}

def DoingBoat(err, data):
	global boatinfo
	global boatProcess
	global dest_lati
	global dest_long

	if err == None and boatinfo["id"] == data["id"]:
		boatinfo["targetGps"] = data["targetGps"]
		boat.emit("boat-received", boatinfo)

		if boatinfo["isStopped"] == False:
			dest_lati = boatinfo["targetGps"]["lat"]  
			dest_long = boatinfo["targetGps"]["lng"]
			boatinfo["isMoving"] = True
			print("I am going to move to lat: %s and lng: %s!" % (dest_lati, dest_long))

			cmd = ["python","gotodest.py"]
			boatProcess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
			boatProcess.stdin.write("%s\n" %str(dest_lati))
			boatProcess.stdin.write(str(dest_long))
			boatProcess.stdin.close()
			print(boatProcess)
			print("doing boat")
	else:
		print("Error occured while DoingBoat.")

def StartAgain(err, data):
	global boatinfo
	global dest_lati
	global dest_long
	
	if err == None and boatinfo["id"] == data["id"] and boatinfo["isStopped"] == True:
		boatinfo["targetGps"] = data["targetGps"]
		boatinfo["isStopped"] = False
		boatinfo["isMoving"] = True
		dest_lati = boatinfo["targetGps"]["lat"]  
		dest_long = boatinfo["targetGps"]["lng"]
		boat.emit("boat-received", boatinfo)
		print("I am moving again to lat: %s and lng %s!" % (dest_lati, dest_long))

		"""boat process"""
		cmd = ["python","gotodest.py"]
		boatProcess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
		boatProcess.stdin.write("%s\n" %str(dest_lati))
		boatProcess.stdin.write(str(dest_long))
		boatProcess.stdin.close()
		print(boatProcess)
		print("start again")

	else:
		print("Error occured while StartAgain.")
		print(err)


def Stop(err, data):
	global boatinfo
	if err == None and boatinfo["id"] == data["id"]:
		boatinfo["speed"] = 0
		boatinfo["isMoving"] = False
		boatinfo["isStopped"] = True
		boat.emit("boat-received", boatinfo)
		
		SpeedWrite(0)
		"""boat process"""
		boatProcess.kill()
		print("kill boat process")
		print("I stopped!")
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
	global LastPing
	global PingSent
	if data == None:
		print("Server didn't respond to boat-ping.")
	else:
		if err != None:
			print(err)
			# GoToBase_init()
			print("Error occured while boat-ping.")
		else:
			print("Server successfully responded to boat-ping.")
			LastPing = time.time()
			PingSent = True

def CheckSensor(err, data):
	global LastSensor
	global SensorSent
	if data == None:
		print("Server didn't respond to boat-sensor.")
	else:
		if err != None:
			print(err)
			print("Error occured while boat-sensor.")
		else:
			print("Server successfully responded to boat-sensor.")
			LastSensor = time.time()
			SensorSent = True

def SetBase(err, data):
	global baseGps
	baseGps["lat"] = data["data"]["lat"]
	baseGps["lng"] = data["data"]["lng"]
	print("Base is setted to lat: %s and lng: %s." % (baseGps["lat"], baseGps["lng"]))

def GoToBase(lat, lng):
	global dest_lati
	global dest_long

	boatinfo["targetGps"] = baseGps
	dest_lati = boatinfo["targetGps"]["lat"]  
	dest_long = boatinfo["targetGps"]["lng"]
	boatinfo["isMoving"] = True
	print("I am going to move to lat: %s and lng: %s!" % (dest_lati, dest_long))

	"""boat process"""
	cmd = ["python","gotodest.py"]
	boatProcess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
	boatProcess.stdin.write("%s\n" %str(dest_lati))
	boatProcess.stdin.write(str(dest_long))
	boatProcess.stdin.close()
	print(boatProcess)
	print("I'll goto base")


###최초에 init_imu() 를 이용해 initialize 한 뒤, getYaw()함수를 사용해야 함.
init_imu()

print("waiting for connection...")
boat = SocketIO('192.168.1.121', 8080, LoggingNamespace)
boat.on('connect', on_connect)
boat.on('disconnect', on_disconnect)
boat.on('reconnect', on_reconnect)

boat.on('boat-base', SetBase)
boat.on('boat-move', DoingBoat)
boat.on('boat-resume', StartAgain)
boat.on('boat-stop', Stop)

boat.emit("boat-base", boatinfo, SetBase)
boat.emit('boat-ping', boatinfo, CheckPing)
boatinfo["gps"]["lat"], boatinfo["gps"]["lng"] = locate()
print("I am at lat: %s, lat %s" % (boatinfo["gps"]["lat"], boatinfo["gps"]["lng"]))
# boat.emit('boat-sensor', boatinfo, CheckSensor)
LastPing = time.time()
BaseFlag = False

while True:
	global boatProcess
	global dest_lati
	global dest_long
	
	"""boat process"""
	output = boatProcess.stdout.readline()
	if boatProcess.poll() is not None:
		print("boat arrived dest")
		boat.emit('boat-arrived',boatinfo)
	else :
		print("boat state", output.strip())	

	if time.time() > LastPing + 1 and PingSent == True:
		print(boatinfo)
		PingSent = False
		boat.emit('boat-ping', boatinfo, CheckPing)

	boat.wait(seconds=0.1)
	
	if time.time() > LastPing + 60 and BaseFlag == False:
		print("moving to base [lat: %s, lng: %s]" % (baseGps["lat"], baseGps["lng"]))
		dest_lati =baseGps["lat"]
		dest_long =baseGps["lng"]
		
		"""boat process"""
		boatProcess.kill()
		cmd = ['python','gotodest.py']
		boatProcess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
		boatProcess.stdin.write("%s\n" %str(dest_lati))
		boatProcess.stdin.write(str(dest_long))
		boatProcess.stdin.close()
		print(boatProcess)
		print("goto base")

		BaseFlag = True 

	# if time.time() > LastSensor + 10 and SensorSent == True:
	# 	CheckSensor = False
	# 	boat.emit('boat-sensor', boatinfo, CheckSensor)