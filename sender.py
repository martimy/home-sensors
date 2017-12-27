# This file is part of home sesnors project.
# Copyright (c) 2017, Guy Kemeber, Samer Mansour, and Maen Artimy

from datetime import datetime
from influxdb import InfluxDBClient
from cfg import ConfigReader
import util
import logging, fnmatch, time, calendar, os, sys, csv, requests


class PatchSender():
    """
    This class reads the local data files and send the data to a remote sever.
    To prevent the class from sendig the data again, the names of the processed
    files are stored in a log file.

    There is a case, however, when a file may be visited more than once. This is
    needed when the data file continutes to be appended with data after this
    class sends its current data to the remote server. To handle this senario,
    if the last modification time of the file falls within pre-defined time from 
    the current execution time of this class, the file is not added to the log.
    This means that the data in the file will be sent again to the remote server.
    This is not an optimal soultion due to repeated transmission of old data, but
    the solution is simple and there is no impact on the remote database.
    
    """

    sent_files_log = 'sentfiles.log'
    url_write_template = 'http://{}:{}/write?db={}'
    sucess_log_msg = 'Data from "{}" was sent to remote server successfully ({} lines in {} seconds.)'
    failed_log_msg = 'Attempt to send data from "{}" to remote server was not successful.'
    not_found_msg = '{} not found in the configuration file!'

    hours_past = 3
    
    def __init__(self, **args):
        if not args: exit(self.not_found_msg.format("Cloud settings"))
        host = args.get('host', None)
        if not host: exit(self.not_found_msg.format("Host address"))
        port = args.get('port', 8086)

        dbname = args.get('dbname', None)
        if not dbname: exit(self.not_found_msg.format("Database name"))
        self.patch_size = args.get('patch', 1)
        self.retries = args.get('retries', 3)

        self.url_write = self.url_write_template.format(host, port, dbname)


    def sendData(self, fullname, testmode=False):
        """
        The entry point to the app.
        In test mode, the payload of API calls to the remote server will be
        printed to the stdout.
        """
        self.testmode = testmode
        flist = self._getFilesList(fullname)
        self._readFiles(flist)
            
    def _getFilesList(self, fullname):
        """
        Gets a list of all data file with the prefix found in the
        configuration file. The files dir is extracted from the file path.
        If no path is found, the local (working) directory is used.
        """
        try:
            fileprefix = os.path.splitext(fullname)[0]        # name w/o extension
            filebase = os.path.basename(fileprefix)           # name w/o path
            dirname = os.path.dirname(fileprefix) or '.'      # only path

            return sorted([os.path.join(dirname,f) for f in os.listdir(dirname) if fnmatch.fnmatch(f, filebase+'*')])
        except:
            e = sys.exc_info()[0]
            logging.error("Error: {}".format(e) )
            return None

    def _readFiles(self, filelist):
        """
        This method ignores all the files that are found in thhe sentfiles log.
        The remaining files are processed, and if transmission is successful,
        they are added to the sentfiles log. See class description of caveats.
        """

        HOUR = 3600 # seconds
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
                ext = os.path.splitext(f)[1].upper()
                if (ext == '.CSV' and self._sendCSVFile(f)) or \
                    (ext == '.DAT' and self._sendInfluxFile(f)):

                    # If the file has not been modfied for x hours
                    # it is safe to ignore it in the next run
                    if (time.time() - os.path.getmtime(f))/HOUR >= self.hours_past:
                        sfile.write(f + '\n')
                else:
                    print(self.failed_log_msg.format(f))
    
    def _sendCSVFile(self, filename):
        """
        This method reads csv file and translates each row contnet to a database
        query that can be executed by the remote server (which supports InfluxDB).
        """
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
            print(self.sucess_log_msg.format(filename, index, (b-a).seconds))
        return True

    def _sendInfluxFile(self, filename):
        """
        This method reads a .dat file. Each row in the file represents a database
        query that can be executed by the remote server (which supports InfluxDB).

        # this method is almost identical to the one above so maybe there
        # is a way to merge the two
        """
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
            print(self.sucess_log_msg.format(filename, index, (b-a).seconds))
        return True
    
    def _nanosec(self, t):
        """
        A utility method that retuns Unix time given UTC time in rfc3339 format.
        """
        dt = datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')  # given in UTC
        return calendar.timegm(dt.timetuple()) * 1e9 # if dt is local time, use time.mktime(dt.timetuple()) * 1e9

    def _getInfluxPayload(self, row):
        """
        This method is called by the csv file reader to translate the comma-seperated
        columns in the file into a database query.

        TODO: This works only for DHT sensor. It neede o be generalized
        """
        influx_payload = '{},room=basement temperature={},humidity={} {:.0f}'     # sensor, temperature,humidity time
        [t, sensor, temp, hum] = row
        return influx_payload.format(sensor, temp, hum, self._nanosec(t))

    def _sendPayload(self, payload):
        """
        Sends a POST requet to the remote server.
        """
        if self.testmode:
            print(payload)
            return True

        count = self.retries
        while count:
            r = requests.post(self.url_write, payload)
            if r.status_code == 204:                             # hard-coded code!
                return True
            count -= 1
        logging.error('Code:{} Msg:{}'.format(r.status_code,r.text))
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
