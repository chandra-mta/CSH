#!/usr/bin/env python
"""
**csh_limits_supplemental.py**: Generate supplemental limit information for Maude CSH website.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Mar 30, 2026

# /// testing
# tested-ska-release = "2026.1"
# ///

"""

import os
import shutil
import sqlite3 as sq
from contextlib import closing
import json
import argparse
import requests
from urllib.parse import urlparse
from pathlib import Path
#
#--- Define Directory Pathing
#
GLIMMON_FILE = Path("/data/mta/Script/MSID_limit/glimmondb.sqlite3")
OCC_LINK = "https://occweb.cfa.harvard.edu/occweb/web/fot_web/software/sandbox/SOT_area/msididx.json"

SOH_DIR = Path(os.getenv("SOH_DIR", "/data/mta4/Script/SOH"))
SOH_WEB_DIR = Path(os.getenv("SOH_WEB_DIR", "/data/mta4/www/CSH"))
SCRIPT_DIR = Path(__file__).parent
HOUSE_KEEPING = SCRIPT_DIR / "house_keeping"

SEARCH_TERMS = "datesec, warning_low, warning_high, caution_low, caution_high"

def _filename(url):
    return os.path.basename(urlparse(url).path)

def _get_json(url):
    with requests.get(url) as response:
        _json = response.json()
    return _json

def get_options(args=None):
    parser = argparse.ArgumentParser(description="Generate CSH supplemental files")
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    opt = parser.parse_args(args)
    return opt

def mta_msididx_alterations(msididx):
    #: Include MTA Alterations
    for i in range(len(msididx)):
        if msididx[i]['name'] in ["AORATE1", "AORATE2", "AORATE3", "AOGBIAS1", "AOGBIAS2", "AOGBIAS3"]:
            msididx[i]['description'] += " (*206265)" #Include CSH Conversion into Description
        
        elif msididx[i]['name'] in ["AODITHR2", "AODITHR3"]:
            msididx[i]['description'] += " (*3600)"
    
    #: Include MTA Pseudo-MSID's
    addition = [{"name": "AOACFIDC", "idx": 99999, \
            "description": "ACA Fiducial Object 0-7  (OBC)"},\
            {"name": "AOACFCTC", "idx": 98989, \
            "description": "ACA Image Func 0-7 (OBC)"},\
            {"name": "LASTDCHECK", "idx": 97989, \
            "description": "Last Data Check Time)"},\
            {"name": "ACISSTAT",    "idx": 97995, \
            "description": "ACIS Stat7-0",}\
        ]
    msididx = addition + msididx
    return msididx

def update_limit_json(limit_json):
    """
    Connect to GLIMMON_FILE and update CSH limit set
    """

    refreshed_limits = {}

    with closing(sq.connect(GLIMMON_FILE)) as conn: #: Auto-closes
        with closing(conn.cursor()) as cur:
            for msid in limit_json.keys():
                time = 0
                cur.execute(f"SELECT {SEARCH_TERMS} FROM limits where msid='{msid.lower()}' AND setkey = 0")
                for res in cur.fetchall():
                    if res[0] > time:
                        time = res[0]
                        warning_low = res[1]
                        warning_high = res[2]
                        caution_low = res[3]
                        caution_high = res[4]
                        refreshed_limits[msid] = {
                            'warning_low' : warning_low,
                            'warning_high' : warning_high,
                            'caution_low' : caution_low,
                            'caution_high' : caution_high,
                        }
    return refreshed_limits

def main():
    #: Update MSID IDX information, and include MTA alterations to expand description.
    msididx_json = _get_json(OCC_LINK)
    msididx = mta_msididx_alterations(msididx_json)
    _file = HOUSE_KEEPING / _filename(OCC_LINK)
    with open(_file, 'w') as f:
        json.dump(msididx, f, indent = 4)

    #: Update CSH limit table with refreshed information from GLIMMON_FILE
    _file = HOUSE_KEEPING / "CSH_limit_table.json"
    with open(_file) as f:
        limit_json = json.load(f)
    refreshed_limits = update_limit_json(limit_json)
    with open(_file, 'w') as f:
        json.dump(refreshed_limits, f, indent = 4)

if __name__ == "__main__":
    opt = get_options()
    main()
    #: No stall handling or path alterations for test mode
    if opt.mode == "flight":
        shutil.copyfile(HOUSE_KEEPING / _filename(OCC_LINK), SOH_WEB_DIR / _filename(OCC_LINK))