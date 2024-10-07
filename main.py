import os.path
import json
from convert import dst_dir
from convert.moves import (
    parse_tm_tutor_file,
    parse_learnsets,
    add_compatibilities,
    add_learned_moves,
)
from convert.locations import (
    parse_location_files,
    create_location_lookup,
    update_pokemon_names,
)
from convert.pokedex import (
    build_pokedex,
    merge_data,
    propagate_learnset,
    add_compatible_moves,
)
from convert.collect_fields import collect_field_types

# Collect Moves Data
move_data = parse_tm_tutor_file()
learnsets_data = parse_learnsets()
add_compatibilities(move_data)
add_learned_moves(move_data, learnsets_data)

# Collect Pokedex Data
pokedex = build_pokedex()
propagate_learnset(pokedex)

# Collect and merge location data
location_data = parse_location_files()
update_pokemon_names(location_data, pokedex)
location_lookup = create_location_lookup(location_data)
merge_data(pokedex, location_lookup, "location")

# Add learnsets and TM/Tutors to Pokedex
merge_data(pokedex, learnsets_data, "learnset")
add_compatible_moves(pokedex, move_data)
propagate_learnset(pokedex, "learnset")
propagate_learnset(pokedex, "tm")
propagate_learnset(pokedex, "tutor")

# Create output files
pokedex_dir = os.path.join(dst_dir, "pokedex")
move_file = os.path.join(dst_dir, "moves.json")
fields_file = os.path.join(dst_dir, "fields.json")
locations_file = os.path.join(dst_dir, "locations.json")

with open(locations_file, 'w') as json_file:
    json.dump(location_data, json_file, indent=1)
print(f"Locations data successfully parsed and saved to {locations_file}")

with open(move_file, 'w') as json_file:
    json.dump(move_data, json_file, indent=1)
print(f"Move data successfully parsed and saved to {move_file}")

fields_data = collect_field_types(pokedex)
with open(fields_file, 'w') as json_file:
    json.dump(fields_data, json_file, indent=1)
print(f"Fields data successfully parsed and saved to {fields_file}")

# Output each species Pokedex entry to a separate JSON file
for species in pokedex:
    out_file = os.path.join(pokedex_dir, species + ".json")

    # Output the merged data to a JSON file
    with open(out_file, 'w') as json_file:
        json.dump(pokedex[species], json_file, indent=4)
        print(f"Saving pokedex data: {out_file}")
