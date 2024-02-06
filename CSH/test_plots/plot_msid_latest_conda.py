#!/proj/sot/ska3/flight/bin/python

from soh_msid_plot_class_v3 import soh_plots
from plot_cleaning import plot_cleaning
import numpy as np
import os, time
import signal
from pathlib import Path
import os.path
import timeit
import sys
import traceback
import json

BIN_DIR = "/data/mta4/www/CSH/test_plots"
OUT_DIR = "/data/mta4/www/CSH/test_plots/plot_sections"

#define the various graph groups any weights(conversions) and units
with open(f"{BIN_DIR}/plot_looks.json") as f:
	PLOT_LOOKS = json.load(f)

MSID_GROUP_SELECTION = list(PLOT_LOOKS.keys())#Selections of which MSID groupings to plot. Default to all.

CONSIDER_TIME = False #whether or not to use the plot_time.json file to determine which MSID_groups to generate the plot for.
CUTOFF = 30

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
	p = soh_plots()
	cleaning = plot_cleaning()
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


def choose_group():
	"""
	Select which MSID groups to plot based on provided timing information
	"""
	selection = []
	now = time.time()
	with open(f"{BIN_DIR}/plot_time.json") as f:
		time_dict = json.load(f)
	for k,v in time_dict.items():
		if now - v <= CUTOFF:
			selection.append(k)
	return selection


if __name__ == '__main__':
	if CONSIDER_TIME:
		selection = choose_group()
	else:
		selection = MSID_GROUP_SELECTION
	gen_plots(selection)