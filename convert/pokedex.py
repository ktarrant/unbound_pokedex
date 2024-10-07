import re
import os
from convert import c_dir

base_stats = os.path.join(c_dir, "src/Base_Stats.c")
egg_moves = os.path.join(c_dir, "src/Egg_Moves.c")
pokedex_blurbs = os.path.join(c_dir, "strings/Pokedex_Data.string")
pokedex_names = os.path.join(c_dir, "strings/Pokemon_Name_Table.string")
evolutions_file = os.path.join(c_dir, "src/Evolution Table.c")


def parse_base_stats():
    """Parse species data from the given file and return as a dictionary."""
    parsed_data = {}
    species_regex = re.compile(r'\[SPECIES_(\w+)\]')
    attribute_regex = re.compile(r'\.(\w+)\s*=\s*(.+),')

    current_species = None

    with open(base_stats, 'r') as file:
        for line in file:
            line = line.strip()

            # Match the species identifier (e.g., [SPECIES_BULBASAUR])
            species_match = species_regex.match(line)
            if species_match:
                current_species = species_match.group(1).replace("SPECIES_", "")
                parsed_data[current_species] = {}
                continue

            # Match attribute lines (e.g., .baseHP = 45,)
            attribute_match = attribute_regex.match(line)
            if attribute_match and current_species:
                key = attribute_match.group(1)
                value = attribute_match.group(2)

                # Handle specific data types
                if value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
                elif 'PERCENT_FEMALE' in value:
                    # Extract percentage from PERCENT_FEMALE(x)
                    value = float(re.findall(r'\d+\.?\d*', value)[0])
                elif value.startswith('TRUE'):
                    value = True
                elif value.startswith('FALSE'):
                    value = False
                elif value.startswith('ABILITY_') or value.startswith('TYPE_') or value.startswith('ITEM_') or value.startswith('EGG_GROUP_'):
                    value = value  # Leave string as is

                parsed_data[current_species][key] = value

    return parsed_data


def get_relatives(species, pokedex):
    species_basename = species.split("_")[0]
    relatives = [relative for relative in pokedex if species_basename in relative]
    return relatives


def parse_egg_moves():
    """Parse egg moves data from the given file and return as a dictionary."""
    egg_moves_data = {}
    start_parsing = False
    current_species = None
    current_moves = []

    with open(egg_moves, 'r') as file:
        for line in file:
            line = line.strip()

            # Skip until we reach the start of the egg moves list
            if not start_parsing:
                if line.startswith('const u16 gEggMoves[] ='):
                    start_parsing = True
                continue

            # Stop if we reach the end of the egg moves list
            if line.startswith('EGG_MOVES_TERMINATOR') or line.startswith('};'):
                break

            # Handle the start of an egg_moves block
            if line.startswith('egg_moves('):
                # Extract the species name
                match = re.match(r'egg_moves\((\w+),', line)
                if match:
                    current_species = match.group(1)
                    current_moves = []
                else:
                    continue

            # Continue collecting moves for the current species
            elif current_species and line.endswith('),'):
                # If it's the closing line of the block, collect the remaining moves and save the entry
                moves = line.replace('),', '').split(',')
                current_moves.extend([move.strip() for move in moves if move.strip()])
                egg_moves_data[current_species] = current_moves
                current_species = None  # Reset species to handle the next one
            elif current_species:
                # Collect moves across multiple lines
                moves = line.split(',')
                current_moves.extend([move.strip() for move in moves if move.strip()])

    return egg_moves_data


def parse_evolutions():
    """Parse the evolution data from the file and return it as a dictionary."""
    evolution_data = {}

    # Regex to match each species entry and extract the evolution details
    species_pattern = re.compile(r'\[SPECIES_(\w+)\]\s*=\s*\{(.+?})},', re.MULTILINE)
    evolution_pattern = re.compile(r'\{\s*(\w+),\s*([^,]+),\s*(SPECIES_\w+),\s*([^}]+)\s*}', re.MULTILINE)

    with open(evolutions_file, 'r') as file:
        file_content = file.read()

        # Iterate through each species block
        for species_match in species_pattern.finditer(file_content):
            species_name = species_match.group(1)  # e.g., BULBASAUR
            evolutions = species_match.group(2).strip()

            # Parse the evolution details for this species
            evolutions_list = []
            for evolution_match in evolution_pattern.finditer(evolutions):
                method = evolution_match.group(1)  # e.g., EVO_LEVEL
                condition = evolution_match.group(2)  # e.g., 16 or ITEM_THUNDER_STONE
                target_species = evolution_match.group(3)  # e.g., SPECIES_IVYSAUR
                extra = evolution_match.group(4).strip()  # e.g., 0 or MEGA_VARIANT_STANDARD

                # Store the evolution details as a dictionary
                evolutions_list.append({
                    "method": method,
                    "condition": condition,
                    "target": target_species.replace('SPECIES_', ''),  # Remove SPECIES_ prefix
                    "extra": extra
                })

            # Store this species' evolution data
            evolution_data[species_name] = evolutions_list

    return evolution_data


def convert_string_file(file_path):
    # Regex patterns to match dex and name entries
    dex_entry_pattern = re.compile(r"#org @DEX_ENTRY_(\w+)")
    name_entry_pattern = re.compile(r"#org @NAME_(\w+)")
    # Regex pattern to match settings (ignore these)
    setting_pattern = re.compile(r"(\w+)\s*=\s*(.*)")

    data = {}
    current_entry = None
    current_text = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            # Match DEX entries
            dex_entry_match = dex_entry_pattern.match(line)
            if dex_entry_match:
                if current_entry:  # Save the previous entry before starting a new one
                    data[current_entry] = " ".join(current_text).replace("\\n", " ").replace("Pok\\emon", "Pokémon")
                # Remove DEX_ENTRY_ prefix from the key
                current_entry = dex_entry_match.group(1)
                current_text = []
                continue  # Skip to the next line

            # Match NAME entries
            name_entry_match = name_entry_pattern.match(line)
            if name_entry_match:
                if current_entry:  # Save the previous entry before starting a new one
                    data[current_entry] = " ".join(current_text).replace("\\n", " ").replace("Pok\\emon", "Pokémon")
                # Remove NAME_ prefix from the key
                current_entry = name_entry_match.group(1)
                current_text = []
                continue  # Skip to the next line

            # Ignore setting entries like MAX_LENGTH=10 or FILL_FF=True
            setting_match = setting_pattern.match(line)
            if setting_match:
                continue  # Simply skip settings lines

            # Add text to current entry
            if current_entry and line:  # Only add non-empty lines
                current_text.append(line.strip(" \t\u2642\u2640\ufe0f").replace("\e", "e"))

        # Save the last entry
        if current_entry:
            data[current_entry] = " ".join(current_text).replace("\\n", " ").replace("Pok\\emon", "Pokémon")

    return data


def merge_data(pokedex, data, key):
    """Merge species data and egg moves into a single data structure."""
    for species, value in data.items():
        if species in pokedex:
            pokedex[species][key] = value
        else:
            relatives = get_relatives(species, pokedex)
            for suffix_len in [-1, -2, -3]:
                relatives += get_relatives(species[:suffix_len], pokedex)
            for prefix_len in [1]:
                relatives += get_relatives(species[prefix_len:], pokedex)
            if relatives:
                for relative in relatives:
                    if key not in pokedex[relative]:
                        pokedex[relative][key] = value
                continue
            else:
                print(f"{species} in {key} not found in pokedex")


def create_evolves_from(pokedex):
    # We want to create a back-reference for the evolution, i.e. evolve_from
    for species, entry in pokedex.items():
        for from_species, from_entry in pokedex.items():
            from_evos = [from_species for from_evo in from_entry.get("evolve_to", [])
                         if from_evo["target"] == species]
            entry["evolve_from"] = entry.get("evolve_from", []) + from_evos


def build_pokedex():
    pokedex = parse_base_stats()
    egg_moves = parse_egg_moves()
    evolutions = parse_evolutions()
    blurbs_data = convert_string_file(pokedex_blurbs)
    names_data = convert_string_file(pokedex_names)

    merge_data(pokedex, egg_moves, "egg_moves")
    merge_data(pokedex, evolutions, "evolve_to")
    merge_data(pokedex, blurbs_data, "blurb")
    merge_data(pokedex, names_data, "name")
    create_evolves_from(pokedex)
    return pokedex


def add_compatible_moves(pokedex, move_data):
    for species in pokedex:
        # add compatibility tables
        for category in ["tm", "tutor"]:
            move_list = []
            for move_num, entry in move_data[category].items():
                if species in entry["compatibility"]:
                    move_list.append(entry["key"])

            if move_list:
                pokedex[species][category] = move_list


def propagate_learnset(pokedex, learnset_key="learnset"):
    # If there is a MEGA or other alternate version of a Pokemon,
    # its will have the learnset and the regular one will not.
    for species, entry in pokedex.items():
        if learnset_key not in entry or not entry[learnset_key]:
            relatives = get_relatives(species, pokedex)
            for relative in relatives:
                if learnset_key in pokedex[relative]:
                    pokedex[species][learnset_key] = pokedex[relative][learnset_key]


if __name__ == "__main__":
    from convert import pprint_top_entries

    pokedex = build_pokedex()

    pprint_top_entries(pokedex)
