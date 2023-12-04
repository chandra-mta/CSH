#!/proj/sot/ska3/flight/bin/python

import sys, os

#Path altering to import script which is undergoing testing
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(TEST_DIR)
OUT_DIR = f"{TEST_DIR}/outTest"
sys.path.insert(0,PARENT_DIR)

new_dir_list = [OUT_DIR, f"{OUT_DIR}/house_keeping", f"{OUT_DIR}/Web"]
for dir in new_dir_list:
	os.system(f"mkdir -p {dir}")

import copy_data_from_occ as cdfo
import check_msid_status as cms

mod_group = [cdfo,cms]
#Permute across the imported modules to change pathing variables
for mod in mod_group:
	if hasattr(mod,'BIN_DIR'):
		mod.BIN_DIR = f"{PARENT_DIR}"
	#cdfo uses several file lists stored in house_keeping. Consult/copy from git repo.
	if hasattr(mod,'HOUSE_KEEPING'):
		mod.HOUSE_KEEPING = f"{OUT_DIR}/house_keeping"
	if hasattr(mod,'HTML_DIR'):
		mod.HTML_DIR = f"{OUT_DIR}/Web"
	
part_list = ['snap']
for part in part_list:
    cdfo.copy_data_from_occ_part(part)