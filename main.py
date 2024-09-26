import os
import os.path
from convert.convert_c import convert_c_file
from convert.convert_string import convert_string_file
from convert.convert_txt import convert_txt_file

root_dir = os.path.dirname(__file__)
src_dir = os.path.join(root_dir, "c")
dst_dir = os.path.join(root_dir, "json")

for root, dirs, files in os.walk(src_dir):
    for file in files:
        src_file = os.path.join(root, file)
        dst_subdir = root.replace(src_dir, dst_dir)
        dst_file = src_file.replace(src_dir, dst_dir)

        if not os.path.exists(dst_subdir):
            os.makedirs(dst_subdir)

        converters = {
            ".c": convert_c_file,
            ".string": convert_string_file,
            ".txt": convert_txt_file,
        }

        for extension in converters:
            if file.endswith(extension):
                dst_file = dst_file.replace(extension, ".json")
                converters[extension](src_file, dst_file)
