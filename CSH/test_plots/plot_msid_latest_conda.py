#!/proj/sot/ska3/flight/bin/python

import soh_msid_plot_class_v3
import plot_cleaning
import numpy as np
import os
import time
import signal
from pathlib import Path
import os.path
import timeit
import sys
import traceback
import json
import argparse
import getpass

BIN_DIR = "/data/mta4/www/CSH/test_plots"
OUT_DIR = "/data/mta4/www/CSH/test_plots/plot_sections"

#define the various graph groups any weights(conversions) and units
with open(f"plot_looks.json") as f:
	PLOT_LOOKS = json.load(f)

MSID_GROUP_SELECTION = list(PLOT_LOOKS.keys())#Selections of which MSID groupings to plot. Default to all.

def plot(msid_group, plot_class):
	#print("Here is your arg:", msid_group)
	#import ast and open file that contains weights and units and such(?)
	msid_list = PLOT_LOOKS[msid_group]['msid_ls']
	weight = PLOT_LOOKS[msid_group]['weight']
	units = PLOT_LOOKS[msid_group]['units']
	title = PLOT_LOOKS[msid_group]['title']
	#get the dependents of each msid that's in our group
	dep_list = []
	for msid in msid_list:
		dep = plot_class.return_dependent(msid)
		if dep is not None:
			dep_list += [dep]
	pull_set = np.append(msid_list, np.unique(dep_list))
	file_name = f"{msid_group}_plot.html"
	plot_class.plot_joint_graphs(pull_set, msid_group,  msid_list, weight, units, title, file_name)	

def signal_handler(signum, frame):
	raise Exception("time is done")

def gen_plots(selection = MSID_GROUP_SELECTION):
	p = soh_msid_plot_class_v3.soh_plots()
	cleaning = plot_cleaning.plot_cleaning()
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(3660)
	for msid_group in selection:
		try:
			start_t = timeit.default_timer()
			cleaning.main(msid_group)
			#print( "cleaning: ", timeit.default_timer() - start_t)
			plot(msid_group,p)
		except:
			traceback.print_exc()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
	parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of plot.")
	parser.add_argument("-g", "--group", required = False, nargs="+", help = "Select which MSID grouping plots to generate. Consult plot_looks.json keys for options.\
					 Choose 'all' in test mode to test all groups.")
	args = parser.parse_args()

#
#--- Determine if running in test mode and change pathing if so
#
	if args.mode == "test":
#
#--- Path output to same location as unit tests
#
		BIN_DIR = os.path.dirname(os.path.realpath(__file__))
		OUT_DIR = f"{BIN_DIR}/test/_outTest/plot_sections"

		if args.path:
			OUT_DIR = args.path
		os.makedirs(OUT_DIR, exist_ok = True)
		if args.group:
			if args.group != ['all']:
				MSID_GROUP_SELECTION = args.group
		else:
			MSID_GROUP_SELECTION = ['Sys_temps', 'Spcelec']
				
		MOD_GROUP = [soh_msid_plot_class_v3, plot_cleaning]
#
#--- Permute across imported modules to change pathing variables
#
		for mod in MOD_GROUP:
			if hasattr(mod,'BIN_DIR'):
				mod.BIN_DIR = f"{BIN_DIR}"
			if hasattr(mod,'OUT_DIR'):
				mod.OUT_DIR = f"{OUT_DIR}"

		gen_plots(MSID_GROUP_SELECTION)

	elif args.mode == "flight":
#
#--- Create a lock file and exit strategy in case of race conditions
#
		import getpass
		name = os.path.basename(__file__).split(".")[0]
		user = getpass.getuser()
		if os.path.isfile(f"/tmp/{user}/{name}.lock"):
			sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
		else:
			os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

		gen_plots(MSID_GROUP_SELECTION)
#
#--- Remove lock file once process is completed
#
		os.system(f"rm /tmp/{user}/{name}.lock")