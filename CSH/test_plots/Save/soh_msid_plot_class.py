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
import Ska.engarchive.fetch as fetch
from datetime import datetime, timedelta, time
import Chandra.Time
import pickle
import os, getpass
print ("Login info",os.getlogin()," user info:" ,getpass.getuser())
import numexpr as ne
#import maude
fetch.data_source.set('maude')


class soh_plots:

	def __init__(self):
		#msid_dictionary created in msididx_dict_formatter.py
		limit_file = 'msid_limits.pickle'
		pickle_in = open(limit_file, "rb")
		self.msid_dict = pickle.load(pickle_in)

		#general time 
		now = datetime.utcnow()
		yesterday = now - timedelta(1)
		tomorrow = now + timedelta(1)
		yesterday_start= Chandra.Time.DateTime(yesterday).day_start()
		tomorrow_end = Chandra.Time.DateTime(tomorrow).day_end()
		self.in_comm = False
		self.start_time = None
		#are we in comm? If not when was the last comm. 
		dsn_comms = events.dsn_comms.filter(yesterday_start.date, tomorrow_end.date)
		self.next_comm = None

		#find when the next comm is going to be and let me know if we're currently
		#in comm
		for dsn_i,comm_event in enumerate(dsn_comms):
			comm_start, comm_stop = self.tracktime(comm_event.bot, comm_event.tstart) , self.tracktime(comm_event.eot, comm_event.tstop)
			print (now, comm_start, comm_stop)
			if (now >= comm_start and now <= comm_stop):
				self.in_comm = True
				self.start_time = comm_start
			if not self.in_comm: #find the last comm that occured
				if now > comm_stop:
					self.start_time = self.tracktime(dsn_comms[dsn_i-1].bot, dsn_comms[dsn_i-1].tstart) if dsn_i > 0 else comm_start
			if (now<comm_start and self.next_comm is None): #assumes order
				self.next_comm = comm_start
		self.dsn_comms = dsn_comms
		#vectorized functions
		self.change_time = np.vectorize(self.tme)
		self.calc = np.vectorize(self.msid_weight)
		self.color_choice_set = np.vectorize(self.color_equalities)
		self.color_choice_switch = np.vectorize(self.switch_color)
		self.switch = np.vectorize(self.switch_lookup)

	#returns chandra time as a datetime object
	def tme(self, x):
		return (datetime.strptime(Chandra.Time.DateTime(x).date, '%Y:%j:%H:%M:%S.%f'))

	def tracktime(self, track, ttime):
		comm_day = self.tme(ttime)
		track_time = datetime.strptime(track, '%H%M').time()
		if (comm_day.time() >= time(23,0)):
			comm_day = comm_day + timedelta(1)
		return( datetime.combine(comm_day.date(), track_time) )


	#multiplies numbers by a weight
	def msid_weight(self, x, weight):
		return (x*weight)

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
	
	def switch_color(self, msid_value, msid_limit, weight):
		if (msid_limit is None):
			return ("Normal")
		low_red , low_yellow = msid_limit['wl']*weight, msid_limit['cl']*weight
		hi_red, hi_yellow = msid_limit['wh']*weight, msid_limit['ch']*weight
		#print (msid_value, low_red, low_yellow, hi_red, hi_yellow)
		return (self.color_equalities(msid_value, low_red, low_yellow, hi_red, hi_yellow))


	def switch_lookup(self, msid_info, point):
		if point in msid_info['switch_lim']['switch']:
			return (msid_info['switch_lim']['switch'][point])

	def return_dependent(self, msid):
		if ('switch_lim' in self.msid_dict[msid]):
			dependent = self.msid_dict[msid]['switch_lim']['dependent']
			return (dependent)

	def return_limit_colors(self, msid, msid_vals, set_data, weight):
		msid_info = self.msid_dict[msid]
		dep = self.return_dependent(msid)
		if ('set_lim' in msid_info):
			low_red , low_yellow = msid_info['set_lim']['wl']*weight, msid_info['set_lim']['cl']*weight
			hi_red, hi_yellow = msid_info['set_lim']['wh']*weight, msid_info['set_lim']['ch']*weight
			return (self.color_choice_set(msid_vals, low_red, low_yellow, hi_red, hi_yellow))
		elif ('switch_lim' in msid_info):
			#here we need to go through the possible values our dependent could be
			#because msids have different time steps (1) create intervals 
			#(2) return the right limit for that interval 
			msid_limits = np.empty(len(set_data[msid]), dtype = dict)
			for val in self.msid_dict[msid]['switch_lim']['switch'].keys():
				val_intervals = set_data[dep].logical_intervals('==', val, complete_intervals = False)
				interval_msid = set_data[msid].select_intervals(val_intervals, copy = True)
				msid_bool = np.in1d(set_data[msid].times, interval_msid.times)
				msid_limits[msid_bool] = self.msid_dict[msid]['switch_lim']['switch'][val]
			return (self.color_choice_switch(msid_vals, msid_limits, weight))

	def plot_joint_graphs(self, pull_set, group_name, msid_list, weight, units, title,  dep_list, file_name):
		start_time = timeit.default_timer()
		print ("begin", timeit.default_timer()-start_time)
		script_name = 'script_' + group_name
		div_name = 'div_' + group_name
		try:
			set_data = fetch.MSIDset(pull_set, self.start_time)
		except Exception as ex:
			for excs in ex.args:
				if "MAUDE query failed" in excs:
					with open(script_name, 'w') as f:
						f.write("<font color=\"red\"><b>Sorry, Maude couldn't fetch the data from the last comm</font>")
			return
		print ("pulled set data", timeit.default_timer()-start_time)
		now = datetime.utcnow()
		frames = []
		for frame, msid in enumerate(msid_list):
			data = set_data[msid]
			#print ("got subset", timeit.default_timer()-start_time)
			print (len(data.times), len(data.vals))
			#comm_data = data.select_intervals(events.dsn_comms, copy = True)
			#print (comm_data.times)
			t1998 = 883612736.816
			data_tme, data_vals = data.times, data.vals
			data_times = np.array(ne.evaluate('data_tme + t1998'), dtype='u8').view('datetime64[s]')
			data_values = ne.evaluate('data_vals*weight')
			#data_times , data_values = self.change_time(data.times), self.calc(data.vals, weight)
			#comm_times, comm_values = self.change_time(comm_data.times), self.calc(comm_data.vals, weight)
			#print ("translated data", timeit.default_timer()-start_time)
			nxt_comm = "Currently in comm" if self.in_comm else self.next_comm.strftime('%Y:%j:%H:%M')
			plot_title = """%s
			Last updated: %s
			Next DSN Comm: %s """%(title, now.strftime('%Y:%j:%H:%M'),nxt_comm)
			y_label = msid + " (" + units + ")"
			if frame > 0:
				p = figure(title=plot_title, x_axis_label = 'Time (UTC)', y_axis_label= y_label, 
						   x_range = frames[0][0].x_range, x_axis_type = "datetime",
						  plot_width = 700, plot_height = 300)
			else:
				p = figure(title=plot_title, x_axis_label = 'Time (UTC)', y_axis_label= y_label,
						   x_axis_type = "datetime", plot_width = 700, plot_height = 300)
			print ("frame_time", timeit.default_timer()-start_time) 
			p.xaxis.formatter = DatetimeTickFormatter(
				minutes = ["%Y:%j:%H:%M"],
				hours = ["%Y:%j:%H"],
				hourmin = ["%Y:%j:%H:%M"],
				days = ["%Y:%j"]
			)
			
			if 'lim' in self.msid_dict[msid]:
				colors = self.return_limit_colors(msid, data_values, set_data, weight)
			else:
				colors = np.full((1,len(data_values)),'Normal')[0]
			#print ("limit_colors", timeit.default_timer()-start_time) 
			source = ColumnDataSource(dict(
				utc_times = data_times,
				msid_values = data_values,
				label = colors
			))
			#print ("source", timeit.default_timer()-start_time) 
			color_mapper = CategoricalColorMapper(factors = ['Normal','High-red','Low-red','Low-yellow','High-yellow'],
												 palette = [Plasma5[0],Plasma5[1],Plasma5[2],Plasma5[3],Plasma5[4]]
												 )
			#print ("color_mapper", timeit.default_timer()-start_time) 
			for comm in self.dsn_comms:
				low_box = BoxAnnotation(left = self.tme(comm.start), right = self.tme(comm.stop), fill_alpha = 0.1, fill_color = "#99FF99")
				p.add_layout(low_box)
			#print ("box annotation", timeit.default_timer()-start_time) 
			d = p.circle(x = 'utc_times', y = 'msid_values', source = source,
						 color = {'field':'label', 'transform':color_mapper}, 
						 line_color=None, size = 2, legend = 'label')
			#print ("circles", timeit.default_timer()-start_time) 
			new_legend = p.legend[0]
			p.legend[0].plot = None
			p.add_layout(new_legend, 'right')

			frames.append([p])

		s = gridplot(frames)
		script, div = components(s)
		with open(script_name, 'w') as f:
			f.write(script)
		with open(div_name, 'w') as f:
			f.write(div)

