#!/usr/bin/env /data/mta4/Script/Python3.6/envs/ska3/bin/python

import os
from kadi import events
from datetime import datetime, timedelta, time
import Chandra.Time
import signal
import pandas as pd
import requests 
import time as t

def tme(x):
		return (datetime.strptime(Chandra.Time.DateTime(x).date, '%Y:%j:%H:%M:%S.%f'))

def tracktime(track, ttime):
	comm_day = tme(ttime)
	track_time = datetime.strptime(track, '%H%M').time()
	if (comm_day.time() >= time(23,0) and track_time < time(1,0)):
		comm_day = comm_day + timedelta(1)
	return( datetime.combine(comm_day.date(), track_time) )

def pull_comm_schedule():
	########################
	# dsn_comm function gets our comm events calendar using kadi
	# these events are turned into a pandas dataframe with an IntervalIndex
	# this IntervalIndex facilitates lookup
	# This dataframe is saved to the instance variable int_df
	#######################
	now = datetime.utcnow()
	yesterday = now - timedelta(1)
	tomorrow = now + timedelta(1)
	yesterday_start= Chandra.Time.DateTime(yesterday).day_start()
	tomorrow_end = Chandra.Time.DateTime(tomorrow).day_end()
	dsn_comms = events.dsn_comms.filter(yesterday_start.date, tomorrow_end.date)
	dsn_comms = dsn_comms
	#create dsn_intervals
	dsn_intervals = []
	for dsn_i , comm_event in enumerate(dsn_comms):
		comm_start, comm_stop = tracktime(comm_event.bot, comm_event.tstart) , tracktime(comm_event.eot, comm_event.tstop)
		dsn_intervals += [comm_start, comm_stop]
	#we are creating intervals based on the comm schedule, this will tell us whether it's comm or not
	#but it's an uneven number
	comm_vals = ([True, False]*int(len(dsn_intervals)/2))[:-1]
	int_df = pd.DataFrame(comm_vals, index = pd.IntervalIndex.from_breaks(dsn_intervals, closed='right'))
	return int_df

	#taken from maude code
def get_user_password():
	import Ska.ftp
	#netrc = Ska.ftp.parse_netrc()
	netrc = Ska.ftp.parse_netrc('/data/mta4/Script/SOH/house_keeping/.netrc')
	if 'occweb' in netrc:
		user = netrc['occweb']['login']
		password = netrc['occweb']['password']
	else:
		raise ValueError('user and password or "occweb" machine definition in ~/.netrc are '
						 'required for OCCweb authentication')
	return user, password

def check_site(now):
	user, password = get_user_password()
	site = 'https://telemetry.cfa.harvard.edu/maude/mrest/FLIGHT/{}.json?tp={}&nearest=t'
	tp = datetime.strftime(now, '%Y.%j.%H.%M')
	url = site.format('AORATE1', tp)
	r = requests.get(url, headers = {'Accept-Encoding': 'gzip'}, auth=(user, password))
	if r.status_code != 200:
		raise IOError('request failed with status={} for URL={} and text={}'.format(r.status_code, r.url, r.text))
	out = r.json()

	last_point = datetime.strptime(str(out['data-fmt-1']['times'][0]), '%Y%j%H%M%S%f')
	return (last_point)

def monitor_comms(comm_intervals, path):
	user, password = get_user_password()
	in_comm = False
	while True:
		now = datetime.utcnow()
		comm_scheduled = comm_intervals.loc[pd.Timestamp(now)][0]
		sleep_time = 0
		#if a comm is scheduled but we're not in comm
		if (comm_scheduled and not in_comm):
			last_point = check_site(now)
			in_comm = True if ((now - last_point).seconds < 300) else False
			#sleep for 3 minutes, since a comm was scheduled we'll want to check again soon
			sleep_time = 180
		#if a comm is not scheduled let's check just in case
		elif (not comm_scheduled and not in_comm):
			last_point = check_site(now)
			in_comm = True if ((now - last_point).seconds < 300) else False
			#sleep for 5 minutes 
			sleep_time = 300
		elif (comm_scheduled and in_comm):
			sleep_time = 300
		elif (not comm_scheduled and in_comm):
			last_point = check_site(now)
			in_comm = True if ((now - last_point).seconds < 300) else False
			sleep_time = 60
		else: 
			print ("Unknown comm_config (sched, in): ", comm_scheduled, in_comm)
			sleep_time = 60

		in_comm_path = path + '.in_comm'
		comm_stop_path = path + '.last_comm'
		if (in_comm and comm_scheduled):
			comm_interv = comm_intervals.loc[pd.Timestamp(now)].name
			comm_start, comm_stop = comm_interv.left.to_pydatetime() , comm_interv.right.to_pydatetime()
			print (comm_start, comm_stop)
			with open(in_comm_path, 'w') as f:
				f.write(str(comm_stop))
			with open(comm_stop_path, 'w') as f:
				f.write(str(comm_stop))
		if (not in_comm and os.path.exists('.in_comm')):
			os.remove(in_comm_path)
		if ((not os.path.exists(comm_stop_path) or os.stat(comm_stop_path).st_size ==0) and not in_comm):
			comm_interv = comm_intervals.loc[pd.Timestamp(now)].name
			comm_stop = comm_interv.left.to_pydatetime()
			print("hello", comm_stop)
			with open(comm_stop_path, 'w') as f:
				f.write(str(comm_stop))
		t.sleep(sleep_time)


def signal_handler(signum, frame):
    raise Exception("time is done")


if __name__ == '__main__':
	comm_intervals = pull_comm_schedule()
	signal.signal(signal.SIGALRM, signal_handler)
	signal.alarm(3650)
	try:
		path = '/data/mta4/www/CSH/test_plots/'
		monitor_comms(comm_intervals, path)
	except Exception as msg:
		print (msg)
		
