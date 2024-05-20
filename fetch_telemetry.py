#!/proj/sot/ska3/flight/bin/python

#####################################################################################
#                                                                                   #
#           fetch_telemetry: extract maude blobs for specific part from occ         #
#                                                                                   #
#           author: w. aaron ( william.aaron@cfa.harvad.edu)                        #
#                                                                                   #
#           last update: May 17, 2024                                               #
#                                                                                   #
#####################################################################################

import os
import sys
from datetime import datetime, timedelta
import cxotime
import maude
import traceback
import argparse
import getpass
import json
import timeit
#
#--- Define Directory Pathing
#
BIN_DIR = "/data/mta4/Script/SOH"
HTML_DIR = "/data/mta4/www/CSH"
HOUSE_KEEPING = f"{BIN_DIR}/house_keeping"
#
#--- append path to a private folder
#
sys.path.append(BIN_DIR)
import check_msid_status    as cms

#
#--- Defining kwarg of blob fetch
#
FETCH_SECONDS = 120
FETCH_KWARGS = {
    "channel": "FLIGHT", # options (FLIGHT, FLTCOMP, ASVT, TEST)
    #"hr": "t", #High data rate
    #"ap": "t", #Include all points in the query fetch
    #"icalc": "t", #include calc-type blobs in spacecraft blob queries
}

def fetch_telemetry(msid_list, part, stop= None):
    start = timeit.default_timer()
    fetch_result = get_CSH_blobs(msid_list, stop)
    print(f"get_CSH_blobs Run time: {timeit.default_timer() - start}")

    start = timeit.default_timer()
    formatted_data = format_result(fetch_result)
    print(f"format_result Run time: {timeit.default_timer() - start}")

    start = timeit.default_timer()
    write_to_file(formatted_data)
    print(f"write_to_file Run time: {timeit.default_timer() - start}")



def get_CSH_blobs(msid_list, stop= None):
    """
    Fetch the telemetry data using maude
    """
#
#--- If no time frame is passed, then pull current time and format into cxotime
#
    if not stop:
        stop = datetime.utcnow()
        start = stop - timedelta(seconds= FETCH_SECONDS)
        stop = cxotime.CxoTime(stop.strftime("%Y:%j:%H:%M:%S")).secs
        start = cxotime.CxoTime(start.strftime("%Y:%j:%H:%M:%S")).secs
    else:
        stop = cxotime.CxoTime(stop).secs
        start = stop - FETCH_SECONDS
#
#--- Fetch the blobs in question
#
    result = maude.get_blobs(start = start, stop = stop, msids = msid_list, **FETCH_KWARGS)
    return result

def format_result(fetch_result):
    """
    Format fetch result to only contain the latest data point
    and its limit status
    """
    pass

def write_to_file(formatted_data):
    """
    Iterate through blob_<part>.json updating each data value
    """
    pass
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of json blob.")
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument("-t", "--type", choices = ['all', 'ccdm', 'eps', 'load', 'main', 'mech', 'pcad', 'prop', 'sc_config', 'smode', 'snap', 'thermal'],
                        help= "Determine SOH category type.")
    group.add_argument("-l", "--list", nargs='+', help = "List of MSID's to update in script")
    parser.add_argument("--stop", help= "CXO formatted stop time for a specific blob fetch.")
    args = parser.parse_args()

#
#--- Determine if running in test mode and change pathing if so
#
    if args.mode == "test":
#
#--- Path output to same location as unit tests
#
        BIN_DIR= f"{os.getcwd()}"
        HOUSE_KEEPING = f"{BIN_DIR}/house_keeping"
        if args.path:
            HTML_DIR = args.path
        else:
            HTML_DIR = f"{BIN_DIR}/test/outTest/CSH"
        
#
#--- Determine msid_list for selection blob data
#
        if args.type:
            part = args.type
            ifile = f"{HOUSE_KEEPING}/Inst_part/msid_list_{part}"
            with open(ifile) as f:
                msid_list = [line.strip() for line in f.readlines()]

            #Copy blob from live running if not present in test case
            if not os.path.isfile(f"{HTML_DIR}/blob_{part}.json"):
                os.system(f"cp /data/mta4/www/CSH/blob_{part}.json {HTML_DIR}/blob_{part}.json")
        else:
            part = 'list'
            msid_list = args.list
        
        os.makedirs(HTML_DIR, exist_ok = True)
        
        #Run the script
        start = timeit.default_timer()
        fetch_telemetry(msid_list, part, stop = args.stop)
        print(f"Total Run time: {timeit.default_timer() - start}")

    elif args.mode == "flight":

#
#--- Determine msid_list for selection blob data
#
        if args.type:
            part = args.type
            ifile = f"{HOUSE_KEEPING}/Inst_part/msid_list_{part}"
            with open(ifile) as f:
                msid_list = [line.strip() for line in f.readlines()]
        else:
            part = 'list'
            msid_list = args.list
#
#--- Create a lock file and exit strategy in case of race conditions
#
        name = f"{os.path.basename(__file__).split('.')[0]}_{part}"
        user = getpass.getuser()
        if os.path.isfile(f"/tmp/{user}/{name}.lock"):
            exit(1)
        else:
            #Previous script run must have completed successfully. Prepare lock file for this script run.
            os.system(f"mkdir -p /tmp/{user}; echo '{os.getpid()}' > /tmp/{user}/{name}.lock")
        fetch_telemetry(msid_list, part)