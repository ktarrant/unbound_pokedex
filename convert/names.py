import re
import os

from convert import c_dir

species_map_table = os.path.join(c_dir, "src/Species_To_Pokdex_Table.c")
pokedex_blurbs = os.path.join(c_dir, "strings/Pokedex_Data.string")
pokedex_names = os.path.join(c_dir, "strings/Pokemon_Name_Table.string")

species_map_line = re.compile(r'\[(SPECIES_[\w]+(?:_\w+)?)\s*-\s*1\]\s*=\s*(NATIONAL_DEX_[\w]+),')
name_line = re.compile(r'#org\s*(@NAME_\w+)\n(.*)')
blurb_line = re.compile(r'#org\s*(@DEX_ENTRY_\w+)\n((?:.*\n)*?.*)', re.MULTILINE)

short_suffixes = [
    "EAST", "ORIGIN", "SKY", "PIROUETTE",
    "RED", "BLUE",
    "SUN", "BLACK", "WHITE", "THERIAN",
    "RESOLUTE",
    "F", "M", "Z",
]
ignore_suffixes = [
    "G", "H"
    "UNFEZANT_F",
    "FRILLISH_F",
]

special_maps = {
    "HO_OH": "HOOH",
    "BURMY_SANDY": "BURMYS",
    "WORMADAM_SANDY": "WORMADAM_S",
    "BURMY_TRASH": "BURMYT",
    "WORMADAM_TRASH": "WORMADAM_T",
    "BURMY": "BURMYP",
    "WORMADAM": "WORMADAM_P",
    "DARMANITANZEN": "ZENITAN",
    "HIPPOPOTAS_F": "HIPPOPOTAF",
    "FLETCHINDER": "FLETCHINDR",
}


def handle_rotom(pokedex_name):
    if "ROTOM" in pokedex_name:
        rsplit = list(pokedex_name.split("_"))
        if len(rsplit) == 1:
            return pokedex_name
        else:
            rsplit[1] = rsplit[1].replace("FROST", "FROS")
            return "".join(rsplit)
    else:
        return pokedex_name


def handle_deerling(pokedex_name):
    if pokedex_name.startswith("DEERLING") or pokedex_name.startswith("SAWSBUCK"):
        filters = {"_SUMMER": "S", "_AUTUMN": "F", "_WINTER": "W"}
        for filter in filters:
            if pokedex_name.endswith(filter):
                return pokedex_name.replace(filter, filters[filter])
        return pokedex_name + "M"
    else:
        return pokedex_name


def handle_mega(pokedex_name):
    if "_MEGA" in pokedex_name:
        return "M" + pokedex_name.replace("_MEGA", "")
    else:
        return pokedex_name


def handle_unown(pokedex_name):
    if pokedex_name.startswith("UNOWN_"):
        if "QUESTION" in pokedex_name or "EXCLAMATION" in pokedex_name:
            return pokedex_name
        return pokedex_name.replace("UNOWN_", "UNOWN")
    else:
        return pokedex_name


def handle_genesect(pokedex_name):
    if pokedex_name.startswith("GENESECT"):
        filters = {"_CHILL": "I", "_DOUSE": "W", "_BURN": "F", "_SHOCK": "E"}
        for filter in filters:
            if pokedex_name.endswith(filter):
                return pokedex_name.replace(filter, filters[filter])
        return pokedex_name
    else:
        return pokedex_name


def handle_flabebe(pokedex_name):
    if (pokedex_name.startswith("FLABEBE")
            or pokedex_name.startswith("FLOETTE")
            or pokedex_name.startswith("FLORGES")):
        pokedex_name = pokedex_name.replace("_ORANGE", "_RED")
        args = pokedex_name.split("_")
        if len(args) == 1:
            return pokedex_name
        if args[1] == "ETERNAL":
            return args[0] + "_AZ"
        return args[0] + "_" + args[1][0]
    return pokedex_name


special_cases = [
    handle_rotom,
    handle_deerling,
    handle_mega,
    handle_unown,
    handle_genesect,
    handle_flabebe,
]


def name_mapper(pokedex_name):
    # special_cases handles naming cases that require stranger transformations
    for case in special_cases:
        pokedex_name = case(pokedex_name)
    # special_maps maps pokedex_name to file name manually
    for key in special_maps:
        if pokedex_name == key:
            return special_maps[key]
    # ignore_suffixes is a list of key suffixes that indicate the name needs no changes
    for suffix in ignore_suffixes:
        if pokedex_name.endswith(suffix):
            return pokedex_name
    # short suffixes is for suffixed variants, i.e. NIDORAN_F -> NIDORANF
    for suffix in short_suffixes:
        if pokedex_name.endswith("_" + suffix):
            pokedex_name = pokedex_name.replace("_" + suffix, suffix[0])
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
