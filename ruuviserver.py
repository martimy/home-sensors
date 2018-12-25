#!/usr/bin/python

# Copyright (c) Maen Artimy  2018

#import os, sys
#import socket
import time, pytz
from datetime import datetime, date
from ruuvitag_sensor.ruuvi_rx import RuuviTagReactive

ruuvi_rx = RuuviTagReactive()

def handle_data(d):
    if not d:
        return
    
    # Get server time in UTC
    
    # Get UTC time
    ns = time.time() * 1e9
    #ns -= time.daylight * 60 * 60 * 1e9
    today = time.strftime('%Y-%m-%d', time.gmtime())

    filename = "/home/pi/sensordata/sensordata" + '-' + today + ".dat"

    # get the last reading in the buffer
    tagmac = d[-1][0].replace(':','')
    tagdata = d[-1][1]

    # Sensor time gives the same time as ns
    #dt2 = datetime.strptime(tagdata["time"], "%Y-%m-%d %H:%M:%S.%f")
    #ns2 = time.mktime(dt2.utctimetuple()) * 1e9
    
    # Get the data in a keyward=value format
    line = 'INWK,tag={} '.format(tagmac)
    line += ','.join(['{}={}'.format(k,tagdata[k]) for k in tagdata if k!='time'])   
    line += ' {:.0f}'.format(ns)
    
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

