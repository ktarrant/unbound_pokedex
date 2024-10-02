import os


def convert_txt_file(file_path):
    data = {}
    with open(file_path, 'r') as file:
        for line in file.readlines():
            line = line.strip()
            if not data:
                _, name = line.split(": ")
                data["name"] = name
                data["compatibility"] = []
                continue

            if line:
                data["compatibility"].append(line)

    return data


def build_compatibility_table(move_dir):
    data = {}
    for root, dirs, files in os.walk(move_dir):
        for file in files:
            if file.endswith(".txt"):
                move_num = int(file.split(" - ")[0])
                data[move_num] = convert_txt_file(os.path.join(root, file))
    return data
