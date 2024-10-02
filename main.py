import os
import os.path
import json
from convert.convert_c import parse_species_data_file, parse_egg_moves_file, parse_tm_tutor_file
from convert.convert_string import convert_string_file
from convert.convert_txt import build_compatibility_table

root_dir = os.path.dirname(__file__)
src_dir = os.path.join(root_dir, "c")
dst_dir = os.path.join(root_dir, "json")

# Example usage
base_stats = os.path.join(src_dir, "src/Base_Stats.c")
egg_moves = os.path.join(src_dir, "src/Egg_Moves.c")
pokedex_blurbs = os.path.join(src_dir, "strings/Pokedex_Data.string")
pokedex_names = os.path.join(src_dir, "strings/Pokemon_Name_Table.string")
tm_list = os.path.join(src_dir, "src/TM_Tutor_Tables.c")
tm_compatibilities = os.path.join(src_dir, "src/tm_compatibility")
tutor_compatibilities = os.path.join(src_dir, "src/tutor_compatibility")
pokedex_file = os.path.join(dst_dir, "pokedex.json")
move_file = os.path.join(dst_dir, "moves.json")

species_data = parse_species_data_file(base_stats)
egg_moves_data = parse_egg_moves_file(egg_moves)
blurbs_data = convert_string_file(pokedex_blurbs)
names_data = convert_string_file(pokedex_names)
tm_list_data = parse_tm_tutor_file(tm_list)


def merge_data(species_data, data, key):
    """Merge species data and egg moves into a single data structure."""
    for species, value in data.items():
        if species in species_data:
            species_data[species][key] = value
        else:
            # print(f"{species} in {key} not found in species_data")
            pass

merge_data(species_data, egg_moves_data, "egg_moves")
merge_data(species_data, blurbs_data, "blurb")
merge_data(species_data, names_data, "name")

# Output the merged data to a JSON file
with open(pokedex_file, 'w') as json_file:
    json.dump(species_data, json_file, indent=4)
print(f"Pokedex data successfully parsed and saved to {pokedex_file}")

tm_list_data["tm"] = tm_list_data["tm"] | build_compatibility_table(tm_compatibilities)
tm_list_data["tutor"] = tm_list_data["tutor"] | build_compatibility_table(tutor_compatibilities)

# Output the merged data to a JSON file
with open(move_file, 'w') as json_file:
    json.dump(tm_list_data, json_file, indent=4)
print(f"TM/Tutor data successfully parsed and saved to {move_file}")
