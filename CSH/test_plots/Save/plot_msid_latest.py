#!/data/mta4/ska3/bin/python
from soh_msid_plot_class_v2 import soh_plots
import numpy as np
import os, time
import signal
from pathlib import Path
import os.path

#define the various graph groups any weights(conversions) and units
plot_looks = {
	'Pcaditv':{'msid_ls': ['AIRU1G1I','AIRU1G2I','AIRU2G1I','AIRU2G2I'], 'units': ['mA', 'mA', 'mA', 'mA'], 'weight':1, 'title': 'Realtime IRU Currents'},
	'Aosymom': {'msid_ls': ['AOSYMOM1','AOSYMOM2','AOSYMOM3'],'units': ['J*s', 'J*s', 'J*s'] ,'weight': 1 ,'title': 'Realtime Momentum'},
	'Aorate': {'msid_ls': ['AORATE1','AORATE2','AORATE3'],'units': ['arcsec/sec', 'arcsec/sec', 'arcsec/sec'], 'weight': 206265, 'title': 'Estimated Angular Rates in ACA Frame' },
	'Aodithr': {'msid_ls': ['AODITHR3','AODITHR2'], 'units': ['rad', 'rad'] ,'weight': 3600, 'title': 'Commanded Dither Angles' },
	'Hrcelec': {'msid_ls':['2DETART','2SHLDART', '2DETBRT','2SHLDBRT'],'units': [None, None], 'weight': 1/256.0 , 'title': 'Event and Shield rates'},
	'Spcelec': {'msid_ls':['ELBV','ELBI_LOW'], 'units': ['V', 'A'], 'weight':1 , 'title': 'Bus Voltage and Current'},
	'Pcadgdrift':{'msid_ls':['AOGBIAS1', 'AOGBIAS2','AOGBIAS3'], 'units': ['arcsec/s', 'arcsec/s','arcsec/s'] , 'weight': 206265, 'title': 'Realtine IRU Bias Drift'},
	'Gratgen':{'msid_ls':['4HPOSARO','4LPOSBRO'], 'units': ['deg', 'deg'], 'weight': 1, 'title': 'Gratings Rotation Angles'},
	'Ycurrent':{'msid_ls':['ESAPYI','ESAMYI'], 'units': ['A', 'A'], 'weight': 1, 'title': 'S/A Y Current'},
	'Sc_temp':{'msid_ls':['TSAPYT','TSAMYT'], 'units': [None, None], 'weight': 1, 'title': 'Y Wing Solar Array Temp'},
	'Mups':{'msid_ls':['PLINE03T','PLINE04T'], 'units': [None, None], 'weight': 1, 'title': 'Prop Line Temps'},
	'Spcelecb':{'msid_ls':['CTXBV', 'CTXBPWR'], 'units': ['V', None], 'weight':1, 'title': 'Transmitter B'},
	'Spceleca':{'msid_ls':['CTXAV', 'CTXAPWR'], 'units': ['V', None], 'weight':1, 'title': 'Transmitter A'},
	'Spcelec_pwr':{'msid_ls':['OHRMAPWR', 'OOBAPWR'], 'units': [None, None], 'weight':1, 'title': 'Computed Total Power'},
	'Pcadgrate':{'msid_ls':['AOALPANG', 'AOBETANG'], 'units': ['deg', 'deg'], 'weight':1, 'title': 'FSS Angle Meas.'},
	'Sys_temps':{'msid_ls':['AACCCDPT','4OAVHRMT','4OAVOBAT'], 'units': [None, None, None], 'weight':1, 'title':'Various Temperatures'}  
	}

def plot(msid_group, plot_class):
	print("Here is your arg:", msid_group)
	#import ast and open file that contains weights and units and such(?)
	msid_list, weight = plot_looks[msid_group]['msid_ls'] , plot_looks[msid_group]['weight']
	units, title = plot_looks[msid_group]['units'] , plot_looks[msid_group]['title']
	#get the dependents of each msid that's in our group
	dep_list = []
	for msid in msid_list:
		dep = p.return_dependent(msid)
		if dep is not None:
			dep_list += [dep]
	pull_set = np.append(msid_list, np.unique(dep_list))
	file_name = msid_group + '_plot.html'
	print (p.start_time)
	plot_class.plot_joint_graphs(pull_set, msid_group,  msid_list, weight, units, title, file_name)	

def signal_handler(signum, frame):
	raise Exception("time is done")

if __name__ == '__main__':
	p = soh_plots()
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(3800)
	try:
		plot_file = Path(".plot_these.txt")
		done = []
		ran_comm = False
		while True:
			if (not ran_comm and os.path.isfile('.in_comm')):
				p.dsn_comm()
				ran_comm = True
			with open('.plot_these.txt', 'r') as file:
				for line in file:
					now = time.time()
					if (len(line.split())>1 and line not in done):
						msid, call_time = line.split()[0], line.split()[1]
						if (not msid.isdigit() and call_time.isdigit() and (now - int(call_time))<=30):
							try:
								plot(line.split(" ")[0], p)
								done += [line]
							except Exception as e:
								print (e)
								break #want to break and say there was an error
	except Exception as msg:
		print(msg)
