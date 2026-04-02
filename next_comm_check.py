#!/usr/bin/env python
"""
**next_comm_check.py**: create a display time span till the next comm

:Author: T. Isobe (tisobe@cfa.harvard.edu)
:Maintainer: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Jun 05, 2024

# /// testing
# tested-ska-release = "2026.1"
# ///
"""

import os
from cxotime import CxoTime
import argparse
from pathlib import Path

SOH_WEB_DIR = Path(os.getenv("SOH_WEB_DIR", "/data/mta4/www/CSH"))

#-------------------------------------------------------------------
#-- find_next_comm: create a display time span till the next comm --
#-------------------------------------------------------------------

def find_next_comm():
    """
    create a display time span till the next comm
    input:  none, but read from {HTML_DIR}/comm_list.html
    output: {HTML_DIR}/ncomm.xml
    """
    ctime = CxoTime().secs
    _comm_list_file = SOH_WEB_DIR / "comm_list.html"
    with open(_comm_list_file) as f:
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
            break
        elif (ctime >= start) and (ctime <= stop):
            diff = stop - ctime
            hour, remainder = divmod(int(diff),3600)
            minute = minute = remainder//60
            ltime = f"End of Comm In:  {hour:>02}:{minute:>02}"
            break
        else:
            pstop = stop
    _ncomm_xml = SOH_WEB_DIR / "ncomm.xml"
    with open(_ncomm_xml, 'w') as fo:
        fo.write(f"<ncomm>\n{ltime}\n</ncomm>\n")

#-------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to web file location")
    args = parser.parse_args()
    if args.mode == "test":
        if args.path:
            SOH_WEB_DIR = Path(args.path)
        else:
            SOH_WEB_DIR = Path(os.getcwd(), "test", "_outTest")
        os.makedirs(SOH_WEB_DIR, exist_ok = True)
    
    find_next_comm()