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
import time
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

def fetch_telemetry(part):
    print("hello")
    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of json blob.")
    parser.add_argument("-t", "--type", choices = ['all', 'ccdm', 'eps', 'load', 'main', 'mech', 'pcad', 'prop', 'sc_config', 'smode', 'snap', 'thermal'],
                        required = True, help= "Determine SOH category type.")
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
        #Copy blob from live running if not present in test case
        if not os.path.isfile(f"{HTML_DIR}/blob_{args.type}.json"):
            os.system(f"cp /data/mta4/www/CSH/blob_{args.type}.json {HTML_DIR}/blob_{args.type}.json")
        os.makedirs(HTML_DIR, exist_ok = True)
        start = timeit.default_timer()
        fetch_telemetry(args.type)
        print(f"Run time: {timeit.default_timer() - start}")
    elif args.mode == "flight":
#
#--- Create a lock file and exit strategy in case of race conditions
#
        name = f"{os.path.basename(__file__).split('.')[0]}_{args.type}"
        user = getpass.getuser()
        if os.path.isfile(f"/tmp/{user}/{name}.lock"):
            exit(1)
        else:
            #Previous script run must have completed successfully. Prepare lock file for this script run.
            os.system(f"mkdir -p /tmp/{user}; echo '{os.getpid()}' > /tmp/{user}/{name}.lock")
        fetch_telemetry(args.type)