# contains functions that return important project directories

import os

CONFIGDIR = os.path.dirname(os.path.realpath(__file__))


def arduino_dir():
    root_dir_name = "Self-Driving-Buggy"
    root_dir = CONFIGDIR[:CONFIGDIR.rfind(root_dir_name) + len(root_dir_name)]
    return root_dir + "/Arduino/"


directories = {
    'arduino': arduino_dir(),
    'board': CONFIGDIR + "/board/",
    'camera': CONFIGDIR + "/camera/",
    'videos': CONFIGDIR + "/camera/Videos/",
    'images': CONFIGDIR + "/camera/Images/",
    'controller': CONFIGDIR + "/controller/",
    'maps': CONFIGDIR + "/controller/maps/",
    'gpx': CONFIGDIR + "/controller/maps/gpx/",
    'scripts': CONFIGDIR + "/scripts/",
}


def get_dir(directory=""):
    if ':' in directory:
        shortcut_start = directory.find(":") + 1
        shortcut_end = directory.find("/", shortcut_start)
        if shortcut_end == -1:
            key = directory[shortcut_start:]
            return directories[key]
        else:
            key = directory[shortcut_start: shortcut_end]
            return directories[key] + directory[shortcut_end + 1:]


    elif len(directory) > 0 and directory[0] == '/':
        return directory

    else:
        return CONFIGDIR + "/" + directory
