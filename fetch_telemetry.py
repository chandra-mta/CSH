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
import math
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
#--- Defining Globals
#
BLOB_CHOICE = ['ccdm', 'eps', 'load', 'main', 'mech', 'pcad', 'prop', 'sc_config', 'smode', 'snap', 'thermal']
FETCH_SECONDS = 120
FETCH_KWARGS = {
    "channel": "FLIGHT", # options (FLIGHT, FLTCOMP, ASVT, TEST)
    #"highrate": True, #High data rate
    #"allpoints": True, #Include all points in the query fetch
    #"include_calcs": True, #include calc-type blobs in spacecraft blob queries
}

def fetch_telemetry(part = None, msid_list = None, stop= None):
    start = timeit.default_timer()
    fetch_result = get_CSH_blobs(msid_list, stop)
    print(f"get_CSH_blobs Run time: {timeit.default_timer() - start}")

    start = timeit.default_timer()
    formatted_data = format_result(fetch_result)
    print(f"format_result Run time: {timeit.default_timer() - start}")

    start = timeit.default_timer()
    unit_converted_data = unit_conversion(formatted_data)
    print(f"unit_conversion Run time: {timeit.default_timer() - start}")

    start = timeit.default_timer()
    limit_checked_data = check_limit_status(unit_converted_data)
    print(f"check_limit_status Run time: {timeit.default_timer() - start}")

    
    start = timeit.default_timer()
    write_to_file(limit_checked_data)
    print(f"write_to_file Run time: {timeit.default_timer() - start}")



def get_CSH_blobs(msid_list = None, stop= None):
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
    if msid_list:
        result = maude.get_blobs(start = start, stop = stop, msids = msid_list, **FETCH_KWARGS)
    else:
        #default to fetching all blob data to fill out all blob portions
        result = maude.get_blobs(start = start, stop = stop, **FETCH_KWARGS)
    return result

def format_result(fetch_result):
    """
    Format fetch result to only contain the latest data point
    """
#
#--- iterate over results in time reverse order, therefore added data is latest in result
#
    fetch_result['blobs'].reverse()
    formatted_data = {}
    for blob in fetch_result['blobs']:
#
#--- for each time point, iterate over msid's recorded in this section
#
        for val in blob['values']:
            if val['n'] not in formatted_data.keys():
                formatted_data[val['n']] = {'time': blob['time'], 'value': val['vc'] }

    return formatted_data

def unit_conversion(data):
    """
    Perform a unit conversion for a few special edge cases.
    If statement check since it's possible that one of the MSID's is not in this round of blob updates
    """
    update_msids = data.keys()

    #Shield Rates
    for msid in ['2DETART', '2SHLDART', '2SHLDBRT']:
        if msid in update_msids:
            data[msid]['value'] = f"{round((float(data[msid]['value']) / 256.0), 2)}"
    if '2DETBRT' in update_msids:
        data['2DETBRT']['value'] = f"{math.floor(math.log(float(data['2DETBRT']['value']) + 1.0) / 0.6931471805599453)}"

    #ACA Integration Time
    if 'AOACINTT' in update_msids:
        data['AOACINTT']['value'] = f"{float(data['AOACINTT']['value']) / 1000}"
    
    #Momentum and Bias
    for msid in ['AOGBIAS1', 'AOGBIAS2', 'AOGBIAS3', 'AORATE1', 'AORATE2', 'AORATE3']:
        if msid in update_msids:
            data[msid]['value'] = f"{(float(data[msid]['value']) * 206264.98)}"    #----arcsec/sec
    
    #Dither
    for msid in ['AODITHR2', 'AODITHR3']:
        if msid in update_msids:
            data[msid]['value'] = f"{float(data[msid]['value']) * 3600.0}"

    #AC CCD Temperature
    if 'AACCCDPT' in update_msids:
        data['AACCCDPT']['value'] = f"{5.0 * (float(data['AACCCDPT']['value']) -32) / 9.0}" #---Convert F to C

    #Battery SOC Range
    for msid in ['EOCHRGB1', 'EOCHRGB2', 'EOCHRGB3']:      #--- percentage
        if msid in update_msids:
            data[msid]['value'] = f"{float(data[msid]['value']) * 100.0}"

    return data


def generate_psuedo_msids(data):
    """
    Create psuedo MSIDs for display
    """
    #create "ACIS Stat7-0" msid
    for msid in ['1STAT7ST', '1STAT6ST', '1STAT5ST', '1STAT4ST', '1STAT3ST', '1STAT2ST', '1STAT1ST', '1STAT0ST']:
        pass


def check_limit_status(data):
    """
    Include the limit status into the data structure
    """
    for msid, entry in data.items():
        status = cms.check_status(msid, entry['value'], LIMIT_DICT, data)
        data[msid]['scheck'] = status
    return data

def write_to_file(data):
    """
    Iterate through blob_<part>.json updating each data value
    """
    for part in BLOB_CHOICE:
        with open(f"{HTML_DIR}/blob_{part}.json") as f:
            data_list = json.load(f)
#
#--- Iterate over the specific parts entires via indexing, so that the list can be edited
#
        for i in range(len(data_list)):
            msid = data_list[i]['msid']
            try:
                if data[msid]['time'] > data_list[i]['time']:
    #
    #--- Run the update
    #
                    data_list[i]['time'] = float(data[msid]['time'])
                    data_list[i]['value'] = str(data[msid]['value'])
                    data_list[i]['scheck'] = str(data[msid]['scheck'])
            except KeyError:
                #msid in the blob list not located in formatted data
                pass
            except not KeyError:
                traceback.print_exc()
        with open(f"{HTML_DIR}/blob_{part}.json", 'w') as f:
            json.dump(data_list, f, indent = 4)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of json blob.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t", "--type", choices = BLOB_CHOICE, help= "Determine SOH category type.")
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
        with open(f"{HOUSE_KEEPING}/CSH_limit_table.json") as f:
            LIMIT_DICT = json.load(f)
        if args.path:
            HTML_DIR = args.path
        else:
            HTML_DIR = f"{BIN_DIR}/test/outTest/CSH"
        
#
#--- Determine msid_list for selection of blob data
#
        msid_list = None
        part = None
        if args.type:
            part = args.type
            BLOB_CHOICE = [part]
            ifile = f"{HOUSE_KEEPING}/Inst_part/msid_list_{part}"
            with open(ifile) as f:
                msid_list = [line.strip() for line in f.readlines()]

            #Copy blob from live running if not present in test case
            if not os.path.isfile(f"{HTML_DIR}/blob_{part}.json"):
                os.system(f"cp /data/mta4/www/CSH/blob_{part}.json {HTML_DIR}/blob_{part}.json")
        elif args.list:
            part = 'list'
            BLOB_CHOICE = []
            msid_list = args.list
        
        os.makedirs(HTML_DIR, exist_ok = True)
        
        #Run the script
        start = timeit.default_timer()
        fetch_telemetry(msid_list = msid_list, part = part, stop = args.stop)
        print(f"Total Run time: {timeit.default_timer() - start}")

    elif args.mode == "flight":
        with open(f"{HOUSE_KEEPING}/CSH_limit_table.json") as f:
            LIMIT_DICT = json.load(f)
#
#--- Determine msid_list for selection blob data
#
        if args.type:
            part = args.type
            BLOB_CHOICE = [part]
            ifile = f"{HOUSE_KEEPING}/Inst_part/msid_list_{part}"
            with open(ifile) as f:
                msid_list = [line.strip() for line in f.readlines()]
        else:
            part = 'list'
            BLOB_CHOICE = []
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
        fetch_telemetry()