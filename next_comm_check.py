#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#   next_comm_check.py: create a display time span till the next comm                   #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Mar 15, 2021                                                       #
#                                                                                       #
#########################################################################################
import re
import time
import Chandra.Time


HOUSE_KEEPING = '/data/mta4/Script/SOH/house_keeping'
HTML_DIR = "/data/mta4/www/CSH"
OUT_HTML_DIR = HTML_DIR

#-------------------------------------------------------------------
#-- find_next_comm: create a display time span till the next comm --
#-------------------------------------------------------------------

def find_next_comm():
    """
    create a display time span till the next comm
    input:  none, but read from {HTML_DIR}/comm_list.html
    output: {HTML_DIR}/ctest.xml
            {HTML_DIR}/ncomm
    """
    out = time.strftime('%Y:%j:%H:%M:%S', time.gmtime())
    ctime = Chandra.Time.DateTime(out).secs
    
    with open(f"{HTML_DIR}/comm_list.html") as f:
        data = [line.strip() for line in f.readlines()]
    
    pstop = 0.0
    for ent in data[11:]:
        atemp = re.split('<td>', ent)
        start = atemp[1].replace('</td>','')
        start = Chandra.Time.DateTime(start).secs
        stop  = atemp[3].replace('</td></tr>','')
        stop  = Chandra.Time.DateTime(stop).secs
    
        if (ctime > pstop) and (ctime < start):
            diff = start - ctime
            ltime = 'Next Comm In: '   + convert_to_hour(diff)
            with open(f"{HOUSE_KEEPING}/stime_to_comm", 'w') as fo:
                fo.write(f"{diff}\n")
            break
        elif (ctime >= start) and (ctime <= stop):
            diff = stop - ctime
            ltime = 'End of Comm In: ' + convert_to_hour(diff)
            with open(f"{HOUSE_KEEPING}/stime_to_comm", 'w') as fo:
                fo.write(f"{0.0}\n")
            break
        else:
            pstop = stop

    with open(f"{OUT_HTML_DIR}/ctest.xml", 'w') as fo:
        fo.write(f"<ncomm>\n{ltime}\n</ncomm>\n")
    
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

if __name__ == '__main__':

    find_next_comm()
