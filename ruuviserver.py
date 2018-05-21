#!/usr/bin/python

# Copyright (c) Maen Artimy  2018

#import os, sys
#import socket
import time, pytz
from datetime import datetime, date
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive

ruuvi_rx = RuuviTagReactive()

def handle_data(d):

    # Get server time in UTC
    
    # Method 1: does not seem to work well with daylight saving time
    #dt = datetime.now()
    #ns = time.mktime(dt.utctimetuple()) * 1e9
    
    # Method 1: does not seem to work well with daylight saving time
    utc = pytz.timezone('UTC')
    now = utc.localize(datetime.utcnow())
    ns3 = time.mktime(now.timetuple()) * 1e9

    filename = "/home/pi/sensordata/sensordata" + '-' + str(date.today()) + ".dat"

    # get the last reading in the buffer
    tagmac = d[-1][0].replace(':','')
    tagdata = d[-1][1]

    # Sensor time gives the same time as ns
    #dt2 = datetime.strptime(tagdata["time"], "%Y-%m-%d %H:%M:%S.%f")
    #ns2 = time.mktime(dt2.utctimetuple()) * 1e9
    
    # Get the data in a keyward=value format
    line = 'RUUVI,tag={} '.format(tagmac)
    line += ','.join(['{}={}'.format(k,tagdata[k]) for k in tagdata if k!='time'])   
    line += ' {:.0f}'.format(ns3)
    
    with open(filename, 'a') as myFile:
        myFile.write(line + '\n')

    
# Print only last data every 10 seconds for C8:1C:75:B1:E4:FB
ruuvi_rx.get_subject().\
    filter(lambda x: x[0] == 'C8:1C:75:B1:E4:FB').\
    buffer_with_time(10000).\
    subscribe(handle_data)

ruuvi_rx.get_subject().\
    filter(lambda x: x[0] == 'C8:32:49:63:9C:98').\
    buffer_with_time(10000).\
    subscribe(handle_data)

ruuvi_rx.get_subject().\
    filter(lambda x: x[0] == 'F1:4A:DA:A1:8E:1D').\
    buffer_with_time(10000).\
    subscribe(handle_data)
