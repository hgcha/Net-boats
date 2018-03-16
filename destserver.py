#-*-coding:utf-8 -*-
from sensor_info import *
from socketIO_client import SocketIO, LoggingNamespace 
import sys
import subprocess
import time
from math import degrees
import os
import glob
import json

#initialize variable
boatProcess = None
boatstate = 0
dest_lati = 0.0
dest_long = 0.0
PingSent = False
SensorSent = False

#thermometer setting 
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')
# base_dir = '/sys/bus/w1/devices/'
# device_folder = base_dir + '28-0316a360b7ff'
# device_file = device_folder + '/w1_slave'
# device_folder = glob.glob(base_dir + '28*')[0]

# def read_temp_raw():
#     f = open(device_file, 'r')
#     lines = f.readlines()
#     f.close()
#     return lines

# def read_temp(): 
#     lines = read_temp_raw()
#     while lines[0].strip()[-3:] != 'YES':
#         time.sleep(0.2)
#         lines = read_temp_raw()
        
#     equals_pos = lines[1].find('t=')
      
#     if equals_pos != -1:
#         temp_string = lines[1][equals_pos+2:]
#         temp_c = float(temp_string) / 1000.0
        # return temp_c

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
			print("doing boat")
			print("I am going to move to lat: %s and lng: %s!" % (dest_lati, dest_long))

			print(boatProcess)
			if boatProcess is not None:
				if boatProcess.poll() == None:
					boatProcess.terminate()
					boatProcess.kill()
				
				if boatProcess is not None:
					start = time.time()
					while boatProcess.poll() == None:
						if time.time() - start > 10:
							boatProcess.terminate()
							boatProcess.kill()
							start = time.time()

				boatProcess =None

			cmd = ["python","/home/pi/hg/gotodest.py"]
			boatProcess = subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
			boatProcess.stdin.write("%s\n" %str(dest_lati))
			boatProcess.stdin.write(str(dest_long))
			# boatProcess.stdin.write("%s\n" %str(30.4542))
			# boatProcess.stdin.write("%s\n" %str(170.4542))
			boatProcess.stdin.close()
			# print(boatProcess)
	else:
		print("Error occured while DoingBoat.")

def StartAgain(err, data):
	global boatinfo
	global boatProcess
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
		cmd = ["python","/home/pi/hg/gotodest.py"]
		boatProcess = subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
		boatProcess.stdin.write("%s\n" %str(dest_lati))
		boatProcess.stdin.write(str(dest_long))
		boatProcess.stdin.close()
		print("start again")
	else:
		print("Error occured while StartAgain.")
		print(err)


def Stop(err, data):
	global boatinfo
	global boatProcess
	if err == None and boatinfo["id"] == data["id"]:
		boatinfo["speed"] = 0
		boatinfo["isMoving"] = False
		boatinfo["isStopped"] = True
		boat.emit("boat-received", boatinfo)
		
		"""boat process"""
		if boatProcess is not None:
			print(boatProcess)
			if boatProcess.poll() == None:
				boatProcess.terminate()
				boatProcess.kill()
			print(type(boatProcess))
			if boatProcess is not None:
				start = time.time()
				while boatProcess.poll() == None:
					if time.time() - start > 10:
						boatProcess.terminate()
						boatProcess.kill()
						start = time.time()

			boatProcess =None

		print("I stopped!")
	else:
		print("Error occured while Stop")
		print(err)
	SpeedWrite(0, speed)	

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
	boat.emit("boat-received", boatinfo)
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
	cmd = ["python", "/home/pi/hg/gotodest.py"]
	boatProcess = subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
	boatProcess.stdin.write("%s\n" %str(dest_lati))
	boatProcess.stdin.write(str(dest_long))
	boatProcess.stdin.close()
	print(boatProcess)
	print("I'll goto base")

def init_control(speed) :
	for i in range(2) :
		AngleWrite(1)
		SpeedWrite(1, speed)
		time.sleep(1)
		AngleWrite(2)
		SpeedWrite(0, speed)
		time.sleep(1)
		SpeedWrite(1, speed)
		AngleWrite(3)
		time.sleep(1)
		SpeedWrite(0, speed)
		AngleWrite(2)
		time.sleep(1)
	SpeedWrite(0, speed)
	AngleWrite(2)

# for i in range(300,330,1) :
# 	pwm.setPWM(1, 0, i)
# 	time.sleep(1)
# 	print(i)

json_data = open("config.json").read()
data = json.loads(json_data)
speed = data["PWM"]

# 최초로 배 세팅
init_control(speed)

print("waiting for connection...")
boat = SocketIO('192.168.0.7', 8080, LoggingNamespace)
boat.on('connect', on_connect)
boat.on('disconnect', on_disconnect)
boat.on('reconnect', on_reconnect)

boat.on('boat-base', SetBase)
boat.on('boat-move', DoingBoat)
boat.on('boat-resume', StartAgain)
boat.on('boat-stop', Stop)

p = subprocess.Popen(["hostname", "-I"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
boatinfo = {"id": data["id"],
			"ip": p.communicate()[0].split(" ")[0],
            "gps": {"lat" : None, "lng" : None},
            "targetGps": {"lat" : None, "lng" : None},
            "speed": None,
            "heading": None,
            "isMoving": False,
            "isStopped": False}
            
baseGps = {"lat": None, "lng": None}

boatsensor = {"id": boatinfo["id"],
		      "temperature": None}

boat.emit("boat-base", boatinfo, SetBase)
boat.emit('boat-ping', boatinfo, CheckPing)
boat.emit('boat-sensor', boatsensor, CheckSensor)

try :
	boatinfo["gps"]["lat"], boatinfo["gps"]["lng"] = locate()
except Exception as ex: 
	print("error6", ex)	

print("I am at lat: %s, lat %s" % (boatinfo["gps"]["lat"], boatinfo["gps"]["lng"]))
LastPing = time.time()
LastSensor = time.time()
BaseFlag = False
print("connected to server")

while True:
	try:
		boatinfo["gps"]["lat"], boatinfo["gps"]["lng"] = locate()
		boatinfo["heading"] = degrees(getYaw())
	except Exception as ex: # 에러 종류
		print("error5", ex)

	if boatProcess is not None :
		while True :
			output = boatProcess.stdout.readline()
			if output.startswith('distance: ') == True:
				print('=============================================distance')
				print(output)
			elif output.startswith('time : ') == True :
				sensorTime = float(output[7:])
				nowTime = time.time()
				delaytime = nowTime - sensorTime
				# print('delaytime : %f' %delaytime)
				if delaytime < 0.2 :
					print('break!==========================================')
					break
			elif output.startswith('arrived dest') == True :
				break
			print(output)

		if boatProcess.poll() is not None:
			print("boat arrived dest")
			boat.emit('boat-arrived', boatinfo)
			boatstate =1
			boatProcess=None

	else :
		rdest_lati = radians(dest_lati)
		rdest_long = radians(dest_long)
		rClati = radians(boatinfo["gps"]["lat"])
		rClong = radians(boatinfo["gps"]["lng"])

		Dlati = rdest_lati - rClati
		Dlong = rdest_long - rClong
		dist = UtmToDistance(Dlati, Dlong, rdest_lati, rClati)

		if dist >3 and boatstate ==1:
			boatstate =0
			cmd = ["python","/home/pi/hg/gotodest.py"]
			boatProcess = subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
			boatProcess.stdin.write("%s\n" %str(dest_lati))
			boatProcess.stdin.write(str(dest_long))
			boatProcess.stdin.close()

	if time.time() > LastPing + 1 and PingSent == True:
		PingSent = False
		print(boatinfo)
		boat.emit('boat-ping', boatinfo, CheckPing)

	if time.time() > LastSensor + 10 and SensorSent == True:
		SensorSent = False
		# boatsensor["temperature"] = read_temp()
		boat.emit('boat-sensor', boatsensor, CheckSensor)

	if time.time() > LastPing + 60 and BaseFlag == False:
		print("moving to base [lat: %s, lng: %s]" % (baseGps["lat"], baseGps["lng"]))
		dest_lati =baseGps["lat"]
		dest_long =baseGps["lng"]
		
		"""boat process"""
		if boatProcess is not None:
			if boatProcess.poll() == None:
				boatProcess.terminate()
				boatProcess.kill()
			print(boatProcess)
			
			if boatProcess is not None:
				start = time.time()
     			while boatProcess.poll() == None:
        			if time.time() - start > 10:
						boatProcess.terminate()
						boatProcess.kill()
						start = time.time()
			boatProcess =None

			AngleWrite(1)
			SpeedWrite(0, speed)
			print("kill boat process")

		cmd = ["python", "/home/pi/hg/gotodest.py"]
		boatProcess = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		boatProcess.stdin.write("%s\n" %str(dest_lati))
		boatProcess.stdin.write(str(dest_long))
		boatProcess.stdin.close()
		print("goto base")

		BaseFlag = True 

	boat.wait(seconds=0.1)