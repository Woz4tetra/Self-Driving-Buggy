import csv
import sys
import time
import config

class Recorder():
    def __init__(self, file_name=None):
        if file_name == None:
            self.file_name = time.strftime("%c").replace(":", ";")
        else:
            self.file_name = file_name
        
        directory = config.get_project_dir() + "/data/recorded/" + self.file_name
        
        self.csvfile = open(directory + ".csv", 'a')

        self.writer = csv.writer(self.csvfile, delimiter=',',
                                 quotechar='|',
                                 quoting=csv.QUOTE_MINIMAL)
        
    def add_data(self, data_row):
        self.writer.writerow(data_row)
    
    def close(self):
        self.csvfile.close()
