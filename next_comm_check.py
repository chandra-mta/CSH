#!/proj/sot/ska3/flight/bin/python

#########################################################################################
#                                                                                       #
#   next_comm_check.py: create a display time span till the next comm                   #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last update: Jun 05, 2024                                                       #
#                                                                                       #
#########################################################################################
import os
from datetime import datetime, timezone
from cxotime import CxoTime
import argparse


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
    ctime = CxoTime(datetime.now(timezone.utc)).secs
    
    with open(f"{HTML_DIR}/comm_list.html") as f:
        data = [line.strip() for line in f.readlines()]
    
    pstop = 0.0
    for ent in data[11:]:
        atemp = ent.split('<td>')
        start = atemp[1].replace('</td>','')
        start = CxoTime(start).secs
        stop  = atemp[3].replace('</td></tr>','')
        stop  = CxoTime(stop).secs
    
        if (ctime > pstop) and (ctime < start):
            diff = start - ctime
            hour, remainder = divmod(int(diff),3600)
            minute = minute = remainder//60
            ltime = f"Next Comm In:  {hour:>02}:{minute:>02}"
            with open(f"{HOUSE_KEEPING}/stime_to_comm", 'w') as fo:
                fo.write(f"{diff:.1f}\n")
            break
        elif (ctime >= start) and (ctime <= stop):
            diff = stop - ctime
            hour, remainder = divmod(int(diff),3600)
            minute = minute = remainder//60
            ltime = f"End of Comm In:  {hour:>02}:{minute:>02}"
            with open(f"{HOUSE_KEEPING}/stime_to_comm", 'w') as fo:
                fo.write(f"{0.0}\n")
            break
        else:
            pstop = stop

    with open(f"{OUT_HTML_DIR}/ctest.xml", 'w') as fo:
        fo.write(f"<ncomm>\n{ltime}\n</ncomm>\n")

#-------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    args = parser.parse_args()

    if args.mode == "test":
        OUT_HTML_DIR = f"{os.getcwd()}/test/_outTest"
        HOUSE_KEEPING = OUT_HTML_DIR
        os.makedirs(OUT_HTML_DIR, exist_ok = True)
        find_next_comm()

    elif args.mode == "flight":
        find_next_comm()
