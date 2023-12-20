#!/proj/sot/ska3/flight/bin/python

from soh_msid_plot_class_v3 import soh_plots
from plot_cleaning import plot_cleaning
import numpy as np
import os, time
import signal
from pathlib import Path
import os.path
import timeit

#define the various graph groups any weights(conversions) and units
plot_looks = {
	'Pcaditv':{'msid_ls': ['AIRU1G1I','AIRU1G2I','AIRU2G1I','AIRU2G2I'], 'units': ['mA', 'mA', 'mA', 'mA'], 'weight':1, 'title': 'Realtime IRU Currents'},
	'Aosymom': {'msid_ls': ['AOSYMOM1','AOSYMOM2','AOSYMOM3'],'units': ['J*s', 'J*s', 'J*s'] ,'weight': 1 ,'title': 'Realtime Momentum'},
	'Aorate': {'msid_ls': ['AORATE1','AORATE2','AORATE3'],'units': ['arcsec/sec', 'arcsec/sec', 'arcsec/sec'], 'weight': 206265, 'title': 'Estimated Angular Rates in ACA Frame' },
	'Aodithr': {'msid_ls': ['AODITHR3','AODITHR2'], 'units': ['rad', 'rad'] ,'weight': 3600, 'title': 'Commanded Dither Angles' },
	'Hrcelec': {'msid_ls':['2DETART','2SHLDART', '2DETBRT','2SHLDBRT'],'units': [None, None, None, None], 'weight': 1/256.0 , 'title': 'Event and Shield rates'},
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
	'Sys_temps':{'msid_ls':['2CEAHVPT','AACCCDPT','4OAVHRMT','4OAVOBAT'], 'units': ['C', 'F', 'F', 'F'], 'weight':1, 'title':'Various Temperatures'},  
	'Zmodel_temps':{'msid_ls':['TCYLAFT6','TCYLFMZM','TEPHIN','TFSSBKT1','TMZP_MY'], 'units': [None, None, None, None, None], 'weight':1, 'title':'Minus-Z Model Temperatures'},	
	'Mups_load':{'msid_ls':['PM1THV1T', 'PM2THV1T'], 'units': [None, None], 'weight':1, 'title':'Mups Value Model Temp'},  
	'Tank_temp':{'msid_ls':['PFTANK2T', 'PMTANK3T'], 'units': [None,  None], 'weight':1, 'title':'Fuel and Mups Tank Temp'},  
	'Quat':{'msid_ls':['AOTARQT1','AOTARQT2', 'AOTARQT3', 'AOATTQT4'], 'units': [None, None, None, None], 'weight':1, 'title':'Target Quaternion'},
	'Blkhd':{'msid_ls':['4RT700T'], 'units': [None], 'weight':1, 'title':'OBA Frward BLKHD Temp'},
	'Aosares':{'msid_ls':['AOSARES1', 'AOSARES2'], 'units': [None, None], 'weight':1, 'title':'Solar Array Angle'},
	'Psmc':{'msid_ls':['1PDEAAT','1PIN1AT'], 'units': [None, None], 'weight':1, 'title':'PSMC Model Temp'},
	'Dpa':{'msid_ls':['1DPAMZT'], 'units': [None], 'weight':1, 'title':'DPA Model Temp'}, 
	'EB1':{'msid_ls':['EB1CI','EB1DI','EB1V'], 'units': [None, None, None], 'weight':1, 'title':'Battery 1 Metrics'}, 
	'EB2':{'msid_ls':['EB2CI','EB2DI','EB2V'], 'units': [None, None, None], 'weight':1, 'title':'Battery 2 Metrics'}, 
	'EB3':{'msid_ls':['EB3CI','EB3DI','EB3V'], 'units': [None, None, None], 'weight':1, 'title':'Battery 3 Metrics'},
	'Scs_acis':{'msid_ls':['1CBAT','1DPICACU','1DPICBCU'], 'units': [None, None, None], 'weight':1, 'title':'ACIS Science Intrument Safing'}, 
	'TB1':{'msid_ls':['TB1T1','TB1T2','TB1T3'], 'units': [None, None, None], 'weight':1, 'title':'EPS Battery 1 Temps'}, 
	'TB2':{'msid_ls':['TB2T1','TB2T2','TB2T3'], 'units': [None, None, None], 'weight':1, 'title':'EPS Battery 2 Temps'}, 
	'TB3':{'msid_ls':['TB3T1','TB3T2','TB3T3'], 'units': [None, None, None], 'weight':1, 'title':'EPS Battery 3 Temps'}, 
	'AACHT':{'msid_ls':['AACH1T','AACH2T'], 'units': [None, None], 'weight':1, 'title':'AC Housing Temps'},
	'ACPV':{'msid_ls':['ACPA5CV','ACPB5CV'], 'units': [None, None], 'weight':1, 'title':'CPE Converter Voltage'},
	'ADEV':{'msid_ls':['ADE1P5CV','ADE2P5CV'], 'units': [None, None], 'weight':1, 'title':'ADE Converter Voltage'},
	'AGWSV':{'msid_ls':['AGWS1V','AGWS2V'], 'units': [None, None], 'weight':1, 'title':'Gyro Wheel Supply Input Voltage'},
	'IRUBT':{'msid_ls':['AIRU1BT','AIRU2BT', 'AIRU1VFT','AIRU2VFT'], 'units':[None, None, None, None], 'weight':1, 'title':'IRU Base Temp'},
	'Pcaditt':{'msid_ls':['AIRU1G1T','AIRU1G2T','AIRU2G1T','AIRU2G2T'], 'units': [None, None, None, None], 'weight':1, 'title':'Gyro Temps'},
	'AIOCV':{'msid_ls':['AIOAP5CV','AIOBP5CV'], 'units': [None, None], 'weight':1, 'title':'IOE Converter Voltage'},
	'ARWBT':{'msid_ls':['ARWA1BT', 'ARWA2BT', 'ARWA3BT', 'ARWA4BT', 'ARWA5BT', 'ARWA6BT'], 'units': [None, None, None, None, None, None], 'weight':1, 'title':'RWA Bearing Temperature'},
	'AWDCV':{'msid_ls':['AWD1CV5V', 'AWD2CV5V', 'AWD3CV5V', 'AWD4CV5V', 'AWD5CV5V', 'AWD6CV5V'], 'units': [None, None, None, None, None, None], 'weight':1, 'title':'WDE Converter Voltage'},
	'AWDTQ':{'msid_ls':['AWD1TQI', 'AWD2TQI', 'AWD3TQI', 'AWD4TQI','AWD5TQI', 'AWD6TQI'], 'units': [None, None, None, None, None, None], 'weight':1, 'title':'Wheel Torque Current'},
	'ASPEV':{'msid_ls':['ASPEB5CV','ASPEA5CV'], 'units': [None, None], 'weight':1, 'title': 'SPE Converter Voltage'},
	'AVDCV':{'msid_ls':['AVD1CV5V', 'AVD2CV5V'], 'units': [None, None], 'weight':1, 'title': 'VDE Converter Voltage'},
	'1CB_T':{'msid_ls':['1CBAT', '1CBBT'], 'units': [None, None], 'weight':1, 'title': 'Camera Body Temp'},
	'1CR_T':{'msid_ls':['1CRAT', '1CRBT'], 'units': [None, None], 'weight':1, 'title': 'Cold Radiator Temp'},
	'1D_MZT':{'msid_ls':['1DEAMZT', '1DPAMZT'], 'units': [None, None], 'weight':1, 'title': '-Z Panel Temp'},
	'1WR_T':{'msid_ls':['1WRAT', '1WRBT'], 'units': [None, None], 'weight':1, 'title': 'Warm Radiator Temp'},
	'Hrc_temps':{'msid_ls':['2CHTRPZT', '2DCENTRT', '2DTSTATT', '2FRADPYT'], 'units': [None, None, None, None], 'weight':1, 'title': 'HRC Temps'},
	'Pline_1_8':{'msid_ls':['PLINE01T','PLINE02T','PLINE03T','PLINE04T','PLINE05T','PLINE06T','PLINE07T','PLINE08T'], 'units': [None, None, None, None, None, None, None, None], 'weight':1, 'title': 'PLINE 01-08 Temps'},
	'Pline_9_16':{'msid_ls':['PLINE09T','PLINE10T','PLINE11T','PLINE12T','PLINE13T','PLINE14T','PLINE15T','PLINE16T'], 'units': [None, None, None, None, None, None, None, None], 'weight':1, 'title': 'PLINE 01-08 Temps'},
	'Mups_tank':{'msid_ls':['PMTANK1T', 'PMTANK2T', 'PMTANK3T'], 'units': [None, None, None], 'weight':1, 'title': 'Mups Tank Temp'},
	'Fuel_tank':{'msid_ls':['PFTANK1T', 'PFTANK2T'], 'units': [None, None], 'weight':1, 'title': 'Fuel Tank Temp'}

	}

def plot(msid_group, plot_class):
	print("Here is your arg:", msid_group)
	#import ast and open file that contains weights and units and such(?)
	msid_list, weight = plot_looks[msid_group]['msid_ls'] , plot_looks[msid_group]['weight']
	units, title = plot_looks[msid_group]['units'] , plot_looks[msid_group]['title']
	#get the dependents of each msid that's in our group
	dep_list = []
	for msid in msid_list:
		dep = plot_class.return_dependent(msid)
		if dep is not None:
			dep_list += [dep]
	pull_set = np.append(msid_list, np.unique(dep_list))
	file_name = msid_group + '_plot.html'
	plot_class.plot_joint_graphs(pull_set, msid_group,  msid_list, weight, units, title, file_name)	
	print (p.start_time)

def signal_handler(signum, frame):
	raise Exception("time is done")

if __name__ == '__main__':
	p = soh_plots()
	cleaning = plot_cleaning()
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(3660)
	try:
		plot_file = Path(".plot_these.txt")
		done = []
		ran_comm = False
		while True:
			#if (not ran_comm and os.path.isfile('.in_comm')):
				#print("thinks we're in comm")
				#p.dsn_comm()
				#ran_comm = True
			with open('.plot_these.txt', 'r') as file:
				for line in file:
					now = time.time()
					if (len(line.split())>1 and line not in done):
						msid, call_time = line.split()[0], line.split()[1]
						if (not msid.isdigit() and call_time.isdigit() and (now - int(call_time))<=30):
							try:
								start_t = timeit.default_timer()
								cleaning.main(msid)
								print( "cleaning: ", timeit.default_timer() - start_t)
								plot(line.split(" ")[0], p)
								done += [line]
							except Exception as e:
								print (e)
								break #want to break and say there was an error
	except Exception as msg:
		print(msg)
