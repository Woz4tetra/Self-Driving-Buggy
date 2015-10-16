import csv
import time


def get_map(current_file="Tue Oct 13 20;43;26 2015"):
    with open("storage/" + current_file + ".csv", 'rb') as csvfile:
        map_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        parsed = [[int(row[0]), int(row[1])] for row in map_reader]
        return parsed


def write_map(data, file_name=None):
    if file_name == None:
        file_name = time.strftime("%c").replace(":", ";")
    with open("storage/" + file_name + ".csv", 'wb') as csvfile:
        map_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)
        for row in data:
            assert len(row) == 2
            map_writer.writerow(row)


if __name__ == '__main__':
    print get_map()
