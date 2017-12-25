import csv, os
from datetime import datetime, date
    
class DataRecorder():
    """
    The class creates file(s) to record received data in csv (comma-seperated
    text) format. By default, the class starts a new file every day (local time).
    """
    
    extension = ".csv"

    def __init__(self, filepath, daily=True):
        self.daily = daily
        self.fileprefix = os.path.splitext(filepath)[0]

    def writeData(self, seq):
        if self.daily:
            # Open a new file for each day
            filename = self.fileprefix + '-' + str(date.today()) + self.extension
        else:
            # Makes sure the file extension is always the same
            filename = self.fileprefix + self.extension

        with open(filename, 'a') as myFile:
            writer = csv.writer(myFile)
            writer.writerow([str(datetime.utcnow())] + seq)

if __name__ == "__main__":
    # This is for testing only. It i executed when the script
    # is run as a standalone app

    import random, time

    recorder = DataRecorder('/home/pi/sensors/csvexample.csv', daily=True)
    start_time = time.time()
    ls = [str(datetime.utcnow())]
    print(ls)
    print(ls+[3,4])
    while time.time() - start_time < 10:
        recorder.writeData([random.random()])
        time.sleep(1)
