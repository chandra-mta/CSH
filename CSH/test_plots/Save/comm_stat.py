#!/proj/sot/ska3/flight/bin/python
import os
from kadi import events
from datetime import datetime, timedelta, time
import Chandra.Time

def tme(x):
        return (datetime.strptime(Chandra.Time.DateTime(x).date, '%Y:%j:%H:%M:%S.%f'))

#necessary function due to how chandra events gives us time
def tracktime(bot, tstart, eot, tstop): #track, ttime): 
        comm_day = tme(tstart)       
        bot_time, eot_time = datetime.strptime(bot, '%H%M').time(), datetime.strptime(eot, '%H%M').time()
        comm_start, comm_stop = datetime.combine(comm_day.date(), bot_time), datetime.combine(comm_day.date(), eot_time)
        if (comm_day.time() >= time(23,0) and eot_time <= time(1,0)):
                comm_day = comm_day + timedelta(1)
                comm_stop = datetime.combine(comm_day.date(), eot_time)
        return (comm_start, comm_stop)


now = datetime.utcnow()
today = datetime(now.year, now.month, now.day)
yesterday = today - timedelta(1)
tomorrow = today + timedelta(1)
dsn_comms = events.dsn_comms.filter(yesterday, tomorrow)
in_comm = False
for comm_event in dsn_comms:
        comm_start, comm_stop = tracktime(comm_event.bot, comm_event.tstart, comm_event.eot, comm_event.tstop)
        print (comm_start, comm_stop)
        if (now >= comm_start and now <= comm_stop):
                in_comm = True
                with open('/data/mta4/www/CSH/test_plots/.in_comm', 'w') as f:
                        f.write(str(comm_stop))
                with open('/data/mta4/www/CSH_ASVT/test_plots/.in_comm', 'w') as f:
                        f.write(str(comm_stop))
			
        elif (now > comm_stop):
                with open('/data/mta4/www/CSH/test_plots/.last_comm', 'w') as f:
                        f.write(str(comm_stop))
                with open('/data/mta4/www/CSH_ASVT/test_plots/.last_comm', 'w') as f:
                        f.write(str(comm_stop))

if not in_comm and os.path.exists('.in_comm'):
    os.remove('.in_comm')
