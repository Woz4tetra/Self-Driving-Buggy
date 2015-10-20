import csv
import time
import os

project_dir = os.path.dirname(os.path.realpath(__file__))

def get_map(current_file="Tue Oct 13 20;43;26 2015"):
    with open(project_dir + "/storage/" + current_file, 'rb') as csvfile:
        map_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        parsed = [[float(row[0]), float(row[1])] for row in map_reader]
        return parsed


def write_map(data, file_name=None):
    if file_name == None:
        file_name = time.strftime("%c").replace(":", ";")
    with open(project_dir + "/storage/" + file_name + ".csv", 'w+') as csvfile:
        map_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        for row in data:
            assert len(row) == 2
            map_writer.writerow(row)


if __name__ == '__main__':
    print get_map()
