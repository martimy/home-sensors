# This file is part of home sesnors project.
# Copyright (c) 2017, Guy Kemeber, Samer Mansour, and Maen Artimy

import csv, os
from datetime import datetime, date
import util, time


class DataRecorder():
    """
    The class creates file(s) to record received data in csv (comma-seperated
    text) format or in InfluxDB format. By default, the class starts a new file every day (local time).
    """

    INFLUX_FORMAT = 'INFLUX'
    CSV_FORMAT = 'CSV'
    
    ext_csv = ".csv"
    ext_influx = ".dat"

    def __init__(self, **settings):
        self.daily = settings.get('daily', False)
        filename = settings.get('file', 'sensordata.dat')
        self.fileprefix = os.path.splitext(filename)[0]
        self.format = settings.get('format', 'influx')

    def writeData(self, sensorname, fieldnames, data):
        if self.format.upper() == self.INFLUX_FORMAT:
            self.writeInfluxData(sensorname, fieldnames, data)
        elif self.format.upper() == self.CSV_FORMAT:
            self.writeCSVData(sensorname, fieldnames, data)
        
    def writeCSVData(self, sensorname, fieldnames, data):
        if self.daily:
            # Open a new file for each day
            filename = self.fileprefix + '-' + str(date.today()) + self.ext_csv
        else:
            # Makes sure the file extension is always the same
            filename = self.fileprefix + self.ext_csv

        with open(filename, 'a') as myFile:
            writer = csv.writer(myFile)
            writer.writerow([str(datetime.utcnow())] + [sensorname] + data)

    def writeInfluxData(self, sensorname, fieldnames, data):
        # 'sensorname, field1=value1,...,fieldN=valueN time'

        assert len(fieldnames) == len(data)

        dt = datetime.now()
        ns = time.mktime(dt.utctimetuple()) * 1e9
        line = '{},room=basement '.format(sensorname)

        flist = []
        for f, d in zip(fieldnames, data):
            flist.append('{}={}'.format(f,d))
            
        line +=  '{} {:.0f}'.format(','.join(flist), ns)
        
        if self.daily:
            # Open a new file for each day
            filename = self.fileprefix + '-' + str(date.today()) + self.ext_influx
        else:
            # Makes sure the file extension is always the same
            filename = self.fileprefix + self.ext_influx
            
        with open(filename, 'a') as myFile:
            myFile.write(line + '\n')
            
if __name__ == "__main__":
    # This is for testing only. It is executed when the script
    # is run as a standalone app

    import random, time

##    recorder = DataRecorder('/home/pi/sensors/csvexample.csv', daily=True)
##    start_time = time.time()
##    while time.time() - start_time < 10:
##        recorder.writeCSVData([random.random()])
##        time.sleep(1)

    recorder = DataRecorder('/home/pi/sensors/influxexample.dat', daily=True)
    start_time = time.time()
    while time.time() - start_time < 10:
        recorder.writeInfluxData('dht', ['temperature','humudity'], [random.random()*20, random.random()*30])
        time.sleep(1)

