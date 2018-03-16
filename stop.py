#-*-coding:utf-8 -*-
from sensor_info import *
import json

json_data = open("config.json").read()
data = json.loads(json_data)
speed = data["PWM"]

AngleWrite(2)
SpeedWrite(0, speed)