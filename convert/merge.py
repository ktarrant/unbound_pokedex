from convert.error import report_error


def merge_species_data(pokedex, data, key=None, extra_mapper=None):
    for dex in pokedex:
        for species, species_entry in pokedex[dex].items():
            if species in data:
                if key:
                    species_entry[key] = data.pop(species)
                else:
                    species_entry.update(data.pop(species))
            elif dex in data:
                if key:
                    species_entry[key] = data.pop(dex)
                else:
                    species_entry.update(data.pop(dex))

    if data:
        report_error("merge_species_data", f"Unmatched data for {key} left over: {data}")


def create_evolves_from(pokedex):
    # We want to create a back-reference for the evolution, i.e. evolve_from
    for dex, dex_entry in pokedex.items():
        for species, species_entry in dex_entry.items():
            for from_dex, from_dex_entry in pokedex.items():
                for from_species, from_species_entry in from_dex_entry.items():
                    from_evos = [from_species for from_evo in from_species_entry.get("evolve_to", [])
                                 if from_evo["target"] == species]
                    species_entry["evolve_from"] = species_entry.get("evolve_from", []) + from_evos


def add_compatible_moves(pokedex, move_data):
    for dex, dex_entry in pokedex.items():
        for species in dex_entry:
            # add compatibility tables
            for category in ["tm", "tutor"]:
                move_list = []
                for move_num, entry in move_data[category].items():
                    if species in entry["compatibility"]:
                        move_list.append(entry["key"])

                if move_list:
                    pokedex[dex][species][category] = move_list
