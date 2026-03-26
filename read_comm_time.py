#!/usr/bin/env python
"""
**read_comm_time.py**: read comm time from aspect site

:Author: T. Isobe (tisobe@cfa.harvard.edu)
:Maintainer: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 26, 2026

# /// testing
# tested-ska-release = "2026.1"
# ///
"""

import os
from cxotime import CxoTime
import argparse
from pathlib import Path
#
#--- Define Directory Pathing
#
SOH_WEB_DIR = Path(os.getenv("SOH_WEB_DIR", "/data/mta4/www/CSH"))
ARC_DIR = Path("/data/mta4/www/ASPECT/arc")
DISREGARD_PAST_COMMS = True

#-------------------------------------------------------------------------------
#-- find_comm_pass: read comm pass from aspect site                           --
#-------------------------------------------------------------------------------

def find_comm_pass():
    """
    read comm pass form aspect site
    input:  none but read from http://cxc.harvard.edu/mta/ASPECT/arc/'
    output: <soh_web_dir>/comm_list.html
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
    _arc_file = ARC_DIR / "index.html"
    with open(_arc_file) as f:
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
#--- finish html page
#
    hline += '</table>\n'
    hline += '<p style="padding-top:5px;"> Time is in <b><em>UT</em></b> </p>\n'
    hline += '</div>\n'
    hline += '</body>\n</html>\n'
    _comm_list_file = SOH_WEB_DIR / "comm_list.html"
    with open(_comm_list_file, 'w') as fo:
        fo.write(hline)


#-------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of comm html file.")
    args = parser.parse_args()

    if args.mode == "test":
        DISREGARD_PAST_COMMS = False
        if args.path:
            SOH_WEB_DIR = Path(args.path)
        else:
            SOH_WEB_DIR = Path(os.getcwd(), "test", "_outTest")
        os.makedirs(SOH_WEB_DIR, exist_ok=True)
    find_comm_pass()