import os
import re
from convert import c_dir, dst_dir

tm_list = os.path.join(c_dir, "src/TM_Tutor_Tables.c")
tm_compatibilities = os.path.join(c_dir, "src/tm_compatibility")
tutor_compatibilities = os.path.join(c_dir, "src/tutor_compatibility")
learnsets = os.path.join(c_dir, "src/Learnsets.c")


def parse_tm_tutor_file():
    # Regex to match and capture the MOVE_ value and the number after the //
    pattern = r'(MOVE_\w+),\s*//(\d+)'

    with open(tm_list) as file:
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


def parse_learnsets():
    """Parse the level up moves from the file and return a dictionary of learnset names to move data."""
    level_up_moves_data = {}
    current_learnset_name = None
    current_moveset = []
    species_map = {}

    with open(learnsets, 'r') as file:
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


def add_compatibilities(move_data):
    # Merge the compatibility tables into the TM_Tutor base table
    for category, table in [
        ("tm", build_compatibility_table(tm_compatibilities).items()),
        ("tutor", build_compatibility_table(tutor_compatibilities).items()),
    ]:
        for move_num, compatibility in table:
            if move_num in move_data[category]:
                for key in compatibility:
                    move_data[category][move_num][key] = compatibility[key]


def add_learned_moves(move_data, learnsets):
    learned_moves = {}
    for species, entry in learnsets.items():
        for move in entry:
            compatibility = learned_moves.get(move["move"], [])
            compatibility.append({"target": species, "level": move["level"]})
            learned_moves[move["move"]] = compatibility
    move_data["learned"] = learned_moves


if __name__ == "__main__":
    from convert import pprint_top_entries

    move_data = parse_tm_tutor_file()
    learnsets_data = parse_learnsets()
    add_compatibilities(move_data)
    add_learned_moves(move_data, learnsets_data)

    pprint_top_entries(move_data["tm"])
