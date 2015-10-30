# import sys
import os


def get_project_dir():
    project_dir = os.path.dirname(os.path.realpath(__file__))
    project_name = "Self-Driving Buggy Rev. 6"
    return project_dir[:project_dir.rfind(project_name) + len(
        project_name)]


def get_arduino_ino(file_name='SerialBox'):
    project_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = "Self-Driving-Buggy"
    project_dir = project_dir[:project_dir.rfind(root_dir) + len(
        root_dir)]

    return project_dir + "/Arduino/" + file_name + "/" + file_name + ".ino"

# project_dir = get_project_dir()
# print(project_dir)
# if project_dir not in sys.path:
#     sys.path.insert(0, project_dir)
