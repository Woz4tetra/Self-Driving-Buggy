import csv
import time
import sys

def get_map(file_name=None):
    if __name__ == '__main__':
        directory = "storage/" + file_name
    else:
        import config
        directory = config.get_project_dir() + "/map/storage/" + file_name
    with open(directory, 'rb') as csvfile:
        map_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        parsed = [[float(row[0]), float(row[1])] for row in map_reader]
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

def convert_gpx(file_name):
    with open("storage/gpx/" + file_name, 'r') as gpx_file:
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
        write_map(data, file_name[:-4])

if __name__ == '__main__':
    arguments = sys.argv
    
    convert_gpx(arguments[1])
