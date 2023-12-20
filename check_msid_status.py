#!/proj/sot/ska3/flight/bin/python

#########################################################################
#                                                                       #
#       check_msid_status.py: check status of msid                      #
#                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                   #
#                                                                       #
#           last update: Mar 15, 2021                                   #
#                                                                       #
#########################################################################

import os
import sys
import re
import string
import math
import traceback
#
#--- Define Directory Pathing
#

BIN_DIR = '/data/mta4/Script/SOH'
HOUSE_KEEPING = '/data/mta4/Script/SOH/house_keeping'
HTML_DIR = '/data/mta4/www/CSH'

#
#--- append path to a private folder
#
sys.path.append(BIN_DIR)

#-------------------------------------------------------------------------------
#-- check_status: check status of msid                                        --
#-------------------------------------------------------------------------------

def check_status(msid, val, ldict, vdict):
    """
    check status of msid
    input:  msid    --- msid
            val     --- current value of msid
            ldict   --- dictionary of limits for nemeric entry
            vdict   --- dictionary of msid <---> current value
    output: status  --- current status of msid
    """
#
#--- the value is nemeric
#
    try:
        val = float(val)
        try:
            status = check_status_neumeric(msid, val, ldict)
            return status
        except:
            traceback.print_exc()
            return 'GREEN'
#
#--- the value is letters
#
    except:
        if val in ['NaN', 'nan', '']:
            return 'CAUTION'

        elif msid in ['AOCONLAW', 'AOCPESTL', '4OBAVTMF', '4OBTOORF', 'COSCS128S',\
                    'COSCS129S','COSCS130S', 'COSCS131S','COSCS132S','COSCS133S',\
                    'COSCS107S','CORADMEN', 'CCSDSTMF', 'ACAFCT', 'AOFSTAR',\
                    '2SHLDART', 'PLINE03T', 'PLINE04T', 'AACCCDPT', '3LDRTNO']:
            status = check_status_letter(msid, val, vdict)
            return status
        else:
            if val in ['ERR', 'FALT', 'FAIL']:
                return "CAUTION"
            else:
                return 'GREEN'

#-------------------------------------------------------------------------------
#-- check_status_neumeric: check status of msid with nemeric value            --
#-------------------------------------------------------------------------------

def check_status_neumeric(msid, val, ldict):
    """
    check status of msid with nemeric value
    input:  msid    --- msid
            val     --- current value of msid
            ldict   --- dictionary of limits for nemeric entry
    output: status  --- current status of msid
    """
#
#--- if no condition, return 'GREEN'
#
    try:
        limit   = ldict[msid]
    except:
        return "GREEN"
    
    if (len(limit) == 0) or (limit == ['']):
        return "GREEN"
#
#--- condition exists; check agaist the value
#
    else:
        try:
            nval = float(val)
            ly   = float(limit[0])
            uy   = float(limit[1])
            lr   = float(limit[2])
            ur   = float(limit[3])
            if (nval >= ly) and (nval < uy):
                return "GREEN"

            elif (nval >= lr) and (nval < ur):
                return "CAUTION"

            else:
                return "WARNING"
        except:
            return 'GREEN'

#-------------------------------------------------------------------------------
#-- check_status_letter: check status of msid with none nuemeric values       --
#-------------------------------------------------------------------------------

def check_status_letter(msid, val, vdict):
    """
    check status of msid with none nuemeric values
    input:  msid    --- msid
            val     --- current value of msid
            vdict   --- dictionary of msid <---> current value
    output: status  --- current status of msid
    """
    if msid == 'AOCONLAW':
        if val == 'NPNT':
            return 'GREEN'
        else:
            return 'WARNING'
    
    elif msid == 'AOCPESTL':
        if val == 'NORM':
            return 'GREEN'
        elif val == 'SAFE':
            return 'WARNING'
        else:
            return 'CAUTION'
    
    elif msid in ['4OBAVTMF', '4OBTOORF']:
        if val == 'NFLT':
            return 'GREEN'
        else:
            return 'WARNING'
    
    elif msid in ['COSCS128S', 'COSCS129S','COSCS130S']:
        tval = vdict['COTLRDSF']
        if tval == 'EPS':
            csc128 = vdict['COSCS128S']
            csc129 = vdict['COSCS129S']
            csc130 = vdict['COSCS130S']
            if (csc128 != 'ACT') and (csc129 != 'ACT') and (csc130 != 'ACT'):
                return 'WARNING'
            elif( val != 'ACT'):
                if ( (csc128 == 'ACT') or (csc129 == 'ACT') or (csc130 == 'ACT')):
                    return 'CAUTION'
            else:
                return 'GREEN'
        else:
            return 'GREEN'
    
    elif msid in ['COSCS131S','COSCS132S','COSCS133S']:
        tval = vdict['COTLRDSF']
        if tval == 'EPS':
            if val == 'ACT':
                return 'GREEN'
            else:
                return 'CAUTION'
        else:
            return 'GREEN'

    elif msid == 'COSCS107S':
            if val in ['ACT', 'DISA']:
                return 'WARNING'
            else:
                return 'GREEN'
    
    elif msid == 'CORADMEN':
        tval1 = vdict['COBSRQID']
        tval2 = vdict['3TSCPOS']
        if (tval1 > 5000) and (tval2) < -99000:
            if val == 'ENAB':
                return 'WARNING'
            elif val == 'DISA':
                return 'GREEN'
            else:
                return 'GREEN'
        elif (tval1 < 5000) and (tval2) > -99000:
            if val == 'ENAB':
                return 'GREEN'
            elif val == 'DISA':
                return 'WARNING'
            else:
                return 'GREEN'
        else:
            return 'GREEN'
    
    elif msid == 'CCSDSTMF':
        if val in [1, 2]:
            return 'GREEN'
        elif val in [3, 4, 6]:
            return 'CAUTION'
        elif val == 5:
            return 'WARNING'
        else:
            return 'GREEN'
    
    elif msid == 'ACAFCT':
        tval1 = vdict('AOPCAMD')
        tval2 = vdict('COBSRQID')
        if tval1 == 'NPNT':
            if tval2 < 5500:
                return 'WARNING'
            elif tval2 >= 5500:
                return 'CAUTION'
        else:
            return 'GREEN'
    
    elif msid == 'AOFSTAR':
        if val == 'GUID':
            return 'GREEN'
        elif val == 'BRIT':
            return 'WARNING'
        else:
            return 'CAUTION'
         
    elif msid == '2SHLDART':
        tval = vdicvdictt('CORADMEN')
        if val > 255:
            return 'GREEN'
        else:
            if tval == 'DISA':
                return 'GREEN'
            elif tval == 'ENAB':
                if val < 80:
                    return 'GREEN'
                else:
                    return 'CAUTION'
            else:
                return 'GREEN'
    
    elif msid in ['PLINE03T', 'PLINE04T']:
        if val >= 42.5:
            return 'GREEN'
        elif val < 40:
            return 'WARNING'
        elif val < 42.5:
            return 'CAUION'
    
    elif msid == 'AACCCDPT':
        if val >= 0:
            return 'WARNING'
        elif val > -17:
            return 'CAUTION'
        elif val < -21.5:
            return 'CAUTION'
        else:
            return 'GREEN'
        
    elif msid == '3LDRTNO':
        if val > 0:
            return 'GREEN'
        else:
            return 'WARNING'

    else:
        return 'GREEN'
