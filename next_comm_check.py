#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#########################################################################################
#                                                                                       #
#   next_comm_check.py: create a display time span till the next comm                   #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Sep 16, 2020                                                       #
#                                                                                       #
#########################################################################################

import os
import sys
import re
import string
import math
import time
import Chandra.Time


house_keeping = '/data/mta/Script/SOH/house_keeping/'

#-------------------------------------------------------------------
#-- find_next_comm: create a display time span till the next comm --
#-------------------------------------------------------------------

def find_next_comm():
    """
    create a display time span till the next comm
    input:  nont, but read from /data/mta4/www/CSH/comm_list.html
    output: /data/mta/www/CSH/ctest
    """
    out = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    ctime = Chandra.Time.DateTime(out).secs
    
    with open('/data/mta_www/MIRROR/CSH/comm_list.html', 'r') as f:
        data = [line.strip() for line in f.readlines()]
    
    pstop = 0.0
    limte = 'n/a'
    for ent in data[11:]:
        atemp = re.split('<td>', ent)
        start = atemp[1].replace('</td>','')
        start = Chandra.Time.DateTime(start).secs
        stop  = atemp[3].replace('</td></tr>','')
        stop  = Chandra.Time.DateTime(stop).secs
    
        if (ctime > pstop) and (ctime < start):
            diff = start - ctime
            ltime = 'Next Comm In: '   + convert_to_hour(diff)
            write_to_hk(diff)
            break
        elif (ctime >= start) and (ctime <= stop):
            diff = stop - ctime
            ltime = 'End of Comm In: ' + convert_to_hour(diff)
            write_to_hk(0.0)
            break
        else:
            pstop = stop

    with open('/data/mta_www/MIRROR/CSH/ctest', 'w') as fo:
        fo.write(ltime + '\n')
    
#-------------------------------------------------------------------
#-------------------------------------------------------------------
#-------------------------------------------------------------------

def convert_to_hour(stime):

    hour = int(stime /3600)
    diff = stime - hour * 3600
    mm   = int(diff/60)

    ltime = adjust_digit(hour) + ':' + adjust_digit(mm)

    return ltime
    
#-------------------------------------------------------------------
#-------------------------------------------------------------------
#-------------------------------------------------------------------

def adjust_digit(val):

    val  = int(val)
    sval = str(val)
    if val < 10:
        sval = '0' + sval

    return sval

    
#-------------------------------------------------------------------
#-------------------------------------------------------------------
#-------------------------------------------------------------------

def write_to_hk(diff):

    line  = str(diff) + '\n'
    ofile = house_keeping + 'stime_to_comm'
    with open(ofile, 'w') as fo:
        fo.write(line)
    
    
#-------------------------------------------------------------------

if __name__ == '__main__':

    find_next_comm()
