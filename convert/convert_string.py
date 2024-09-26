import re
import json


def convert_string_file(file_path, output_json):
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
                current_text.append(line)

        # Save the last entry
        if current_entry:
            data[current_entry] = " ".join(current_text).replace("\\n", " ").replace("Pok\\emon", "Pokémon")

    # Write the JSON output
    with open(output_json, 'w') as json_file:
        json.dump(data, json_file, indent=4)
