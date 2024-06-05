#!/proj/sot/ska3/flight/bin/python

#####################################################################################
#                                                                                   #
#           read_comm_time.py: read comm time from aspect site                      #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Jun 05, 2024                                               #
#                                                                                   #
#####################################################################################

import os
import re
import time
import Chandra.Time

#
#--- Define Directory Pathing
#
HOUSE_KEEPING = "/data/mta4/Script/SOH/house_keeping"
HTML_DIR = "/data/mta4/www/CSH"
ARC_DIR = "/data/mta4/www/ASPECT/arc"

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

    with open(f"{ARC_DIR}/index.html") as f:
        data = [line.strip() for line in f.readlines()]

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
            dstart = convert_time_format(start)
            dstop  = convert_time_format(stop)
            hline  = hline + '<tr><td>' + str(dstart) 
            hline  = hline + '</td><td>&#160;</td><td>' + str(dstop) + '</td></tr>\n'
#
#--- write out the comm list data
#
    with open(f"{HOUSE_KEEPING}/comm_list", 'w') as fo:
            fo.write(sline)
#
#--- finish html page
#
    hline = hline + '</table>\n'
    hline = hline + '<p style="padding-top:5px;"> Time is in <b><em>UT</em></b> </p>\n'
    hline = hline + '</div>\n'
    hline = hline + '</body>\n</html>\n'

    with open(f"{HTML_DIR}/comm_list.html", 'w') as fo:
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

if __name__ == "__main__":

    find_comm_pass()
