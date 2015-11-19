import os
import config

# 0 = Command IDs start
# 1 = Command IDs end
# 2 = Serial Globals start
# 3 = Serial Globals end
# 4 = Auto Globals start
# 5 = Auto Globals end
# 6 = Auto Setup start
# 7 = Auto Setup end
# 8 = Auto Loop start
# 9 = Auto Loop end

markers = [
    "/* ---------------- Includes start ------------------ */\n"
    "/*                                                    */",

    "/*                                                    */\n"
    "/* ----------------- Includes end ------------------- */",

    "/* -------------- Command IDs start ----------------- */\n"
    "/*                                                    */",

    "/*                                                    */\n"
    "/* --------------- Command IDs end ------------------ */",

    "/* -------------- Serial Globals start -------------- */\n"
    "/*                                                    */",

    "/*                                                    */\n"
    "/* --------------- Serial Globals end --------------- */",

    "/* --------------- Auto Globals start --------------- */\n"
    "/*                                                    */",

    "/*                                                    */\n"
    "/* ---------------- Auto Globals end ---------------- */",

    "/* ---------------- Auto Setup start ---------------- */\n"
    "/*                                                    */",

    "/*                                                    */\n"
    "/* ----------------- Auto Setup end ----------------- */",

    "/* ----------------- Auto Loop start ---------------- */\n"
    "/*                                                    */",

    "/*                                                    */\n"
    "/* ------------------ Auto Loop end ----------------- */",

    "/* ------------------- Serial start ----------------- */\n"
    "/*                                                    */",

    "/*                                                    */\n"
    "/* -------------------- Serial end ------------------ */"
]

includes_marker = "/* -------------------- Includes -------------------- */\n"
globals_marker = "/* -------------------- Globals --------------------- */\n"
setup_marker = "/* --------------------- Setup ---------------------- */\n"
loop_marker = "/* ---------------------- Loop ---------------------- */\n"
serial_marker = "/* --------------------- Serial --------------------- */\n"


def insert_tabs(text, num_tabs=1):
    new_text = ""
    for line in text.split("\n"):
        new_text += "    " * num_tabs + line + "\n"
    return new_text


def get_file_contents(arduino_objects, arduino_dir):
    # The file contents to be inserted
    # 0 = includes
    # 1 = globals
    # 2 = setup
    # 3 = loop
    # 4 = when serial packet received
    # SerialPacket.h should always be included
    file_contents_list = ["#include <SerialPacket.h>\n", [], [], [], []]
    file_names = []
    for file_name in os.listdir(arduino_dir + "/code_templates"):
        if file_name[-3:] == "ino" and (file_name[:-4] in arduino_objects):
            # Open code template file
            with open(arduino_dir + "/code_templates/" + file_name,
                      'r') as file_ref:
                file_contents = file_ref.read()

            # Find includes section
            includes_index_start = file_contents.find(includes_marker)
            includes_index_end = includes_index_start + len(includes_marker)

            # Find globals section
            globals_index_start = file_contents.find(globals_marker,
                                                     includes_index_end)
            globals_index_end = globals_index_start + len(globals_marker)

            # Find setup section
            setup_index_start = file_contents.find(setup_marker,
                                                   globals_index_end)
            setup_index_end = setup_index_start + len(setup_marker)

            # Find loop section
            loop_index_start = file_contents.find(loop_marker, setup_index_end)
            loop_index_end = loop_index_start + len(loop_marker)

            # Find serial section
            serial_index_start = file_contents.find(serial_marker,
                                                    loop_index_end)
            serial_index_end = serial_index_start + len(serial_marker)

            # Extract file contents
            file_includes = \
                file_contents[includes_index_end: globals_index_start]
            file_globals = file_contents[globals_index_end: setup_index_start]
            file_setup = file_contents[setup_index_end: loop_index_start]
            file_loop = file_contents[loop_index_end:serial_index_start]
            file_serial = file_contents[serial_index_end:]

            # strip trailing newlines
            file_includes = file_includes.strip("\n")
            file_globals = file_globals.strip("\n")
            file_setup = file_setup.strip("\n")
            file_loop = file_loop.strip("\n")
            file_serial = file_serial.strip("\n")

            # add contents to list
            if file_includes not in file_contents_list[0]:
                file_contents_list[0] += file_includes + "\n"  # includes
            file_contents_list[1].append(file_globals)  # globals
            file_contents_list[2].append(insert_tabs(file_setup))  # setup
            file_contents_list[3].append(insert_tabs(file_loop))  # loop
            file_contents_list[4].append(insert_tabs(file_serial, 3))  # serial

            file_names.append(file_name[:-4])

    return file_contents_list, file_names


def generate_file(serial_file_name, arduino_objects, baud=115200, node=2):
    arduino_dir = config.get_arduino_dir(serial_file_name)

    with open(arduino_dir + serial_file_name, 'r') as serial_box_file:
        contents = serial_box_file.read()  # load file to modify

    marker_indices = [0]

    for marker in markers:  # find each marker in the file to modify
        if "end" in marker:
            marker_indices.append(contents.find(marker, marker_indices[-1]))
        else:
            marker_indices.append(
                contents.find(marker, marker_indices[-1]) + len(marker))
        if marker_indices[-1] == -1:
            raise Exception("Marker not found: " + marker +
                            "\nPlease add to file")

    marker_indices.append(len(contents))  # Index of end of file

    # extract the contents to fill the file with
    file_contents_list, file_names = get_file_contents(arduino_objects,
                                                       arduino_dir)

    # start new contents with whatever comes before the first marker
    new_contents = [contents[marker_indices[0]: marker_indices[1]]]

    # Insert includes into file
    new_contents.append(file_contents_list[0])

    new_contents.append(markers[1] + "\n")
    new_contents.append(markers[2])

    # Insert command ids and serial globals into file
    for index in xrange(len(arduino_objects)):
        if index < 0x10:
            value = "0x0" + hex(index)[2:]
        else:
            value = hex(index)[0:2]
        new_contents.append(
            "#define " + arduino_objects[index] + "_ID " + value)
    new_contents.append(markers[3] + "\n")
    new_contents.append(markers[4])
    new_contents.append("SerialPacket Packet;\n")
    new_contents.append("const int baud = " + str(baud) + ";")
    new_contents.append("const int node = " + str(node) + ";\n")
    new_contents.append("int payload = 0;")
    new_contents.append("int command_id = 0;")

    # Insert new contents from each section into file
    contents_index = 6
    file_names_index = 0
    for index in xrange(1, len(file_contents_list)):
        if index == 1:
            section = "globals"
        elif index == 2:
            section = "setup"
        elif index == 3:
            section = "loop"
        else:
            section = "serial"
        new_contents.append(contents[
                            marker_indices[contents_index]:marker_indices[
                                contents_index + 1]])
        for file_content in file_contents_list[index]:
            if len(file_content.replace("\n", "").replace(" ", "")) > 0:
                new_contents.append("    " * (index - 1) + "\n/* ----- " +
                                    file_names[file_names_index] + " " +
                                    section + " ----- */")
                if section == "serial":
                    new_contents.append(
                        "    " * (index - 2) + "if (command_id == " +
                        file_names[file_names_index] + "_ID)\n" +
                        "    " * (index - 2) + "{")
                new_contents.append(file_content)

                if section == "serial":
                    new_contents.append("    " * (index - 2) + "}\n")

            file_names_index += 1
        file_names_index = 0

        contents_index += 2

    new_contents.append(contents[
                        marker_indices[contents_index]:marker_indices[
                            contents_index + 1]])

    with open(arduino_dir + serial_file_name, 'w') as serial_box_file:
        serial_box_file.write("\n".join(new_contents))
