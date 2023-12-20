#!/proj/sot/ska3/flight/bin/python

import sys, os
import getpass

#Path altering to import script which is undergoing testing
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(TEST_DIR)
OUT_DIR = f"{TEST_DIR}/outTest"
sys.path.insert(0,PARENT_DIR)
LIVE_SCRIPT_DIR = "/data/mta4/Script/SOH"
LIVE_WEB_DIR = "/data/mta4/www/CSH"


PART_LIST = ['snap']

#NEW_DIR_LIST = [OUT_DIR, f"{OUT_DIR}/house_keeping", f"{OUT_DIR}/Web"]
NEW_DIR_LIST = [OUT_DIR, f"{OUT_DIR}/Web"]
for dir in NEW_DIR_LIST:
	os.system(f"mkdir -p {dir}")

#Extra house_keeping setup files
#require MSID lists from git housekeeping
os.system(f"cp -r {PARENT_DIR}/house_keeping {OUT_DIR}")
os.system(f"ln -sf /home/{getpass.getuser()}/.netrc {OUT_DIR}/house_keeping/.netrc")
os.system(f"ln -sf {LIVE_SCRIPT_DIR}/house_keeping/stime_to_comm {OUT_DIR}/house_keeping/")

#Extra Web setup
for part in PART_LIST:
    if not os.path.isfile(f"{OUT_DIR}/Web/blob_{part}.json"):
    	os.system(f"cp {LIVE_WEB_DIR}/blob_{part}.json {OUT_DIR}/Web/")



import copy_data_from_occ as cdfo
import check_msid_status as cms

MOD_GROUP = [cdfo,cms]
#Permute across the imported modules to change pathing variables
for mod in MOD_GROUP:
	if hasattr(mod,'BIN_DIR'):
		mod.BIN_DIR = f"{PARENT_DIR}"
	#cdfo uses several file lists stored in house_keeping. Consult/copy from git repo.
	if hasattr(mod,'HOUSE_KEEPING'):
		mod.HOUSE_KEEPING = f"{OUT_DIR}/house_keeping"
	if hasattr(mod,'HTML_DIR'):
		mod.HTML_DIR = f"{OUT_DIR}/Web"
	
for part in PART_LIST:
    cdfo.copy_data_from_occ_part(part)