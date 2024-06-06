#!/proj/sot/ska3/flight/bin/python

#####################################################################################
#                                                                                   #
#  update_msididx.py: copy msididx.json from occ side and include MTA desc.         #
#                                                                                   #
#           author: w. aaron (william.aaron@cfa.harvard.edu)                        #
#                                                                                   #
#           last update: Jun 06, 2024                                               #
#                                                                                   #
#####################################################################################

import os
import json
import argparse

HTML_DIR = "/data/mta4/www/CSH"
OCC_LINK = "https://occweb.cfa.harvard.edu/occweb/web/fot_web/software/sandbox/SOT_area/msididx.json"

def update_msididx():
    """
    Pull msididx.json from the OCC and include MTA alterations
    input:  none, but read from {OCC_LINK}
    output: {HTML_DIR}/msididx.json
    """
#
#--- Download the latest version of msididx.
#
    os.system(f"wget {OCC_LINK}")
    with open(OCC_LINK.split('/')[-1]) as f:
        msididx = json.load(f)
    
#
#--- Include MTA Alterations
#
    for i in range(len(msididx)):
        if msididx[i]['name'] in ["AORATE1", "AORATE2", "AORATE3", "AOGBIAS1", "AOGBIAS2", "AOGBIAS3"]:
            msididx[i]['description'] += " (*206265)" #Include CSH Conversion into Description
        
        elif msididx[i]['name'] in ["AODITHR2", "AODITHR3"]:
            msididx[i]['description'] += " (*3600)"

#
#--- Include MTA Pseudo-MSID's
#

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
#
#--- Write out to msididx.json file and move to HTML_DIR
#
    with open(OCC_LINK.split('/')[-1],'w') as f:
        json.dump(msididx, f, indent = 4)
    os.system(f"mv {OCC_LINK.split('/')[-1]} {HTML_DIR}/{OCC_LINK.split('/')[-1]}")

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    args = parser.parse_args()

    if args.mode == "test":
        HTML_DIR = f"{os.getcwd()}/test/outTest"
        os.makedirs(HTML_DIR, exist_ok = True)
        update_msididx()

    elif args.mode == "flight":
        update_msididx()