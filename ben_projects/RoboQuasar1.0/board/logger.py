"""
    Written by Ben Warwick

    data.py, written for RoboQuasar1.0
    Version 12/7/2015
    =========

    Allows for easy sensor and command data logging.

    This class integrates nicely with the Sensor and Command objects found in
    data.py. It will take in the input object's data and write it to a csv file
    free of charge!

    Please refer to objects.py for proper usage tips.
"""

import csv
import sys
import time

sys.path.insert(0, '../')

import config


class Recorder(object):
    def __init__(self, file_name=None, directory=None):
        if directory == None:
            self.directory = config.get_dir(":logs")
        else:
            if directory[-1] != "/":
                directory += "/"
            self.directory = directory

        if file_name == None or len(file_name) <= 4:
            self.file_name = time.strftime("%c").replace(":", ";") + ".csv"
        else:
            if file_name[-4:] != ".csv":
                file_name += ".csv"
            self.file_name = file_name

        self.csv_file = open(self.directory + self.file_name, 'a')

        self.writer = csv.writer(self.csv_file, delimiter=',',
                                 quotechar='|',
                                 quoting=csv.QUOTE_MINIMAL)

        self.time0 = time.time()

    def add_data(self, object_name, serial_object):
        time_stamp = time.time() - self.time0

        if type(serial_object.data) != list:
            data = [serial_object.data]
        elif serial_object.data != None:
            data = serial_object.data
        else:
            data = []

        print((repr(serial_object.current_packet)))
        self.writer.writerow(
            [str(time_stamp),
             str(object_name),
             str(serial_object.object_id),
             str(serial_object.current_packet.strip("\n"))] + data
        )

    def close(self):
        self.csv_file.close()
