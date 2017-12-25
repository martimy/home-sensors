import asyncore, socket, logging, os, sys
from io import StringIO
from cloudservice import CloudService
from display import DataPlotter
from cfg import ConfigReader
from recorder import DataRecorder


class SensorHandler(asyncore.dispatcher):
    """
    This class is the handler that receives data from a particular client
    One sample is formated "STXsensor,val1,val2,...,valnETX"
    Note that the data is sent as a string of characters of 1 byte each (ASCII).
    In python an ASCII character is best represented by a "bytes" variable.
    So we need to decode it into a regular string.
    """
    
    STX = b'\x02'
    ETX = b'\x03'
    data_sample = ''

    """
    optional services:
      - local file recording
      - remote server recording
      - data plotting
    """
    rec = None
    cs = None
    disp = None

    def __init__(self, sock):
        asyncore.dispatcher.__init__(self, sock)
        self.set_socket(sock)
        self.logger = logging.getLogger("sensorlog")
        self.read_buffer = StringIO()
        logging.info("SensorHandler intstantiated");

    @staticmethod
    def set_recording(rec):
        SensorHandler.rec = rec

    @staticmethod
    def set_cloud_service(service):
        SensorHandler.cs = service

    @staticmethod
    def set_display(ui):
        SensorHandler.disp = ui

    def handle_read(self):
        octet = self.recv(1)
        if (octet):
            if (octet == self.STX):
                # Re-initialize the string for each sensor reading
                self.data_sample = ''

            self.data_sample += octet.decode("UTF-8","strict")

            if (octet == self.ETX):
                # Process the sensor reading
                self._handle_sample(self.data_sample)           
    

    def _handle_sample(self, data_sample):
        msg_str = data_sample[1:-1].split(',')
        sensor_name = msg_str[0]
        data_str = msg_str[1:]
        data_float = map(lambda x: float(x), data_str)
        logging.debug('Received from sensor: {} data: [{}]'.format(sensor_name, ','.join(data_str)))

        if self.rec:
            self.rec.writeData(data_float)
        else:
            print(data_float)
                   
        # Plotting should not be called when the server is run as a background service
        if self.disp:
            if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
                self.disp.plot(data_float)

        if self.cs:
            self.cs.sendToCloud(sensor_name, data_float)

class AcceleroServer(asyncore.dispatcher):
    """
    This class works is a server waiting to get connections from the
    microcontroller. It hands the socket to the SensorHandler which will handle
    receiving the data.
    """

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger("sensorlog")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            return
        else:
            sock, addr = pair
            logging.debug('Incoming connection from {}'.format(repr(addr)))
            handler = SensorHandler(sock)

    def handle_close(self):
        print('handle_close()')
        self.close()

LOGNAME = 'sensorlog'
LOGFORMAT = '%(asctime)s %(levelname)s:%(message)s'

if __name__ == "__main__":
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

    # Set optional modules for SensorHandler
    # Send all sensor data to a local file
    if cfg.get("record_enabled"):
        filename = cfg.get("record_file")
        dailyfiles = cfg.get("record_daily")
        SensorHandler.set_recording(DataRecorder(filename, daily=dailyfiles))

    # Plot the data (should be enabled only when the app runs standalone)
    if cfg.get("display_enabled"):
        subplots = cfg.get("display_subplots")
        window = cfg.get("display_window")
        SensorHandler.set_display(DataPlotter(subplots=2, window=window))

    # Send all sensor data to a remote server in real-time
    if cfg.get("cloud_enabled"):
        remote_host = cfg.get("cloud_host")
        SensorHandler.set_cloud_service(CloudService(host=remote_host))

    # Run the server
    local_host = cfg.get("local_host")
    local_port = cfg.get("local_port")
    server = AcceleroServer (local_host, local_port)
    asyncore.loop()


