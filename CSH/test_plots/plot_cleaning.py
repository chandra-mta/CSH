#!/proj/sot/ska3/flight/bin/python

import timeit
import os
from datetime import datetime
import argparse
import random

BIN_DIR = "/data/mta4/www/CSH/test_plots"
OUT_DIR = "/data/mta4/www/CSH/test_plots"

class plot_cleaning:

	def __init__(self):
		self.path = BIN_DIR
		
	def rename_files(self, script, div, rand):
		start_time = timeit.default_timer()
		if os.path.exists(script):
			old_s = script + str(rand) + 'old.del'
			os.rename(script, old_s)
		if os.path.exists(div):
			old_d = div + str(rand) + 'old.del'
			os.rename(div, old_d)
		print ("renamed files: ", timeit.default_timer() - start_time)
	
	def in_comm(self, script, div, rand):
		start_time = timeit.default_timer()
		if os.path.isfile(f"{BIN_DIR}/.in_comm"):
			self.rename_files(script, div, rand)
			return True
		print ("checked_comm: ", timeit.default_timer() - start_time)
	
	def last_comm(self, script, div, rand, path):
		start_time = timeit.default_timer()
		#with open('.last_comm', 'r') as f:
		#	time = f.readlines()[0].rstrip()
		#print ("opened comm: ", timeit.default_timer() - start_time)
		#comm_end = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
		last_comm_path = path + '.last_comm'
		comm_end = datetime.utcfromtimestamp(os.path.getmtime(last_comm_path))
		print ('comm end: ', timeit.default_timer() - start_time)
		start_time = timeit.default_timer()
		mod_time = datetime.utcfromtimestamp(os.path.getmtime(script))
		print ("got modified time: ", timeit.default_timer() - start_time)
		#if the last time the plot was updated was before the last comm ended
		#we have more data to pull
		if (mod_time < comm_end):
			self.rename_files(script, div, rand)
			print ("<!-- new plot -->")
		else:
			print ("<!-- old but good plot -->")
	
	def main(self, msid):
		script, div = self.path + 'script_'+ msid , self.path + 'div_' + msid
		rand = random.randint(1000, 9999)
		if not os.path.isfile(script):
			return
		elif self.in_comm(script, div, rand):
			return
		else:
			self.last_comm(script, div, rand, self.path)
	
	
	
	
	


