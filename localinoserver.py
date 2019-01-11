#!/usr/bin/python

# By Steffen
# Heuel und Loeher GmbH & Co KG
# Update: Steffen
# empfaengt UDP datagramme von den Anchors
# 11.10.2016

# Modified 15/2/2017
# By Maen Artimy

import time
import socket
from uuid import getnode


NODE_ID = getnode()
UDP_IP = '0.0.0.0'
UDP_PORT = 10000
version = "0.2"

print("Localino Datadisplay started, Version: ", version)

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))


# ----- Write to file -------------------------------------------------------
#f = open(time.strftime("%Y%m%d-%H%M%S") + '_Rohdaten.csv','w')
#f.write('H&L Localino data receveier. \n')

#meter_wanted = 1

# ------ MAIN ----
# format:
# LOC,anchor=<anchorname>,tag=<tagname> range=<range>,cyc=<cyc> <time>


while True:
    try:
        rc, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        # print(rx)
        rx = rc.decode('utf-8').split(',')
        anchor = rx[0]
        tag = rx[1]
        range = float(rx[2])
        cycle = rx[3]
        print(rx)

        # Catch anchor idle msg
        if (tag == "Anchor"):
            print("Anchor ", anchor, " active")
        else:
            # Get UTC time
            ns = time.time() * 1e9
            today = time.strftime('%Y-%m-%d', time.gmtime())

            #filename = "/home/pi/sensordata/" + NODE_ID + '-' + today + ".dat"
            filename = "/home/pi/sensordata/data-{}-{}.dat".format(today,NODE_ID)

            line = 'LOC,anchor={},tag={} '.format(anchor, tag)
            line += 'range={},cycle={} {:.0f}'.format(range, cycle, ns)

            with open(filename, 'a') as myFile:
                myFile.write(line + '\n')

    except:
        pass
