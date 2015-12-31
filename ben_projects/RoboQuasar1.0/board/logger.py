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

        self.current_row = ["timestamp"]
        self.sensor_indices = {}
        self.header_row = []

        self.time0 = time.time()

    def add_sensor(self, sensor, name, *data_names):
        assert len(data_names) == len(sensor.formats)
        self.header_row.append((sensor.object_id, name, sensor, data_names))

    def end_init(self):
        self.header_row.sort(key=lambda element: element[0])
        names_row = [""]
        for sensor_info in self.header_row:
            object_id, sensor_name, sensor, data_names = sensor_info

            self.sensor_indices[object_id] = len(self.current_row)

            names_row.append(sensor_name)
            names_row += [""] * (len(data_names) - 1)
            self.current_row += data_names
        self.writer.writerow(names_row)
        self.writer.writerow(self.current_row)


    def add_data(self, serial_object):
        start_index = self.sensor_indices[serial_object.object_id]
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
