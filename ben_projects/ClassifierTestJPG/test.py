import os

FILEDIR = os.path.dirname(os.path.realpath(__file__))

file_handle = open("bg.txt", 'r')
text = file_handle.read()

for file_name in text.splitlines():
    if not os.path.isfile(FILEDIR + "/" + file_name):
        print(file_name)
