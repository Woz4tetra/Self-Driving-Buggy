'''
    Written by Ben Warwick
    
    map_maker.py, written for the Self-Driving Buggy Project
    Version 11/24/2015
    =========
    
    
'''

import csv
import time
import sys

sys.path.insert(0, '../')
import config

def get_map(directory=None):
    with open(directory, 'rb') as csvfile:
        map_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        parsed = [[float(row[0]), float(row[1])] for row in map_reader]
        return parsed


def write_map(data, directory=None):
    if directory == None:
        directory = time.strftime("%c").replace(":", ";")
    with open(directory + ".csv", 'wb') as csvfile:
        map_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        for row in data:
            assert len(row) == 2
            map_writer.writerow(row)

def convert_gpx(directory):
    directory = config.get_dir(directory)
    with open(directory, 'r') as gpx_file:
        contents = gpx_file.read()
        data = []

        while len(contents) > 2:
            lat_index_start = contents.find("lat") + 5
            lat_index_end = contents.find('"', lat_index_start)
            latitude = contents[lat_index_start: lat_index_end]

            contents = contents[lat_index_end:]

            lon_index_start = contents.find("lon") + 5
            lon_index_end = contents.find('"', lon_index_start)
            longitude = contents[lon_index_start: lon_index_end]

            data.append([latitude, longitude])
            # print data[-1], len(contents)

            contents = contents[lon_index_end:]

        data.pop(-1)
        write_map(data, directory[:-4])

if __name__ == '__main__':
    arguments = sys.argv
    
    convert_gpx(arguments[1])
