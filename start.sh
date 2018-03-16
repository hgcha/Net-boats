#!/usr/bin/env bash

sudo forever cleanlogs
sudo forever start --uid gps -c python gps.py
sudo forever start --uid imu -c python imu.py
sudo forever start --uid server -c python destserver.py
sudo service motion start
