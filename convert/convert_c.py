import re
import json


def convert_c_file(file_path, output_json):
    # Regex patterns for parsing different attributes
    species_pattern = re.compile(r"\[SPECIES_(\w+)\]")
    attributes_pattern = re.compile(r"\.(\w+)\s*=\s*(.*),")

    data = {}

    with open(file_path, 'r') as file:
        current_species = None
        current_entry = {}

        for line in file:
            species_match = species_pattern.search(line)
            attribute_match = attributes_pattern.search(line)

            # Check if the line defines a new species
            if species_match:
                if current_species:  # If we were already processing a species, save the last one
                    data[current_species] = current_entry
                current_species = species_match.group(1)
                current_entry = {}

            # Check if the line has an attribute (key-value pair)
            if attribute_match:
                key = attribute_match.group(1)
                value = attribute_match.group(2).strip()

                # Try to clean up value
                if value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():  # Handle float values if any
                    value = float(value)
                elif value == "TRUE":
                    value = True
                elif value == "FALSE":
                    value = False
                elif value.startswith("PERCENT_FEMALE"):
                    value = float(re.search(r"\(([\d.]+)\)", value).group(1)) / 100
                elif value.startswith("TYPE_") or value.startswith("ABILITY_") or value.startswith(
                        "ITEM_") or value.startswith("GROWTH_") or value.startswith("EGG_GROUP_"):
                    value = value.replace("TYPE_", "").replace("ABILITY_", "").replace("ITEM_", "").replace("GROWTH_",
                                                                                                            "").replace(
                        "EGG_GROUP_", "")

                current_entry[key] = value

        # Save the last species
        if current_species:
            data[current_species] = current_entry

    # Write the JSON output
    with open(output_json, 'w') as json_file:
        json.dump(data, json_file, indent=4)
