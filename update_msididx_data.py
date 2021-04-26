#!/usr/bin/env /data/mta4/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#           update_msididx_data.py: copy msididx.json from occ side                 #
#                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                                   #
#           last update: Mar 15, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import math
import time
import Chandra.Time
import maude
import ast
import json
path = '/data/mta4/Script/SOH/house_keeping/dir_list'
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- those with conversion values
#
#sp_msid = ['AOGBIAS1', 'AOGBIAS2', 'AOGBIAS3', 'AORATE1', 'AORATE2', 'AORATE3', 'AODITHR2', 'AODITHR3']
#conv_vals = [206264.98,   206264.98,  206264.98, 206264.98,  206264.98, 206264.98, 3600,0,     3600.0]
sp_msid   = []
conv_val  = []

#-------------------------------------------------------------------------------
#-- update_msididx_data: copy msididx.json from occ side                        --
#-------------------------------------------------------------------------------

def update_msididx_data():
    """
    copy msididx.json from occ side
    input: none but read from <house_keeping>/limit_table
                              <house_keeping>/msididx_base
    output: <html_dir>/msididx.json
    """
#
#--- read the local limit table
#
    ifile = house_keeping + 'limit_table'
    out   = read_data_file(ifile)

    l_dict = {}
    for ent in out:
        atemp = re.split('<>', ent)
        l_dict[atemp[0]] = atemp[1:]
#
#--- read the last msididx.json from the main web site
#
    ifile = house_keeping + 'msididx_base'
    with open(ifile, 'r') as f:
        out = json.load(f)

    updated = []
    for ent in out:

        msid = ent['name'].strip()
#
#--- find conversion value of the special msids
#
        conv = 1
        if ent['name'] in sp_msid:
            for k in range(0, len(sp_msid)):
                if msid == sp_msid[k]:
                    conv = conv_vals[k]
                    break
#
#--- update limit values
#
        try:
            out = l_dict[msid]
            save = []
            temp = {}
            lims = {}
            lims['cl']  = float(out[0]) * conv
            lims['ch']  = float(out[1]) * conv
            lims['wl']  = float(out[2]) * conv
            lims['wh']  = float(out[3]) * conv
            xline = 'cl: %2.3f ' % (float(out[0]) * conv)
            xline = xline + 'ch: %2.3f ' % round((float(out[1]) * conv), 2)
            xline = xline + 'wl: %2.3f ' % round((float(out[2]) * conv), 2)
            xline = xline + 'wh: %2.3f ' % round((float(out[3]) * conv), 2)
            temp['set'] = lims
            save.append(temp)
#
#--- 'lim' keeps the limits in the original format, 'xlim' keeps the limits for a display
#
            ent['lim'] = save
            ent['xlim'] = xline
        except:
            pass

        updated.append(ent)
#
#--- special addtions
#
    t_add = [{"name": "AOACFIDC", "idx": 99999, \
              "description": "ACA Fiducial Object 0-7  (OBC)", "sc": [""]},\
             {"name": "AOACFCTC", "idx": 98989, \
              "description": "ACA Image Func 0-7 (OBC)",       "sc": [""]},\
             {"name": "LASTDCHECK", "idx": 97989, \
              "description": "Last Data Check Time)",          "sc": [""]},\
             {"name": "ACISSTAT",    "idx": 97995, \
              "description": "ACIS Stat7-0",          "          sc": [""]}\
            ]
#
#--- combine two lists
#
    out  = t_add + updated
#
#--- print out the data
#
    outfile = html_dir + 'msididx.json'
    with open(outfile, 'w') as msididx:
        json.dump(out, msididx)
#
#--- copy the json file to ASVT site
#
    outfile2 = '/data/mta4/www/CSH_ASVT/msididx.json'
    cmd      = 'cp -f ' + outfile + ' ' + outfile2
    os.system(cmd)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def read_data_file(file):

    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    return data

#-------------------------------------------------------------------------------

if __name__ == '__main__':

    update_msididx_data()

