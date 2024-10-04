import os
import pprint


root_dir = os.path.dirname(os.path.dirname(__file__))
c_dir = os.path.join(root_dir, "c")
csv_dir = os.path.join(root_dir, "csv")
dst_dir = os.path.join(root_dir, "json")


def pprint_top_entries(table, num_entries=10):
    keys = list(table)[:10]
    subdict = {key: table[key] for key in keys}
    pprint.pprint(subdict)