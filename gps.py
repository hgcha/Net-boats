#-*-coding:utf-8 -*-
import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600) #gps serial port
ser.close()
ser.open()
lati_past = 0
long_past = 0
latitude = 36
longitude = 127

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
	# ser.flush()

	# #dummy start
	# gps.write("12314 ")    #dummy file
	# gps.write("45624 ")
	# gps.close()
	# gpsMutexUnLock()
	# time.sleep(0.1)
	# #dummy end
	# gpsMutexLock()
	data = ser.readline()
	# data = "dsa\n"
	if data.startswith('$GNGLL'):
		location = data.split(',')
		GGAprotocolHeader_s = location[0]
		latitude = location[1]
		NS_s = location[2] # North or South
		longitude = location[3]
		EW_s = location[4] # East or West
		# print 'Header: %s' % GGAprotocolHeader_s
		# print 'Time: %s' % UTCTime_s
		print('Laitutude: %s' % latitude)
		# print 'NS : %s' % NS_s
		print('Longitude: %s' % longitude)
		# print 'EW : %s' % EW_s
		# if len(latitude[:2]) != 0:
		# 	gps = open("gpsValue.txt", "w")
		# 	processed_Lati = float(latitude[:2]) + float(Latitude[2:])/60.0 # calculated Latitude, Longitude
		# 	processed_Long = float(longitude[:3]) + float(longitude[3:])/60.0
		# 	gps.write(str(processed_Lati), str(processed_Long))
		# 	gps.close()
		# else:
		# 	print("GPS signal is not found")

		gps = open("gpsValue.txt",'w')
		# if GPS signal is founded, exit the function. else, repeat GPS finding sequence 
		print("GPS signal is not found.")
		gps.write("GPS_signal_is_not_found.")
		gps.write("done")
		gps.write("done")
			if lait_past !=0 and long_past !=0:
				print("lati : %s, long :%s " %(lait_past,long_past))
				gps.write(str(lati_past)+' '+str(long_past))
				gps.write(str(long_past)+' ')
				gps.write('done')
			gps.close()
		else :
			print ("lati : %s, long :%s " %(processed_Lati,processed_Long))
			gps.write(str(processed_Lati)+' ')
			gps.write(str(processed_Long)+' ')
			gps.write('done')
			lait_past = processed_Lati
			long_past = processed_Long
			gps.close()
	
	