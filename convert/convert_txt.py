import json


def convert_txt_file(file_path, output_json):
    data = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            if not data:
                data["name"] = line
                data["compatibility"] = []

            else:
                data["compatibility"].append(line)

    # Write the JSON output
    with open(output_json, 'w') as json_file:
        json.dump(data, json_file, indent=4)
