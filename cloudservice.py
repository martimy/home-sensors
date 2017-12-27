# This file is part of home sesnors project.
# Copyright (c) 2017, Guy Kemeber, Samer Mansour, and Maen Artimy

from datetime import datetime
from influxdb import InfluxDBClient
import logging

class CloudService():
    user = 'root'
    password = 'root'
    dbname = 'house'
    dbuser = 'samer'
    dbuser_password = 'samer_secret_password'
    query = 'select Float_value from temp;'
    json_body = [
        {
            "measurement": "dht",          # this is similar to table name in RDB
            "time": datetime.now(),         # time stamp
            "fields": {                     # data can be anything like RDB
                "temperature": 22.0,
                "humidity": 22.0,
            },
            "tags": {                       # tags are text only and can be indexed
                "room": "basement",
            }
        }
    ]

    def __init__(self, host='localhost', port=8086):
        logging.getLogger("sensorlog")
        self.client = InfluxDBClient(host, port, self.user, self.password, self.dbname)
        logging.info('Connected to InfluxDB at {}, port {}'.format(host, port));

    def sendToCloud(self, sensor_name, sensor_data):
	self.json_body[0]["time"] = datetime.utcnow()
	if sensor_name == 'DHT':
	    self.json_body[0]["measurement"] = 'dht'
	    self.json_body[0]["fields"]["temperature"] = sensor_data[0]
            self.json_body[0]["fields"]["humidity"] = sensor_data[1]
        elif sensor_name == 'ACL':
	    self.json_body[0]["measurement"] = 'accelerometer'
	    self.json_body[0]["fields"]["x-axis"] = sensor_data[0]
            self.json_body[0]["fields"]["y-axis"] = sensor_data[1]
            self.json_body[0]["fields"]["z-axis"] = sensor_data[2]
        else:
            logging.debug('Unrecognized sensor!')
            return

        self.client.write_points(self.json_body)
        logging.debug('Writing: {0}'.format(self.json_body))

if __name__ == '__main__':
    service = CloudService(host='192.168.2.31')
    service.sendToCloud([4.0,6.0])
