import os

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
    "/* ------------------ Auto Loop end ----------------- */"
]

globals_marker = "/* -------------------- Globals --------------------- */\n"
setup_marker = "/* --------------------- Setup ---------------------- */\n"
loop_marker = "/* ---------------------- Loop ---------------------- */\n"


def read_arduino_file():
    project_dir = os.path.dirname(os.path.realpath(__file__))

    with open(project_dir + "/SerialBox.ino", 'r') as serial_box_file:
        return serial_box_file.read()

def insert_tabs(text, num_tabs=1):
    new_text = ""
    for line in text.split("\n"):
        new_text += "\t" * num_tabs + line + "\n"
    return new_text

def get_file_contents():
    file_contents_list = [[], [], []]
    file_names = []

    for file_name in os.listdir("code_templates"):
        if file_name[-3:] == "ino":
            with open("code_templates/" + file_name, 'r') as file_ref:
                file_contents = file_ref.read()
            globals_index_start = file_contents.find(globals_marker)
            globals_index_end = globals_index_start + len(globals_marker)

            setup_index_start = file_contents.find(setup_marker,
                                                   globals_index_end)
            setup_index_end = setup_index_start + len(setup_marker)

            loop_index_start = file_contents.find(loop_marker, setup_index_end)
            loop_index_end = loop_index_start + len(loop_marker)

            file_globals = file_contents[globals_index_end: setup_index_start]
            file_setup = file_contents[setup_index_end: loop_index_start]
            file_loop = file_contents[loop_index_end:]

            file_contents_list[0].append(file_globals)  # globals
            file_contents_list[1].append(insert_tabs(file_setup))  # setup
            file_contents_list[2].append(insert_tabs(file_loop, 2))  # loop

            file_names.append(file_name[:-4])

    return file_contents_list, file_names


def generate_file(baud=115200, node=2):
    contents = read_arduino_file()

    marker_indices = [0]

    for marker in markers:
        if "end" in marker:
            marker_indices.append(contents.find(marker, marker_indices[-1]))
        else:
            marker_indices.append(
                contents.find(marker, marker_indices[-1]) + len(marker))
    marker_indices.append(len(contents))

    print(marker_indices)
    print(len(marker_indices))
    print(os.listdir("code_templates"))

    file_contents_list, file_names = get_file_contents()

    new_contents = [
        contents[marker_indices[0]:  marker_indices[1]]]

    for index in xrange(len(file_names)):
        if index < 0x10:
            value = "0x0" + hex(index)[2:]
        else:
            value = hex(index)[0:2]
        new_contents.append("#define " + file_names[index] + "_ID " + value)
    new_contents.append(markers[1] + "\n")
    new_contents.append(markers[2])
    new_contents.append("const int baud = " + str(baud) + ";")
    new_contents.append("const int node = " + str(node) + ";")
    # new_contents.append(markers[3])

    contents_index = 4
    file_names_index = 0

    for index in xrange(len(file_contents_list)):
        if index == 0:
            section = "globals"
            num_tabs = 0
        elif index == 1:
            section = "setup"
            num_tabs = 1
        else:
            section = "loop"
            num_tabs = 2
        new_contents.append(contents[
                            marker_indices[contents_index]:marker_indices[
                                contents_index + 1]])
        for file_content in file_contents_list[index]:
            new_contents.append("\t" * num_tabs + "/* ----- " +
                                file_names[file_names_index] + " " +
                                section + " ----- */")
            new_contents.append(file_content)
            file_names_index += 1
        file_names_index = 0

        contents_index += 2

    new_contents.append(contents[
                        marker_indices[contents_index]:marker_indices[
                            contents_index + 1]])

    with open("SerialBox.ino", 'w') as serial_box_file:
        serial_box_file.write("\n".join(new_contents))


generate_file()
