#!/proj/sot/ska3/flight/bin/python

import timeit

from bokeh.plotting import figure #1.89usec
from bokeh.layouts import gridplot #1.83 usec
from bokeh.models import DatetimeTickFormatter, Legend, Span, BoxAnnotation, Title, CategoricalColorMapper, ColumnDataSource #1.7 usec
from bokeh.palettes import Plasma5 #5.82 usec
from bokeh.resources import CDN
from bokeh.embed import autoload_static, components
import numpy as np #0.74 usec
import re #0.222
from kadi import events #1.17 usec
from datetime import datetime, timedelta, time
import Chandra.Time
import pickle
import os, getpass
#print ("Login info",os.getlogin()," user info:" ,getpass.getuser())
import numexpr as ne
import maude
import itertools
import pandas as pd
import requests
import sys
import traceback


BIN_DIR = "/data/mta4/www/CSH/test_plots"
OUT_DIR = "/data/mta4/www/CSH/test_plots/plot_sections"

##########################################
# This script creates the soh_plots class that creates plot on https://cxc.cfa.harvard.edu/mta/CSH/soh_snap.html
# It is recommended that you run with a time limit, both to ensure functionality and catch errors
#########################################


class soh_plots:

	def __init__(self):
		#msid_dictionary created in msididx_dict_formatter.py
		limit_file = f"{BIN_DIR}/msid_limits.pickle"
		pickle_in = open(limit_file, "rb")
		self.msid_dict = pickle.load(pickle_in)
		self.in_comm = False
		self.dsn_comm()
		self.user, self.password = self.get_user_password()
		#vectorized functions
		self.change_time = np.vectorize(self.tme)
		self.calc = np.vectorize(self.msid_weight)
		self.color_choice_set = np.vectorize(self.color_equalities)
		self.color_choice_switch = np.vectorize(self.switch_color)
		self.switch = np.vectorize(self.switch_lookup)
		self.check_comm = True
		start_time = timeit.default_timer()
		self.get_time_frames('AORATE1')
		#print("initialized time_frames: ", timeit.default_timer()-start_time)
		self.check_comm = False

	#taken from maude code
	def get_user_password(self):
		import Ska.ftp
		netrc = Ska.ftp.parse_netrc()
		if 'occweb' in netrc:
			user = netrc['occweb']['login']
			password = netrc['occweb']['password']
		else:
			raise ValueError('user and password or "occweb" machine definition in ~/.netrc are '
							 'required for OCCweb authentication')
		return user, password

	def dsn_comm(self):
		########################
		# dsn_comm function gets our comm events calendar using kadi
		# these events are turned into a pandas dataframe with an IntervalIndex
		# this IntervalIndex facilitates lookup
		# This dataframe is saved to the instance variable int_df
		#######################

		now = datetime.utcnow()		
		yesterday = now - timedelta(1)
		tomorrow = now + timedelta(1)
		yesterday_start = Chandra.Time.DateTime(yesterday).day_start()
		tomorrow_end = Chandra.Time.DateTime(tomorrow).day_end()
		dsn_comms = events.dsn_comms.filter(yesterday_start.date, tomorrow_end.date)
		self.dsn_comms = dsn_comms

		#create dsn_intervals
		dsn_intervals = []
		for dsn_i , comm_event in enumerate(dsn_comms):
			comm_start = self.tracktime(comm_event.bot, comm_event.tstart, False) 
			comm_stop = self.tracktime(comm_event.eot, comm_event.tstop, True)
			dsn_intervals += [comm_start, comm_stop]

		#print (dsn_intervals)
		#we are creating intervals based on the comm schedule, this will tell us whether it's comm or not
		#but it's an uneven number
		comm_vals = ([True, False] * int(len(dsn_intervals) / 2))[:-1]
		self.int_df = pd.DataFrame(comm_vals, index = pd.IntervalIndex.from_breaks(dsn_intervals, closed='right'))

	def get_time_frames(self, msid):
		#########################
		# get_time_frames function is responsible for declaring whether or not we are in comm
		# this state is saved in the instance variable "in_comm", based on this variable 
		# we define the "start_time" for our data pull as well as "next_comm" for our plot
		########################

		now = datetime.utcnow()
		#using the 'nearest' functionality from maude, check time of latest data point
		#this is to supplement the comm schedule and in case of an unscheduled comm (also ASVT)
		if self.check_comm:
			site = 'https://telemetry.cfa.harvard.edu/maude/mrest/FLIGHT/{}.json?tp={}&nearest=t'
			tp = datetime.strftime(now, '%Y.%j.%H.%M')
			url = site.format(msid, tp)
			try:
				r = requests.get(url, headers = {'Accept-Encoding': 'gzip'}, auth=(self.user, self.password))
				if r.status_code != 200:
					raise IOError('request failed with status={} for URL={} and text={}'.format(r.status_code, r.url, r.text))
				out = r.json()
				last_point = datetime.strptime(str(out['data-fmt-1']['times'][0]), '%Y%j%H%M%S%f')
				if (now - last_point).seconds < 300:
					self.in_comm = True
				else:
					self.in_comm = False
				self.check_comm = False
			except Exception as e: 
				traceback.print_exc()

		self.start_time = None
		self.next_comm = None
		int_df = self.int_df
		
		# using the int_df built in dsn_comms() function, we just insert the timestamp of now
		# and it tells us if there was a scheduled comm
 
		now_idx = int_df.index.get_loc(pd.Timestamp(now))
		now_inter = int_df.loc[pd.Timestamp(now)]
		comm_sched = now_inter.values[0]
		self.in_comm = comm_sched if not self.check_comm else self.in_comm

		##################
		# if we're in comm pull data from the last comm until now
		# if we're NOT in comm pull data from between the last two comms until now
		# if for some reason there was a failure, just pull the last 24 hours of data
		#################
		if (self.in_comm and comm_sched):
			try:
				self.start_time = int_df.iloc[now_idx - 2].name.left.to_pydatetime()
			except:
				#print("Index error during comm when trying to find start_time")
				traceback.print_exc()
				pass
		elif (not self.in_comm):
			try:
				self.start_time = int_df.iloc[now_idx - 3].name.left.to_pydatetime()
				self.next_comm = int_df.iloc[now_idx].name.right.to_pydatetime()
			except:
				#print ("Index error when trying to find start_time")
				traceback.print_exc()
				pass
		elif (self.start_time == None):
			self.start_time = now - timedelta(1)

	#returns chandra time as a datetime object
	def tme(self, x):
		return (datetime.strptime(Chandra.Time.DateTime(x).date, '%Y:%j:%H:%M:%S.%f'))

	#uses tractime and bot to get at "true time"
	def tracktime(self, track, ttime, end_bool):
		comm_day = self.tme(ttime)
		track_time = datetime.strptime(track, '%H%M').time()
		if (comm_day.time() >= time(23,0) and track_time < time(1,0)):
			comm_day = comm_day + timedelta(1)
		if (comm_day.time() <= time(1,0) and track_time > time(23,0)):
			#print ("comm days where weird")
			comm_day = comm_day - timedelta(1)
		return( datetime.combine(comm_day.date(), track_time) )


	#multiplies numbers by a weight
	def msid_weight(self, x, weight):
		return (x * weight)

	
	def color_equalities(self, point, low_red, low_yellow, hi_red, hi_yellow):
		if (point <= low_red):
			return ("Low-red")
		elif (point <= low_yellow):
			return ("Low-yellow")
		elif (point >= hi_yellow):
			return ('High-yellow')
		elif (point >= hi_red):
			return ("High-red")
		else:
			return ("Normal")
	
	#for instances where we have a switch limit
	def switch_color(self, msid_value, msid_limit, weight):
		if (msid_limit is None):
			return ("Normal")
		low_red = msid_limit['wl'] * weight
		low_yellow = msid_limit['cl'] * weight
		hi_red = msid_limit['wh'] * weight
		hi_yellow = msid_limit['ch'] * weight
		return (self.color_equalities(msid_value, low_red, low_yellow, hi_red, hi_yellow))


	def switch_lookup(self, msid_info, point):
		if point in msid_info['switch_lim']['switch']:
			return (msid_info['switch_lim']['switch'][point])

	def return_dependent(self, msid):
		if ('switch_lim' in self.msid_dict[msid]):
			dependent = self.msid_dict[msid]['switch_lim']['dependent']
			return (dependent)

	#used by select_intervals below
	def logical_intervals(self, times, values, switch_lim):
		i = 0
		ending = len(times)
		intervals = []
		# from the itertools documentation:
		# [k for k, g in groupby('AAAABBBCCDAABBB')] --> A B C D A B
		# [list(g) for k, g in groupby('AAAABBBCCD')] --> AAAA BBB CC D
		# itertools.groupby returns A:[A,A,A,A], B:[B,B,B], C:[C,C], D:[D]
		for key, group in itertools.groupby(values):
			elems = len(list(group))
			begin = times[i] if i > 0 else times[i] - 3600.00
			i += elems
			end = times[i] if i < ending else times[i - 1]
			switch = switch_lim['switch'][key] if key in switch_lim['switch'] else None
			intervals += [(switch, begin, end)]
		return (intervals)

	def select_intervals(self, msid_data, dep_data, msid):
		# function used to assign limits to the right time
		# especially used during switch limits
		msid_limits = np.empty(len(msid_data['times']), dtype = dict)
		intervals = self.logical_intervals(dep_data['times'], dep_data['values'], self.msid_dict[msid]['switch_lim'])
		for interval in intervals:
			begin, end = interval[1], interval[2]
			msid_bool = ((msid_data['times'] >= begin) & (msid_data['times'] <= end))
			msid_limits[msid_bool] = interval[0]
		return (msid_limits)

	def return_limit_colors(self, msid, msid_vals, set_data, frame, weight):
		##########################
		# return_limit_colors returns a list of color values corresponding to each data point and the limit
		# for swithc limits, the limit might be dependent on a different msid
		# logical_intervals matches the value of that msid during a time period to the correct time
		# ########################
		msid_info = self.msid_dict[msid]
		dep = self.return_dependent(msid)
		if ('set_lim' in msid_info):
			low_red = msid_info['set_lim']['wl'] * weight
			low_yellow = msid_info['set_lim']['cl'] * weight
			hi_red = msid_info['set_lim']['wh'] * weight
			hi_yellow = msid_info['set_lim']['ch'] * weight
			return (self.color_choice_set(msid_vals, low_red, low_yellow, hi_red, hi_yellow))
		elif ('switch_lim' in msid_info):
			#here we need to go through the possible values our dependent could be
			#because msids have different time steps (1) create intervals 
			#(2) return the right limit for that interval

			dep = msid_info['switch_lim']['dependent']
			dep_data = set_data['data'][-1]
			msid_data = set_data['data'][frame]
			if (dep_data['msid'] == dep):
				msid_limits = self.select_intervals(msid_data, dep_data, msid) 
				return (self.color_choice_switch(msid_vals, msid_limits, weight))
			else:
				#print ("warning: Non matching msid lim dep", msid)
				return None

	def plot_joint_graphs(self, pull_set, group_name, msid_list, weight, units, title, file_name):
		###############################
		# plot_joint_graphs is the main function it's inputs are:
		# pull_set: the list of msids we're plotting (includes dependent msids) 
		# group_name: the name of the group we're plotting
		# msid_list: the list of msids we're plotting (excludes dependent msids)
		# weight: a list of weights that correspond to the msid_list
		# units: a list of units that correspond to the msid_list
		# title: title of the plot
		# file_name: useless
		# these inputs are all used to output a div and script file that are loaded by the webpage
		#############################
		start_time = timeit.default_timer()
		self.get_time_frames(pull_set[0])
		#print("time_frames: ", timeit.default_timer()-start_time)
		script_name = f"script_{group_name}"
		div_name = f"div_{group_name}"
		start_time = timeit.default_timer()
		try:
			set_data = maude.get_msids(pull_set, self.start_time)
		except Exception as ex:
			for excs in ex.args:
				if "MAUDE query failed" in excs:
					with open(script_name, 'w') as f:
						f.write("<font color=\"red\"><b>Sorry, Maude couldn't fetch the data from the last comm</font>")
			return
		#print ("pulled set data", timeit.default_timer()-start_time)
		now = datetime.utcnow()
		frames = []
		start_plots = timeit.default_timer()
		for frame, msid in enumerate(msid_list):
			start_plot = timeit.default_timer()
			data = set_data['data'][frame]
			t1998 = 883612736.816
			data_tme = data['times']
			data_values = data['values']
			data_times = np.array(ne.evaluate('data_tme + t1998'), dtype='u8').view('datetime64[s]')
			#print (len(data_times), len(data_values))
			last_dat_pt = (np.datetime64(now) - data_times[-1]).astype(int)
			if (self.in_comm and last_dat_pt > 600000000): #10 minutes but in microsecs
				self.check_comm = False
			elif (not self.in_comm and last_dat_pt < 300000000): #5 minutes but in microsecs
				self.check_comm = True
			else:
				self.check_comm = False
			data_values = ne.evaluate('data_values*weight')
			if (self.in_comm):
				nxt_comm = "Currently in comm"
			elif (self.next_comm is None):
				nxt_comm = "Unknown"
			else:
				nxt_comm = self.next_comm.strftime('%Y:%j:%H:%M')
			last_data = data_times[-1].astype(datetime).strftime('%Y:%j:%H:%M')
			plot_title = f"{title}\nLast update: {last_data}\nNextDSN Comm: {nxt_comm}"

			unit = units[frame]
			y_label = f"{msid}({unit})"
			if frame > 0:
				p = figure(title=plot_title, x_axis_label = 'Time (UTC)', y_axis_label = y_label, 
						   x_range = frames[0][0].x_range, x_axis_type = "datetime",
						  width = 700, height = 300)
			else:
				p = figure(title=plot_title, x_axis_label = 'Time (UTC)', y_axis_label = y_label,
						   x_axis_type = "datetime", width = 700, height = 300)
			p.xaxis.formatter = DatetimeTickFormatter(
				minutes = "%Y:%j:%H:%M",
				hours = "%Y:%j:%H",
				hourmin = "%Y:%j:%H:%M",
				days = "%Y:%j"
			)
			colors = None
			if 'lim' in self.msid_dict[msid]:
				colors = self.return_limit_colors(msid, data_values, set_data, frame,  weight)
			if type(colors) == type(None) or all(x is None for x in colors):
				colors = np.full((1, len(data_values)), 'Normal')[0]
			source = ColumnDataSource(dict(
				utc_times = data_times,
				msid_values = data_values,
				label = colors
			))
			color_mapper = CategoricalColorMapper(factors = ['Normal', 'High-red', 'Low-red', 'Low-yellow', 'High-yellow'],
												 palette = [Plasma5[0], Plasma5[1], Plasma5[2], Plasma5[3], Plasma5[4]]
												 )

			for comm in self.dsn_comms:
				low_box = BoxAnnotation(left = self.tme(comm.start).timestamp() * 1000, right = self.tme(comm.stop).timestamp() * 1000, fill_alpha = 0.1, fill_color = "#99FF99")
				p.add_layout(low_box)

			d = p.scatter(x = 'utc_times', y = 'msid_values', source = source,
						 color = {'field': 'label', 'transform': color_mapper}, 
						 line_color = None, size = 2, legend_group = 'label')

			new_legend = p.legend[0]
			p.add_layout(new_legend, 'right')

			frames.append([p])
			#print ("frame time: ", timeit.default_timer()-start_plot)
		s = gridplot(frames)
		#print ("full plots: ", timeit.default_timer()-start_plots)
		start_time = timeit.default_timer()		
		script, div = components(s)
		with open(f"{OUT_DIR}/{script_name}", 'w') as f:
			f.write(script)
		with open(f"{OUT_DIR}/{div_name}", 'w') as f:
			f.write(div)
		#print ('saved plots: ', timeit.default_timer()-start_time)

