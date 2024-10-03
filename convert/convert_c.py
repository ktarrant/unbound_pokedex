import re
import json


def parse_species_data_file(species_file):
    """Parse species data from the given file and return as a dictionary."""
    parsed_data = {}
    species_regex = re.compile(r'\[SPECIES_(\w+)\]')
    attribute_regex = re.compile(r'\.(\w+)\s*=\s*(.+),')

    current_species = None

    with open(species_file, 'r') as file:
        for line in file:
            line = line.strip()

            # Match the species identifier (e.g., [SPECIES_BULBASAUR])
            species_match = species_regex.match(line)
            if species_match:
                current_species = species_match.group(1)
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


def parse_egg_moves_file(egg_moves_file):
    """Parse egg moves data from the given file and return as a dictionary."""
    egg_moves_data = {}
    start_parsing = False
    current_species = None
    current_moves = []

    with open(egg_moves_file, 'r') as file:
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


def parse_tm_tutor_file(tm_tutor_file):
    # Regex to match and capture the MOVE_ value and the number after the //
    pattern = r'(MOVE_\w+),\s*//(\d+)'

    with open(tm_tutor_file) as file:
        data = {}
        category = None
        for line in file.readlines():
            if "gTMHMMoves" in line:
                category = "tm"
                data[category] = {}
                continue

            if "gMoveTutorMoves" in line:
                category = "tutor"
                data[category] = {}
                continue

            if category:
                # Use re.search to find the match
                match = re.search(pattern, line)

                if match:
                    move_value = match.group(1)  # MOVE_ value
                    number_value = match.group(2)  # Number after the //
                    data[category][int(number_value)] = {"key": move_value}

        return data


def parse_level_up_moves(file_name):
    """Parse the level up moves from the file and return a dictionary of learnset names to move data."""
    level_up_moves_data = {}
    current_learnset_name = None
    current_moveset = []
    species_map = {}

    with open(file_name, 'r') as file:
        start_collecting = False
        for line in file:
            line = line.strip()

            # Match the start of a Pokémon's level-up learnset
            pokemon_match = re.match(r'static const struct LevelUpMove s(\w+)LevelUpLearnset\[\] = {', line)
            if pokemon_match:
                current_learnset_name = f's{pokemon_match.group(1)}LevelUpLearnset'
                current_moveset = []
                continue

            # Match the LEVEL_UP_MOVE entries
            move_match = re.match(r'LEVEL_UP_MOVE\(\s*(\d+),\s*(MOVE_\w+)\s*\)', line)
            if move_match:
                level = int(move_match.group(1))
                move = move_match.group(2)
                current_moveset.append({"level": level, "move": move})
                continue

            # Match the LEVEL_UP_END entry (end of the learnset)
            if line == 'LEVEL_UP_END':
                if current_learnset_name:
                    level_up_moves_data[current_learnset_name] = current_moveset
                current_learnset_name = None
                current_moveset = []
                continue

            # Start collecting species map after the correct declaration
            if line.startswith('const struct LevelUpMove* const gLevelUpLearnsets'):
                start_collecting = True
                continue

            if not start_collecting:
                continue

            # Match the SPECIES_ lines
            species_match = re.match(r'\[SPECIES_(\w+)\] = (\w+),', line)
            if species_match:
                species_name = species_match.group(1)  # e.g., BULBASAUR
                learnset_name = species_match.group(2)  # e.g., sBulbasaurLevelUpLearnset
                species_map[learnset_name] = species_name

    final_data = {}
    for learnset_name, species_name in species_map.items():
        if learnset_name in level_up_moves_data:
            final_data[species_name] = level_up_moves_data[learnset_name]

    return final_data

# Example usage:
# moves_data = parse_level_up_moves('level_up_moves.txt')
# species_map = parse_species_map('level_up_moves.txt')
# merge_data_and_save_to_json(moves_data, species_map, 'level_up_moves_output.json')
