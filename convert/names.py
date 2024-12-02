import re
import os

from convert import c_dir

species_map_table = os.path.join(c_dir, "src/Species_To_Pokdex_Table.c")
pokedex_blurbs = os.path.join(c_dir, "strings/Pokedex_Data.string")
pokedex_names = os.path.join(c_dir, "strings/Pokemon_Name_Table.string")

species_map_line = re.compile(r'\[(SPECIES_[\w]+(?:_\w+)?)\s*-\s*1\]\s*=\s*(NATIONAL_DEX_[\w]+),')
name_line = re.compile(r'#org\s*(@NAME_\w+)\n(.*)')
blurb_line = re.compile(r'#org\s*(@DEX_ENTRY_\w+)\n((?:.*\n)*?.*)', re.MULTILINE)


suffixes = [

]

def name_mapper(pokedex_name):
    if pokedex_name == "HO_OH": return "HOOH"
    if pokedex_name == "BURMY_SANDY": return "BURMYS"
    if pokedex_name == "WORMADAM_SANDY": return "WORMADAM_S"
    if pokedex_name == "BURMY_TRASH": return "BURMYT"
    if pokedex_name == "WORMADAM_TRASH": return "WORMADAM_T"
    if pokedex_name == "NIDORAN_F": return "NIDORANF"
    if pokedex_name == "NIDORAN_M": return "NIDORANM"
    if pokedex_name.startswith("BASCULIN"):
        return "BASCULIN" + pokedex_name.split("_")[-1][0]
    if pokedex_name == "ARCEUS": return "ARCEUS"
    if pokedex_name == "SAWSBUCK": return "SAWSBUCKS"
    if pokedex_name in ["UNFEZANT_F", "FRILLISH_F"]:
        return pokedex_name
    if pokedex_name.endswith("_G"):
        return pokedex_name
    if "ROTOM" in pokedex_name:
        rsplit = list(pokedex_name.split("_"))
        if len(rsplit) == 1:
            return pokedex_name
        else:
            rsplit[1] = rsplit[1].replace("FROST", "FROS")
            return "".join(rsplit)
    if "_MEGA" in pokedex_name:
        pokedex_name = "M" + pokedex_name.replace("_MEGA", "")
    if pokedex_name.endswith("_A"):
        pokedex_name = "A" + pokedex_name[:-2]
    for suffix in [
            "_EAST", "_ORIGIN", "_SKY",
            "_SUMMER", "_AUTUMN", "_WINTER"]:
        if pokedex_name.endswith(suffix):
            pokedex_name = pokedex_name.replace(suffix, suffix[1])
    if pokedex_name[-2] == "_":
        pokedex_name = pokedex_name[:-2] + pokedex_name[-1]
    return pokedex_name


def get_species_mapping():
    # Regex pattern to match the specific line format
    entries = {}
    with open(species_map_table, "r") as file:
        for line in file:
            # Find all matches and create a dictionary
            match = species_map_line.match(line.strip())
            if match:
                entries[match.group(1)] = match.group(2)
    return entries


def get_pokedex_outline():
    mapping = get_species_mapping()
    outline = {}
    for species_key, dex_key in mapping.items():
        species = species_key.replace("SPECIES_", "")
        dex = dex_key.replace("NATIONAL_DEX_", "")
        if dex in outline:
            outline[dex][species] = {}
        else:
            outline[dex] = {species: {}}
    return outline


def parse_names():
    # Regex pattern to match Pokédex entries
    with open(pokedex_names, "r") as file:
        matches = name_line.findall(file.read())
    entries = {key.replace("@NAME_", ""): value
               for key, value in matches}
    return entries


def parse_blurbs():
    # Regex pattern to match Pokédex entries
    with open(pokedex_blurbs, "r") as file:
        matches = blurb_line.findall(file.read())
    entries = {key.replace("@DEX_ENTRY_", ""): value.replace('\\n', ' ')
               for key, value in matches}
    return entries


if __name__ == "__main__":
    import pprint
    pprint.pprint(parse_names())
    pprint.pprint(parse_blurbs())
    pprint.pprint(get_pokedex_outline())
