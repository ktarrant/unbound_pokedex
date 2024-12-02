fields = {
    "type": ["type1", "type2"],
    "item": ["item1", "item2"],
    "growthRate": ["growthRate"],
    "eggGroup": ["eggGroup1", "eggGroup2"],
    "ability": ["ability1", "ability2", "hiddenAbility"],
}


def collect_field_types(pokedex):
    data = {field: {} for field in fields}
    for dex, dex_entry in pokedex.items():
        for species, species_entry in dex_entry.items():
            for field, source_fields in fields.items():
                for source_field in source_fields:
                    try:
                        source_value = species_entry[source_field]
                    except KeyError:
                        continue
                    if "NONE" in source_value:
                        continue
                    compatibility = data[field].get(source_value, [])
                    compatibility.append(species)
                    data[field][source_value] = compatibility
    return data
