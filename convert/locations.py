import os
import re
from convert import csv_dir

level_re = re.compile(".*[0-9]F.*")
grass_encounters_file = "Pokémon Unbound Location Guide v2.1.1.1 - Grass & Cave Encounters.csv"
water_encounters_file = "Pokémon Unbound Location Guide v2.1.1.1 - Surfing, Fishing, Rock Smash.csv"


def parse_encounters_csv(csv_file, skip_lines=0):
    with open(csv_file, 'r') as f:
        raw_data = {}
        skip_index = 0
        for line in f.readlines():
            if skip_index < skip_lines:
                skip_index += 1
                continue
            values = line.split(",,")
            if not raw_data:
                raw_data = {header.strip(): [] for header in values}
                continue

            for header, value in zip(raw_data, values):
                raw_data[header].append(value)
    return raw_data


def check_area(value):
    if value in ["Inside", "Outside"]:
        return True
    if "Area" in value:
        return True
    if "Flowers" in value:
        return True
    if level_re.match(value):
        return True
    if value == "Shadow Basement":
        return True
    if ", " in value:
        return True
    if "Headbutt" in value:
        return True
    if value in ["Swarm", "Special Encounter"]:
        return True
    if value in ["Easy", "Medium", "Hard", "Insane"]:
        return True
    return False


def parse_land_columns(raw_data):
    data = {}
    for header in raw_data:
        data[header] = {}
        data[header]["land"] = {}
        column = raw_data[header]
        sub_header = ""
        sub_column = []
        for value in column:
            value = value.strip()
            if check_area(value):
                data[header]["land"][sub_header] = sub_column
                sub_header = value
                sub_column = []
                continue
            if value:
                sub_column.append(value)
        data[header]["land"][sub_header] = sub_column
    return data


def parse_water_columns(raw_data):
    data = {}
    for header in raw_data:
        data[header] = {}
        sheet = "surf"
        data[header][sheet] = {}
        column = raw_data[header]
        sub_header = ""
        sub_column = []
        for value in column:
            value = value.strip()
            if check_area(value):
                if sub_column:
                    data[header][sheet][sub_header] = sub_column
                sub_header = value
                sub_column = []
                continue
            if "Rod" in value or value == "Fishing" or value == "Rock Smash":
                if sub_column:
                    data[header][sheet][sub_header] = sub_column
                sheet = value
                data[header][sheet] = {}
                sub_header = ""
                sub_column = []
                continue
            if value and value != "X":
                sub_column.append(value)
        data[header][sheet][sub_header] = sub_column
    return data


def parse_location_files():
    land_data = parse_land_columns(
        parse_encounters_csv(os.path.join(csv_dir, grass_encounters_file)),
    )
    water_data = parse_water_columns(
        parse_encounters_csv(os.path.join(csv_dir, water_encounters_file),
                             skip_lines=2),
    )
    for route in land_data:
        if route in water_data:
            for key in water_data[route]:
                land_data[route][key] = water_data[route][key]
    return land_data


def create_location_lookup(location_data):
    location_lookup = {}
    for route, route_entry in location_data.items():
        for method, method_entry in route_entry.items():
            for area, area_entry in method_entry.items():
                for species in area_entry:
                    try:
                        encounters = location_lookup[species]
                    except KeyError:
                        encounters = []
                        location_lookup[species] = encounters
                    encounters.append({"route": route, "area": area, "method": method})
    return location_lookup


def update_pokemon_names(location_data, pokedex):
    name_lookup = {entry["name"]: key for key, entry in pokedex.items() if "name" in entry}
    for route, route_entry in location_data.items():
        for method, method_entry in route_entry.items():
            for area, area_entry in method_entry.items():
                location_data[route][method][area] = [
                    name_lookup.get(species, species) for species in area_entry
                ]


if __name__ == "__main__":
    from convert import pprint_top_entries

    location_data = parse_location_files()
    location_lookup = create_location_lookup(location_data)
    pprint_top_entries(location_lookup)
