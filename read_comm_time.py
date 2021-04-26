#!/usr/bin/env /data/mta4/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#           read_comm_time.py: read comm time from aspect site                      #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 15, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import math
import time
import Chandra.Time
#
path = '/data/mta4/Script/SOH/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)
#
#--- set a temporary file name
#
import random
rtail  = int(time.time()*random.random())
zspace = '/tmp/zspace' + str(rtail)

#-------------------------------------------------------------------------------
#-- find_comm_pass: read comm pass from aspect site                           --
#-------------------------------------------------------------------------------

def find_comm_pass():
    """
    read comm pass form aspect site
    input:  none but read from http://cxc.harvard.edu/mta/ASPECT/arc/'
    output: <house_keeping>/comm_list --- <start time>\t<start time in sec>\t<steop time in sec>
            <html_dir>/comm_list.html
    """
#
#--- start writing comm_list.html top part
#
    hline = '<!DOCTYPE html>\n <html>\n <head>\n'
    hline = hline + '<title>Comm Timing List</title>\n'
    hline = hline + '<link href="css/custom.css" rel="stylesheet">\n'
    hline = hline + '</head>\n<body>\n'
    hline = hline + '<div style="margin-left:60px;">\n'
    hline = hline + '<h2>Comm Timing List</h2>\n'
    hline = hline + '<table>\n'
    hline = hline + '<tr><th style="text-align:center;">Start</th><td>&#160;</td>'
    hline = hline + '<th style="text-align:center;">Stop</th></tr>\n'


    now = time.strftime("%Y:%j:%H:%M:%S", time.gmtime())
    now = Chandra.Time.DateTime(now).secs

    cmd = 'wget -q -O' + zspace + ' http://cxc.harvard.edu/mta/ASPECT/arc/'
    os.system(cmd)

    data = read_data_file(zspace, remove=1)

    sline = ''
    for ent in data:
        mc  = re.search('Comm pass', ent)
        if mc is not None:
            atemp = re.split('<tt>', ent)
            btemp = re.split('<\/tt>', atemp[1])
            ctime = btemp[0]

            atemp = re.split('duration', ent)
            btemp = re.split('\)', atemp[1])
            dur   = (btemp[0].strip())
            atemp = re.split(':', dur)
            dur   = int((float(atemp[0]) + float(atemp[1]) / 60.0) * 3600.0)

            start = int(Chandra.Time.DateTime(ctime).secs)
            stop  = start + dur

            if stop < now:
                continue
#
#--- data table input
#
            sline  = sline + ctime + '\t' + str(start) + '\t' + str(stop) + '\n'
#
#--- html page input
#
            #dstart = Chandra.Time.DateTime(start).date
            #dstop  = Chandra.Time.DateTime(stop).date
            dstart = convert_time_format(start)
            dstop  = convert_time_format(stop)
            hline  = hline + '<tr><td>' + str(dstart) 
            hline  = hline + '</td><td>&#160;</td><td>' + str(dstop) + '</td></tr>\n'
#
#--- write out the comm list data
#
    outfile = house_keeping + 'comm_list'
    with open(outfile, 'w') as fo:
            fo.write(sline)
#
#--- finish html page
#
    hline = hline + '</table>\n'
    hline = hline + '<p style="padding-top:5px;"> Time is in <b><em>UT</em></b> </p>\n'
    hline = hline + '</div>\n'
    hline = hline + '</body>\n</html>\n'

    wcomm = html_dir + 'comm_list.html'
    with open(wcomm, 'w') as fo:
        fo.write(hline)

#-------------------------------------------------------------------------------
#-- convert_time_format: add a fadge factor to make time format better        --
#-------------------------------------------------------------------------------

def convert_time_format(ctime):
    """
    add a fadge factor to make time format better
    input:  ctime   --- chandra time; seconds from 1998.1.1
    output: rtime   --- time in <yyyy>:<ddd>:<hh>:<mm>:<ss>
    """

    ctime += 0.2    #--- adding 0.2 seconds to chandra time. this could be different in future

    otime  = Chandra.Time.DateTime(ctime).date
    atemp  = re.split(':', otime)
    btemp  = re.split('\.', atemp[4])

    rtime  = atemp[0] + ':' + atemp[1] + ':' + atemp[2] + ':' + atemp[3] + ':' + btemp[0]

    return rtime

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):

    with open(ifile, 'r') as f:
        data = [line.strip() for line in f.readlines()]

    if remove  == 1:
        cmd = 'rm -rf ' + ifile
        os.system(cmd)

    return data



#-------------------------------------------------------------------------------

if __name__ == "__main__":

    find_comm_pass()
