# This file is part of home sensors project.
# Copyright (c) 2018, Guy Kemeber, Samer Mansour, and Maen Artimy

import requests
from datetime import datetime as dt
from datetime import timedelta as delta
#import matplotlib.pyplot as plt

# To differentiate between volunteers
rr_tag_filter = ['3136471934373039260400', '31364719343730391F0400']

GAP_TIME = 30 #Secounds

class DataReceiver():
    """Use this class to get data from the server
    """
    url_read_template = 'http://{}:{}/query'
    sucess_log_msg = 'Data from "{}" was sent to remote server successfully ({} lines in {} seconds.)'
    failed_log_msg = 'Attempt to send data from "{}" to remote server was not successful.'
    not_found_msg = '{} not defined!'

    def __init__(self, **args):
        host = args.get('host', '0.0.0.0')
        port = args.get('port', 8086)
        self.url_read = self.url_read_template.format(host, port)

    def retrieve_data(self, **args):
        """
        Sends a GET requet to the remote server.
        """

        dbname = args.get('dbname', None)
        if not dbname:
            exit(self.not_found_msg.format("Database name"))
        series = args.get('series', None)
        if not dbname:
            exit(self.not_found_msg.format("series name"))
        time_start = args.get('start', None)
        if not dbname:
            exit(self.not_found_msg.format("start time"))
        time_end = args.get('end', None)
        if not dbname:
            exit(self.not_found_msg.format("end time"))

        query = "SELECT * FROM {} WHERE time >= '{}' and time <'{}'".format(series, time_start, time_end)
        payload = {'db': dbname, 'q': query}

        try:
            r = requests.get(self.url_read, payload)
            if r.status_code == 200:
                return r.json()["results"]
        except Exception as e:
            print(e)
        return None

    def print_data(self, series, filename="timeseries.txt", header=False):
        with open(filename, 'w') as file:
            if header:
                file.write(','.join(series['columns'])+"\n")
            for values in series['values']:
                file.write(','.join(map(str, values))+"\n")

    def generate_states(self, series, filter=None):
        trans = []
        states = {None: 0}

        ANCHOR = series["columns"].index("anchor")
        TAG = series["columns"].index("tag")
        TIME =  series["columns"].index("time")

        if filter:
            filtered = [values for values in series['values'] if values[TAG] in filter]
        else:
            filtered = series['values']

        last_time = dt.strptime(filtered[0][TIME], '%Y-%m-%dT%H:%M:%SZ')
        last_anchor_time = last_time
        last_anchor = filtered[0][ANCHOR]

        for values in filtered:
            time = dt.strptime(values[TIME], '%Y-%m-%dT%H:%M:%SZ')
            if time - last_time > delta(seconds = GAP_TIME):
                # gap detected, start over
                # df = time - last_time
                # print('{}, Anchor change : {}, Anchor: {}'.format(last_anchor_time, last_time - last_anchor_time, last_anchor))
                # print('{}, Gap detected  : {}, Anchor: {}'.format(last_time, df, values[ANCHOR]))
                trans += [[str(last_anchor_time), last_anchor]]
                trans += [[str(last_time), None]]
                states.setdefault(last_anchor, len(states))

                # start over
                last_time = dt.strptime(values[TIME], '%Y-%m-%dT%H:%M:%SZ')
                last_anchor_time = last_time
                last_anchor = values[ANCHOR]

                continue

            if values[ANCHOR] != last_anchor:
                # df = time - last_anchor_time
                # print('{}, Anchor change : {}, Anchor: {}'.format(last_anchor_time, df, last_anchor))
                trans += [[str(last_anchor_time), last_anchor]]
                states.setdefault(last_anchor, len(states))
                #print(','.join(map(str, values)))
                last_anchor = values[ANCHOR]
                last_anchor_time = time

            last_time = time
        # print('{}, Anchor change : {}, Anchor: {}'.format(last_anchor_time, time-last_anchor_time, last_anchor))
        trans += [[str(last_anchor_time), last_anchor]]
        states.setdefault(last_anchor, len(states))

        return trans, states

if __name__ == '__main__':
    cloud_settings = {'host': '192.168.2.12'}
    # Time in UTC
    db_settings = {'dbname': 'house',
                   'series': 'LOC',
                      'start': '2018-06-22T00:00:00Z',
                      'end': '2018-06-22T01:00:00Z'}

    receiver = DataReceiver(host='192.168.2.12')
    results = receiver.retrieve_data(**db_settings)
    data = results[0]["series"][0]
    #data = receiver.getAnchors(**db_settings)

    #print(data)
    #exit()
    if data:
        # Print everything
        receiver.print_data(data)
        # Print periods
        trans, states = receiver.generate_states(data, rr_tag_filter)
        print(states)
        print(trans)
    else:
        print("Could not receive data!")


"""
Then, the  data from InfluxDB comes similar to this:
    {
    "results": [
        {'statement_id': 0, 
        'series': [
            {'name': 'LOC', 
            'columns': ['time', 'anchor', 'cycle', 'range', 'room', 'tag'], 
            'values': [['2018-02-24T00:00:00Z', '3435471531313530270180', 146, 23.18, None, '3136471934373039310400'], 
            ['2018-02-24T00:00:00Z', '34354715313135302C0200', 146, 22.711, None, '3136471934373039310400'], 
            ['2018-02-24T00:00:01Z', '3435471531313530270180', 147, 23.147, None, '3136471934373039310400'], 
            ...
            }
        ]
        }
    }

"""

# Change the SELECT statement to retrieve the desired data set
# Example 1
# payload = {'db':'house', 'q':"SELECT range, cycle FROM LOC WHERE anchor='34354715313135302C0200' and time > '2018-02-22'"}
