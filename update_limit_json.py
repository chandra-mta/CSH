#!/proj/sot/ska3/flight/bin/python

#####################################################################################
#                                                                                   #
#   update_limit_json.py: update a limit data table                                 #
#                                                                                   #
#           author:w. aaron (william.aaron@cfa.harvard.edu)                         #
#                                                                                   #
#           last update: Jun 05, 2024                                               #
#                                                                                   #
#####################################################################################

import os
import sqlite3
import json
import argparse

#
#--- Define Directory Pathing
#
GLIMMON_FILE = "/data/mta/Script/MSID_limit/glimmondb.sqlite3"
HOUSE_KEEPING = "/data/mta4/Script/SOH/house_keeping"

#
#---Globals
#
SEARCH_TERMS = "datesec, warning_low, warning_high, caution_low, caution_high"

def update_limit_json():
    """
    connect to the localt glimmon database copy and update CSH limit set
    input: none, but read from {GLIMMON_FILE}
    output: {HOUSE_KEEPING}/CSH_limit_table.json
    """
#
#--- Connect to the glimmon sqlite database
#
    con = sqlite3.connect("/data/mta/Script/MSID_limit/glimmondb.sqlite3")
    cur = con.cursor()
#
#--- Pull data from the current CSH limit table
#
    with open(f"{HOUSE_KEEPING}/CSH_limit_table.json") as f:
        csh_limit_table = json.load(f)
#
#--- Read table and refresh the limits
#
    fresh = {}
    for msid in csh_limit_table.keys():
        time = 0
        results = cur.execute(f"SELECT {SEARCH_TERMS} FROM limits where msid='{msid.lower()}' AND setkey = 0")
        for res in results:
            if res[0] > time:
                time = res[0]
                warning_low = res[1]
                warning_high = res[2]
                caution_low = res[3]
                caution_high = res[4]
                fresh[msid] = {
                    'warning_low' : warning_low,
                    'warning_high' : warning_high,
                    'caution_low' : caution_low,
                    'caution_high' : caution_high,
                }
#
#--- Write out to CSH limit table
#
    with open(f"{HOUSE_KEEPING}/CSH_limit_table.json", 'w') as f:
        json.dump(fresh, f, indent = 4)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    args = parser.parse_args()

    if args.mode == "test":
        HOUSE_KEEPING = f"{os.getcwd()}/test/outTest"
        if not os.path.isfile(f"{HOUSE_KEEPING}/CSH_limit_table.json"):
            os.system(f"cp /data/mta4/Script/SOH/house_keeping/CSH_limit_table.json {HOUSE_KEEPING}/CSH_limit_table.json")
        update_limit_json()
    if args.mode == 'test':
        update_limit_json()