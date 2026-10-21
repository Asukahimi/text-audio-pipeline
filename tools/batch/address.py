import os
import shutil
import re
source_folder = '<CSV_WORK>'
destination_folder = '<OPERA_WORK>'
def contains_number(filename):
    return bool(re.search(r'\d',filename))
for filename in os.listdir(source_folder):
    if filename.endswith('.csv') and contains_number(filename):
        source_path = os.path.join(source_folder,filename)
        destination_path = os.path.join(destination_folder,filename)
        shutil.move(source_path,destination_path)