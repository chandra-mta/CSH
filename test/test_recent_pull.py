#!/proj/sot/ska3/flight/bin/python

"""
This testing script tests specific subfunctions of the 
copy_data_from_occ python script to check json formatting and
data of a blob_<part>.json file.

Circumvents script auto-failure to fetch data if not in comm, and
instead pulls data values which match most recently.
"""

import sys, os
import getpass
import time
import Chandra.Time
import re

#Path altering to import script which is undergoing testing
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(TEST_DIR)
OUT_DIR = f"{TEST_DIR}/outTest"
sys.path.insert(0,PARENT_DIR)
LIVE_SCRIPT_DIR = "/data/mta4/Script/SOH"
LIVE_WEB_DIR = "/data/mta4/www/CSH"


PART_LIST = ['snap']
#Subject to change as necessary
HOUR_PREV = 5

NEW_DIR_LIST = [OUT_DIR, f"{OUT_DIR}/Web"]
for dir in NEW_DIR_LIST:
	os.system(f"mkdir -p {dir}")

#Extra house_keeping setup files
#require MSID lists from git housekeeping
#but we are testing changes to that data pull, so leave this cmd up to user discretion
#for changing the lists.
#os.system(f"cp -r {PARENT_DIR}/house_keeping {OUT_DIR}")

os.system(f"ln -sf /home/{getpass.getuser()}/.netrc {OUT_DIR}/house_keeping/.netrc")
os.system(f"ln -sf {LIVE_SCRIPT_DIR}/house_keeping/stime_to_comm {OUT_DIR}/house_keeping/")

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

stday = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
stop  = Chandra.Time.DateTime(stday).secs
#Define start time as a larger data fetch
start = stop - 60 *(60* HOUR_PREV)

for part in PART_LIST:
#
#--- read msid list
#
    ifile = f"{cdfo.HOUSE_KEEPING}/Inst_part/msid_list_{part}"
    msid_list = cdfo.read_data_file(ifile)
#
#--- msid <--> id dict
#
    ifile = f"{cdfo.HOUSE_KEEPING}/Inst_part/msid_id_list_{part}"
    data      = cdfo.read_data_file(ifile)

    mdict     = {}
    for ent in data:
        atemp  = re.split(':', ent)
        mdict[atemp[0]] = atemp[1]
#
#--- read limit table
#
        ldict = cdfo.read_limit_table()
#
    cdfo.extract_blob_data(msid_list, mdict, ldict, start, stop, part)