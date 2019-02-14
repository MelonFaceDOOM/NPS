import os 
from create_multiple_torrc_files import create_torrc_files

current_dir = os.path.dirname(os.path.realpath(__file__))
print(create_torrc_files(current_dir, 10))