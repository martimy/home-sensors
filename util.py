# This file is part of home sesnors project.
# Copyright (c) 2017, Guy Kemeber, Samer Mansour, and Maen Artimy

from cfg import ConfigReader
import logging

            
LOGNAME = 'sensorlog'
LOGFORMAT = '%(asctime)s %(levelname)s:%(message)s'

# Read configuration file
cfg = ConfigReader('config.yaml')

# Setup logging
logging.getLogger(LOGNAME)
logfile = cfg.get("logs_file")
if cfg.get("logs_level").upper() == 'DEBUG':
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO
logging.basicConfig(format=LOGFORMAT, filename=logfile, level=loglevel)
