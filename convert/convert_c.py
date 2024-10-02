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
