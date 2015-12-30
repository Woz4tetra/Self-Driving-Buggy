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
    def __init__(self, sensor_dict, file_name=None, directory=None):
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

        self.sensor_dict = sensor_dict
        self.sensor_indices = {}

        name_row = ["time (sec)"]
        data_name_row = [""]
        for sensor_name, sensor_info in self.sensor_dict.items():
            sensor = sensor_info[0]
            data_name_row += sensor_info[1:]

            self.sensor_indices[sensor_name] = len(name_row)
            name_row.append("%s: %s" % (sensor_name, str(sensor.object_id)))
            name_row += [""] * (len(sensor_info[1:]) - 1)

        self.current_row = [""] * (len(name_row))

        assert len(name_row) == len(data_name_row)
        self.writer.writerow(name_row)
        self.writer.writerow(data_name_row)

        self.time0 = time.time()

    def add_data(self, object_name, serial_object):
        start_index = self.sensor_indices[object_name]
        if type(serial_object.data) == list:
            for index in range(len(serial_object.data)):
                self.current_row[index + start_index] = serial_object.data[index]
        else:
            self.current_row[start_index] = serial_object.data

    def end_row(self):
        self.current_row[0] = time.time() - self.time0

        self.writer.writerow(self.current_row)

    def close(self):
        self.csv_file.close()
