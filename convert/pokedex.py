import re
import os
from convert import c_dir
from convert.error import report_error

base_stats = os.path.join(c_dir, "src/Base_Stats.c")
egg_moves = os.path.join(c_dir, "src/Egg_Moves.c")
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
