#!/proj/sot/ska3/flight/bin/python
"""
**read_comm_time.py**: read comm time from aspect site

:Author: T. Isobe (tisobe@cfa.harvard.edu)
:Maintainer: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Dec 09, 2024

# /// testing
# tested-ska-release = "2026.1"
# ///
"""

import os
from cxotime import CxoTime
import argparse

#
#--- Define Directory Pathing
#
HOUSE_KEEPING = "/data/mta4/Script/SOH/house_keeping"
HTML_DIR = "/data/mta4/www/CSH"
ARC_DIR = "/data/mta4/www/ASPECT/arc"
DISREGARD_PAST_COMMS = True

#-------------------------------------------------------------------------------
#-- find_comm_pass: read comm pass from aspect site                           --
#-------------------------------------------------------------------------------

def find_comm_pass():
    """
    read comm pass form aspect site
    input:  none but read from http://cxc.harvard.edu/mta/ASPECT/arc/'
    output: <house_keeping>/comm_list --- <start time>\t<start time in sec>\t<stop time in sec>
            <html_dir>/comm_list.html
    """
#
#--- start writing comm_list.html top part
#
    hline = '<!DOCTYPE html>\n <html>\n <head>\n'
    hline += '<title>Comm Timing List</title>\n'
    hline += '<link href="css/custom.css" rel="stylesheet">\n'
    hline += '</head>\n<body>\n'
    hline += '<div style="margin-left:60px;">\n'
    hline += '<h2>Comm Timing List</h2>\n'
    hline += '<table>\n'
    hline += '<tr><th style="text-align:center;">Start</th><td>&#160;</td>'
    hline += '<th style="text-align:center;">Stop</th></tr>\n'

    now = CxoTime().secs

    with open(f"{ARC_DIR}/index.html") as f:
        data = [line.strip() for line in f.readlines()]

    sline = ''
    for ent in data:
        if 'Comm pass' in ent:
            atemp = ent.split('<tt>')
            btemp = atemp[1].split('</tt>')
            ctime = btemp[0]

            atemp = ent.split('duration')
            btemp = atemp[1].split(')')
            dur = btemp[0].strip()
            atemp = dur.split(':')
            dur   = int((float(atemp[0]) + float(atemp[1]) / 60.0) * 3600.0)

            start = int(CxoTime(ctime).secs)
            stop  = start + dur

            if DISREGARD_PAST_COMMS:
                if stop < now:
                    continue
#
#--- data table input
#
            sline += f"{ctime}\t{start}\t{stop}\n" 
#
#--- html page input
#
            hline += f"<tr><td>{ctime}</td><td>&#160;</td><td>{CxoTime(stop).date}</td></tr>\n"
#
#--- write out the comm list data
#
    with open(f"{HOUSE_KEEPING}/comm_list", 'w') as fo:
            fo.write(sline)
#
#--- finish html page
#
    hline += '</table>\n'
    hline += '<p style="padding-top:5px;"> Time is in <b><em>UT</em></b> </p>\n'
    hline += '</div>\n'
    hline += '</body>\n</html>\n'

    with open(f"{HTML_DIR}/comm_list.html", 'w') as fo:
        fo.write(hline)


#-------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("--arc_dir", required = False, help = f"Determine arc data location. (default={ARC_DIR})")
    parser.add_argument("--html_dir", required = False, help = f"Determine web output location. (default={HTML_DIR})")
    args = parser.parse_args()

    if args.mode == "test":
        DISREGARD_PAST_COMMS = False
        if args.arc_dir:
            ARC_DIR = args.arc_dir
        if args.html_dir:
            HTML_DIR = args.html_dir
        else:
            HTML_DIR = f"{os.getcwd()}/test/_outTest"
        HOUSE_KEEPING = f"{os.getcwd()}/test/_outTest"
        os.makedirs(HOUSE_KEEPING, exist_ok = True)
        os.makedirs(HTML_DIR, exist_ok = True)
        find_comm_pass()

    elif args.mode == "flight":
        find_comm_pass()
