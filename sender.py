# This file is part of home sesnors project.
# Copyright (c) 2017, Guy Kemeber, Samer Mansour, and Maen Artimy

from datetime import datetime
from influxdb import InfluxDBClient
from cfg import ConfigReader
import util
import logging, fnmatch, time, calendar, os, sys, csv, requests


class PatchSender():

    sent_files_log = 'sentfiles.log'
    url_write_template = 'http://{}:{}/write?db={}'
    
    def __init__(self, **args):
        if not args: exit("Cloud settings not found in the configuration file!")
        host = args.get('host', None)
        if not host: exit("Host address not found in the configuration file!")
        port = args.get('port', 8086)

        dbname = args.get('dbname', None)
        if not dbname: exit("Database name not found in the configuration file!")
        self.patch_size = args.get('patch', 1)
        self.retries = args.get('retries', 3)

        self.url_write = self.url_write_template.format(host, port, dbname)

    def sendData(self, fullname, testmode=False):
        self.testmode = testmode
        flist = self._getFilesList(fullname)
        self._readFiles(flist)
            
    def _getFilesList(self, fullname):
        try:
            fileprefix = os.path.splitext(fullname)[0]        # name w/o extension
            filebase = os.path.basename(fileprefix)           # name w/o path
            dirname = os.path.dirname(fileprefix) or '.'      # only path

            return sorted([f for f in os.listdir(dirname) if fnmatch.fnmatch(f, filebase+'*')])
        except:
            e = sys.exc_info()[0]
            logging.error("Error: {}".format(e) )
            return None

    def _readFiles(self, filelist):
        # read list of files that have been sent
        sentfiles = []
        try:
            with open(self.sent_files_log, 'r') as sfile:
                # read lines and remove the the newline char 
                sentfiles = [f[:-1] for f in sfile.readlines()]                
        except:
            pass

        for f in [x for x in filelist if x not in sentfiles]:
            with open(self.sent_files_log, 'a') as sfile:
                ext = os.path.splitext(f)[1]
                print(ext)
                if (ext.upper() == '.CSV' and self._sendCSVFile(f)) or \
                    (ext.upper() == '.DAT' and self._sendInfluxFile(f)):
                    sfile.write(f + '\n')
                else:
                    print('Attempt to send data from "{}" to remote server was not successful.'.format(f))

    MSG = 'Data from "{}" was sent to remote server successfully ({} lines in {} seconds.)'
    
    def _sendCSVFile(self, filename):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            a = datetime.now()
            index, counter, payload = 0, self.patch_size, []
            for row in reader:
                payload.append(self._getInfluxPayload(row))
                if not index % counter:
                    if not self._sendPayload('\n'.join(payload)):
                        return False
                    payload = []
                index += 1
            if payload:
                if not self._sendPayload('\n'.join(payload)):
                    return False
            b = datetime.now()
            print(self.MSG.format(filename, index, (b-a).seconds))
        return True

    def _sendInfluxFile(self, filename):
        with open(filename, 'r') as f:
            reader = f.readlines()
            a = datetime.now()
            index, counter, payload = 0, self.patch_size, []
            for row in reader:
                payload.append(row)
                if not index % counter:
                    if not self._sendPayload(''.join(payload)):
                        return False
                    payload = []
                index += 1
            if payload:
                if not self._sendPayload(''.join(payload)):
                    return False
            b = datetime.now()
            print(self.MSG.format(filename, index, (b-a).seconds))
        return True
    
    def _nanosec(self, t):
        dt = datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')  # given in UTC
        return calendar.timegm(dt.timetuple()) * 1e9 # if dt is local time, use time.mktime(dt.timetuple()) * 1e9

    def _getInfluxPayload(self, row):
        influx_payload = '{},room=basement temperature={},humidity={} {:.0f}'     # sensor, temperature,humidity time
        [t, sensor, temp, hum] = row
        return influx_payload.format(sensor, temp, hum, self._nanosec(t))

    def _sendPayload(self, payload):
        if self.testmode:
            print(payload)
            return True

        count = self.retries
        while count:
            r = requests.post(self.url_write, payload)
            if r.status_code == 204:                             # hard-coded code!
                return True
            count -= 1
        return False
           
if __name__ == '__main__':
    # Read configuration file
    cfg = ConfigReader('config.yaml')

    fullname = cfg.get("record_file")
    cloud_settings = cfg.getSection("cloud")
    
    sender = PatchSender(**cloud_settings)
    sender.sendData(fullname)
           
##    t = '2017-12-27 00:28:09.270813'  # UTC
##    dt = datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')
##    print('%.0f' % (calendar.timegm(dt.timetuple()) * 1e9))
