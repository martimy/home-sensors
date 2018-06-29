# This file is part of home sensors project.
# Copyright (c) 2018, Guy Kemeber, Samer Mansour, and Maen Artimy

import requests
from datetime import datetime as dt
from datetime import timedelta as delta
import json

# To differentiate between volunteers
rr_tag_filter = ['3136471934373039260400', '31364719343730391F0400']

GAP_TIME = 30 #Secounds

WIDTH = 600
HEIGHT = 400

class DataReceiver():
    """Use this class to get data from the server
    """
    url_read_template = 'http://{}:{}/query'
    not_found_msg = '{} not defined!'

    cache = {}

    def __init__(self, host='0.0.0.0', port=8086, cachefile="cache.txt"):
        self.url_read = self.url_read_template.format(host, port)
        self.cachefile = cachefile
        try:
            with open(cachefile, 'r') as infile:
                self.cache = json.load(infile)
        except IOError as e:
            print("{}. Moving on.".format(e))

    def retrieve_data(self, **args):
        """
        Sends a GET requet to the remote server.
        """

        try:
            dbname = args['dbname']
            series = args['series']
            time_start = args['start']
            time_end = args['end']
        except Exception as e:
            exit(e)

        query = "SELECT * FROM {} WHERE time >= '{}' and time <'{}'".format(series, time_start, time_end)

        # read data from the cache, if available
        if query in self.cache:
            filename = self.cache[query]
            with open(filename, 'r') as infile:
                print("Reading data from cache.")
                return json.load(infile)

        payload = {'db': dbname, 'q': query}
        try:
            print("Reading data from server.")
            r = requests.get(self.url_read, payload)
            if r.status_code == 200:
                data = r.json()["results"][0]["series"][0]
                filename = "data{}.txt".format(len(self.cache)+1)

                # save the query results
                with open(filename, 'w') as outfile:
                    json.dump(data, outfile)
                    self.cache[query] = filename

                # save the new cache content
                with open(self.cachefile, 'w') as outfile:
                    json.dump(self.cache, outfile)

                return data

        except Exception as e:
            s = requests.session()
            s.config['keep_alive'] = False
            print(e)
        return None

    def print_data(self, series, filename="timeseries.txt", header=False):
        with open(filename, 'w') as file:
            if header:
                file.write(','.join(series['columns'])+"\n")
            for values in series['values']:
                file.write(','.join(map(str, values))+"\n")

    def get_state_rep(self, series, filter=None):
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
                trans += [[last_anchor_time, last_anchor]]
                trans += [[last_time, None]]
                states.setdefault(last_anchor, len(states))

                # start over
                last_time = dt.strptime(values[TIME], '%Y-%m-%dT%H:%M:%SZ')
                last_anchor_time = last_time
                last_anchor = values[ANCHOR]

                continue

            if values[ANCHOR] != last_anchor:
                # df = time - last_anchor_time
                # print('{}, Anchor change : {}, Anchor: {}'.format(last_anchor_time, df, last_anchor))
                trans += [[last_anchor_time, last_anchor]]
                states.setdefault(last_anchor, len(states))
                #print(','.join(map(str, values)))
                last_anchor = values[ANCHOR]
                last_anchor_time = time

            last_time = time
        # print('{}, Anchor change : {}, Anchor: {}'.format(last_anchor_time, time-last_anchor_time, last_anchor))
        trans += [[last_anchor_time, last_anchor]]
        states.setdefault(last_anchor, len(states))

        return trans, states

class Plotter():

    def __init__(self, trans, states):
        tmp = [t[0].timestamp() for t in trans]
        self.x_axis = [t-tmp[0] for t in tmp]
        self.y_axis = [states[s[1]] for s in trans]

        self.x_scale = WIDTH / self.x_axis[-1]
        self.y_scale = HEIGHT / len(states)



if __name__ == '__main__':
    cloud_settings = {'host': '192.168.2.12'}
    # Time in UTC
    db_settings = {'dbname': 'house',
                   'series': 'LOC',
                      'start': '2018-06-23T00:00:00Z',
                      'end': '2018-06-23T08:00:00Z'}

    receiver = DataReceiver(host='adhoc.no-ip.org')
    data = receiver.retrieve_data(**db_settings)
    #data = results[0]["series"][0]

    if not data:
        exit("Could not receive data!")

    # Print everything
    # receiver.print_data(data)

    # Get states representation of data
    trans, states = receiver.get_state_rep(data, rr_tag_filter)
    print("States:\n ",states)
    print("Transitions:\n ",trans)


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
