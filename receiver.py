# This file is part of home sesnors project.
# Copyright (c) 2018, Guy Kemeber, Samer Mansour, and Maen Artimy

from datetime import datetime
from influxdb import InfluxDBClient
#from cfg import ConfigReader
import util
import logging
import fnmatch
import time
import calendar
import os
import sys
import csv
import requests


class BatchReceiver():
    """Use this class to get data from the server
    """
    url_read_template = 'http://{}:{}/query'
    sucess_log_msg = 'Data from "{}" was sent to remote server successfully ({} lines in {} seconds.)'
    failed_log_msg = 'Attempt to send data from "{}" to remote server was not successful.'
    not_found_msg = '{} not defined!'

    hours_past = 3

    def __init__(self, **args):
        if not args:
            exit(self.not_found_msg.format("Cloud settings"))
        host = args.get('host', None)
        if not host:
            exit(self.not_found_msg.format("Host address"))
        port = args.get('port', 8086)

        dbname = args.get('dbname', None)
        if not dbname:
            exit(self.not_found_msg.format("Database name"))

        self.batch_size = args.get('batch', 1)
        self.retries = args.get('retries', 3)

        self.url_read = self.url_read_template.format(host, port, dbname)

    def receiveData(self):
        """
        Sends a GET requet to the remote server.
        """

        # Change the SELECT statement to retrieve the desired data set
        # Example 1
        #payload = {'db':'house', 'q':"SELECT range, cycle FROM LOC WHERE anchor='34354715313135302C0200' and time > '2018-02-22'"}
        # Example 2
        payload = {
            'db': 'house', 'q': "SELECT * FROM LOC WHERE time >= '2018-02-22T00:00:00Z' and time <'2018-02-24T01:00:00Z'"}

        r = requests.get(self.url_read, payload)
        if r.status_code == 200:
            self.cleanData(r.json()["results"])
        else:
            print("error ", r.json())

    def cleanData(self, results):
        """
        if this is the SELECT statement
            SELECT range, cycle FROM LOC WHERE anchor='34354715313135302C0200' and time > '2018-02-22'
        Then, the  data from InfluxDB comes similar to this:
            {
            "results": [
                {
                    "statement_id": 0,
                    "series": [
                        {
                            "name": "LOC",
                            "columns": [
                                "time",
                                "range",
                                "cycle"
                            ],
                            "values": [
                                [
                                    "2018-02-23T21:55:43.702900257Z",
                                    25.0,
                                    34
                                ],
                                [
                                    "2018-02-23T21:55:43.702900257Z",
                                    25.4,
                                    35
                                ],
                                ...
                            ]
                        }
                    ]
                },
                ...
            }
        """
        print(len(results))
        for statement in results:
            for series in statement['series']:
                print(','.join(series['columns']))
                for values in series['values']:
                    print(','.join(map(str, values)))


if __name__ == '__main__':
    cloud_settings = {'host': '192.168.2.30', 'dbname': 'host'}

    receiver = BatchReceiver(**cloud_settings)
    receiver.receiveData()
