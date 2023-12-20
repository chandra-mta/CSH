#!/proj/sot/ska3/flight/bin/python

import sys,os

#Path altering to import script which is undergoing testing
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(TEST_DIR)
OUT_DIR = f"{TEST_DIR}/outTest"
sys.path.insert(0,PARENT_DIR)
LIVE_BIN_DIR = "/data/mta4/www/CSH/test_plots"

NEW_DIR_LIST = [OUT_DIR]
for dir in NEW_DIR_LIST:
	os.system(f"mkdir -p {dir}")


#Extra housekeeping for setup files
#NOTE this should be required. why searhc outtest?
#os.system(f"ln -sf  {LIVE_BIN_DIR}/msid_limits.pickle {OUT_DIR}")

import plot_msid_latest_conda as pml
import soh_msid_plot_class_v3 as smpc
import plot_cleaning as pc

MOD_GROUP = [pml, smpc, pc]
#Permute across imported modules to change pathing variables
for mod in MOD_GROUP:
    if hasattr(mod,'BIN_DIR'):
	    mod.BIN_DIR = f"{PARENT_DIR}"
    if hasattr(mod,'OUT_DIR'):
	    mod.OUT_DIR = f"{OUT_DIR}"

pml.gen_plots()