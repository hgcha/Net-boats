#-*-coding:utf-8 -*-
import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600) #gps serial port
ser.close()
ser.open()
lait_past = 0
long_past = 0

def gpsMutexLock() :
	gpsMutex = open("gpsMutex.txt", 'r')
	while True :
		if gpsMutex.readline() == "0" :
			gpsMutex.close()
			print("GPS is locked")
			break
		time.sleep(0.05)
		print('GPS has been locked')
	gpsMutex = open("gpsMutex.txt", 'w')
	gpsMutex.write("1")
	gpsMutex.close()

def gpsMutexUnLock() :
	gpsMutex = open("gpsMutex.txt", 'w')
	print("gpsUnlock")
	gpsMutex.write("0")
	gpsMutex.close()

gpsMutex = open("gpsMutex.txt", 'w')
gpsMutex.write("0")
gpsMutex.close()
print("init success")

while True:
	ser.flush()

	# #dummy start
	# gps.write("12314 ")    #dummy file
	# gps.write("45624 ")
	# gps.close()
	# gpsMutexUnLock()
	# time.sleep(0.1)
	# #dummy end
	gpsMutexLock()
	data = ser.readline()
	gpsMutexUnLock()
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
		
		gps = open("gpsValue.txt",'w')
		if len(Latitude_s[:2]) == 0 :		# if GPS signal is founded, exit the function. else, repeat GPS finding sequence 
			print("GPS signal is not found.")
			# gps.write("GPS_signal_is_not_found.")
			# gps.write("done")
			# gps.write("done")
			if lait_past !=0 and long_past !=0:
				print("lati : %s, long :%s " %(lait_past,long_past))
				gps.write(str(lait_past)+' ')
				gps.write(str(long_past)+' ')
				gps.write('done')
			gps.close()
		else :
			processed_Lati = float(Latitude_s[:2]) + float(Latitude_s[2:])/60.0 # calculated Latitude, Longitude
			processed_Long = float(Longitude_s[:3]) + float(Longitude_s[3:])/60.0
			print ("lati : %s, long :%s " %(processed_Lati,processed_Long))
			gps.write(str(processed_Lati)+' ')
			gps.write(str(processed_Long)+' ')
			gps.write('done')
			lait_past = processed_Lati
			long_past = processed_Long
			gps.close()
	
	time.sleep(0.1)