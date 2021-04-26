#!/usr/bin/env /data/mta4/Script/Python3.8/envs/ska3-shiny/bin/python

#####################################################################################
#                                                                                   #
#   mk_limit_table.py: update a limit data table                                    #
#                                                                                   #
#           author:t. isobe (tisobe@cfa.harvard.edu)                                #
#                                                                                   #
#           last update: Mar 15, 2021                                               #
#                                                                                   #
#####################################################################################

import os
import sys
import re
import string
import math
import sqlite3
import json
#
path = '/data/mta4/Script/SOH/house_keeping/dir_list'
with open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var   = atemp[1].strip()
    line  = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append path to a private folder
#
sys.path.append(bin_dir)

glimmon = '/data/mta4/MTA/data/op_limits/glimmondb.sqlite3'
#
#--- these use the same limits as their counterparts in Side 1
#
mech_sp = ['7FAMOVE', '7FAMTRAT', '7FAPOS', '7FAPSAT', '7FASEAAT', '7LDRTMEK',\
           '7LDRTNO', '7LDRTPOS', '7MRMMXMV', '7SEAID', '7SEAINCM', '7SEARAMF',\
           '7SEAROMF', '7SEARSET', '7SEATMUP', '7SMOTOC', '7SMOTPEN', '7SMOTSEL',\
           '7SMOTSTL', '7STAB2EN', '7TRMTRAT', '7TSCMOVE', '7TSCPOS']
#
#--- these do not check limit
#
no_test = ['AOCPESTC', 'ACPEAHB', 'CONHLHTBT', 'COFHLHTBT', 'COERRCN']

#-------------------------------------------------------------------------------
#-- get_current_limits: update limit table                                    --
#-------------------------------------------------------------------------------

def get_current_limits():
    """
    update limit table
    input:  none but read from:
            <house_keeping>/Inst_part/msid_list_all
            /data/mta4/MTA/data/op_limits/glimmondb.sqlite3
    output: <house_keeping>/limit_table
    """
#
#--- get a list of msids
#
    ifile = house_keeping  + 'Inst_part/msid_list_all'
    data  = read_data_file(ifile)

    sline  = ''
    for msid in data:
#        if msid[-1] in ['T', 't']:
#            tind = 1
#        else:
#            tind = 0
        tind = 0

        line =  msid
#
#--- use side1 limits for side2 msid of mech.
#
        if msid in mech_sp:
            msid = msid.replace('7', '3')
#
#--- don't check the limit if it is in no_test list
#
        if msid in no_test:
            out = []
        else:
            out = read_glimmon(msid, tind)

        if len(out) > 0:
           for val in out:
               line = line + '<>' + str(val)
            
           line = line + '\n'
           sline = sline + line

    outfile = house_keeping + 'limit_table'
    with open(outfile, 'w') as fo:
        fo.write(sline)

    #outfile2 = '/data/mta4/Script/SOH_ASVT/house_keeping/limit_table'
    #cmd      = 'cp -f ' + outfile + ' ' + outfile2
    #os.system(cmd)

#-----------------------------------------------------------------------------------
#-- read_glimmon: read glimmondb.sqlite3 and return yellow and red lower and upper limits 
#-----------------------------------------------------------------------------------

def read_glimmon(msid, tind):
    """
    read glimmondb.sqlite3 and return yellow and red lower and upper limits
    input:  msid    --- msid
            tind    --- whether this is a temperature related msid and in K. O; no, 1: yes
    output: y_min   --- lower yellow limit
            y_max   --- upper yellow limit
            r_min   --- lower red limit
            r_max   --- upper red limit
    """
    lmsid = msid.lower()
#
#--- glimmon keeps the temperature related quantities in C. convert it into K.
#
    if tind == 0:
        add = 0
    else:
        add = 273.15
    
    db = sqlite3.connect(glimmon)
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM limits WHERE msid='%s'" % lmsid)
    allrows = cursor.fetchall()
    
    if len(allrows) == 0:
        return []
    
    tup   = allrows[0]
    try:
        if msid == 'AACCCDPT':
            y_min = f_to_c(tup[12])
            y_max = f_to_c(tup[11])
            r_min = f_to_c(tup[14])
            r_max = f_to_c(tup[13])
        elif msid in ['AODITHR1', 'AODITHR2', 'AODITHR3']:
            y_min = tup[12] * 3600.0
            y_max = tup[11] * 3600.0
            r_min = tup[14] * 3600.0
            r_max = tup[13] * 3600.0
        elif msid in ['AORATE1', 'AORATE2', 'AORATE3', 'AOGBIAS1', 'AOGBIAS2', 'AOGBIAS3']:
            y_min = tup[12] * 206265.0
            y_max = tup[11] * 206265.0
            r_min = tup[14] * 206265.0
            r_max = tup[13] * 206265.0
        else:
            y_min = tup[12] + add
            y_max = tup[11] + add
            r_min = tup[14] + add
            r_max = tup[13] + add
    except:
        y_min = tup[12]
        y_max = tup[11]
        r_min = tup[14]
        r_max = tup[13]
    
    return [y_min, y_max, r_min, r_max]

#-------------------------------------------------------------------------------
#-- f_to_c: convert temp from F to C                                          --
#-------------------------------------------------------------------------------

def f_to_c(fval):
    """
    convert temp from F to C
    input fval  --- temp in f
    output:     --- temp in c
    """
    
    return 5.0 * (fval - 32.0) / 9.0

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def read_data_file(ifile, remove=0):

    with open(ifile, 'r') as f:
        data = [line.strip() for line in f.readlines()]

    if remove  == 1:
        cmd = 'rm -rf ' + ifile
        os.system(cmd)

    return data

#-------------------------------------------------------------------------------

if __name__ == "__main__":

    get_current_limits()

