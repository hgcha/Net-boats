#-*-coding:utf-8 -*-
import serial
import time

serYaw = serial.Serial('/dev/ttyAMA0', 57600)
serYaw.close()
serYaw.open()
yaw_past =400
def yawMutexLock() :
	yawMutex = open("yawMutex.txt", 'r')
	while True :
		if yawMutex.readline() == "0" :
			yawMutex.close()
			print("imu is locked")
			break
		time.sleep(0.01)
        print("IMU has been locked")
	yawMutex = open("yawMutex.txt", 'w')
	yawMutex.write("1")
	yawMutex.close()

def yawMutexUnLock() :
	yawMutex = open("yawMutex.txt", 'w')
	print("IMUnlock")
	yawMutex.write("0")
	yawMutex.close()

yawMutex = open("yawMutex.txt", 'w')
yawMutex.write("0")
yawMutex.close()
print("init IMU success")

while True:
	try:
		serYaw.flush()
		# yawMutexLock()
		data=serYaw.readline()
		# yawMutexUnLock()
		print(data)
		if data.startswith('#YPR=') == True:
			print(data)
			yprRaw = data
			ypr = yprRaw.split(',')
			YAW = ypr[0]
			PITCH = float(ypr[1])
			ROLL = float(ypr[2])
			YAW = float(YAW[5:])
			if YAW < 0 :
				YAW = YAW + 360
			print(YAW)	
			
			yaw = open("yawValue.txt",'w')
			yaw.write(str(YAW))
			yaw_past = YAW
        	yaw.close()    
	    	# print ('YAW: %f' % YAW)
			# print ('PITCH: %f' %PITCH)
			# print ('ROLL: %f' % ROLL)
    	# time.sleep(0.1)
	except Exception as ex: 
		if yaw_past !=400:
			yaw = open("yawValue.txt",'w')
			yaw.write(str(yaw_past))
			yaw.close()
		print("error10", ex)