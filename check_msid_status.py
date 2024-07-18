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

#-------------------------------------------------------------------------------
#-- check_status: check status of msid                                        --
#-------------------------------------------------------------------------------

def check_status(msid, val, ldict, vdict):
    """
    check status of msid
    input:  msid    --- msid
            val     --- current value of msid
            ldict   --- dictionary of limits for numeric entry
            vdict   --- dictionary of msid <---> current value
    output: status  --- current status of msid
    """
#
#--- If value is numeric, then convert
#
    try:
        val = float(val)
    except:
        pass
#
#--- General Violation
#
    if val in ['ERR', 'FALT', 'FAIL', 'NaN', 'nan', '']:
        return 'CAUTION'
#
#--- Edge Case Violation
#
    elif msid in ['AOCONLAW', 'AOCPESTL', '4OBAVTMF', '4OBTOORF', 'COSCS128S',\
                  'COSCS129S','COSCS130S', 'COSCS131S','COSCS132S','COSCS133S',\
                  'COSCS107S','CORADMEN', 'CCSDSTMF', 'ACAFCT', 'AOFSTAR', '2SHLDART']:
        return check_status_edge_case(msid, val, vdict)
#
#--- Numerical Violation
#
    elif isinstance(val, float):
        return check_status_numeric(msid, val, ldict)
#
#--- Unchecked Instance
#
    else:
        return 'GREEN'

#-------------------------------------------------------------------------------
#-- check_status_numeric: check status of msid with numeric value            --
#-------------------------------------------------------------------------------

def check_status_numeric(msid, val, ldict):
    """
    check status of msid with numeric value
    input:  msid    --- msid
            val     --- current value of msid
            ldict   --- dictionary of limits for numeric entry
    output: status  --- current status of msid
    """
    if msid in ldict.keys():
#
#--- condition exists; check agaist the value
#
        limit   = ldict[msid]
        if (val >= limit['warning_low']) and (val <= limit['warning_high']):
            return "GREEN"
        elif (val >= limit['caution_low']) and (val <= limit['caution_high']):
            return "CAUTION"
        else:
            return "WARNING"
    else:
#
#--- if no condition, return 'GREEN'
#
        return "GREEN"

#-------------------------------------------------------------------------------
#-- check_status_edge_case: check status of msid with none numeric values       --
#-------------------------------------------------------------------------------

def check_status_edge_case(msid, val, vdict):
    """
    check status of msid with none numeric values
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
            scs128 = vdict['COSCS128S']
            scs129 = vdict['COSCS129S']
            scs130 = vdict['COSCS130S']
            if (scs128 != 'ACT') and (scs129 != 'ACT') and (scs130 != 'ACT'):
                return 'WARNING'
            elif( val != 'ACT'):
                if ( (scs128 == 'ACT') or (scs129 == 'ACT') or (scs130 == 'ACT')):
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
        tval1 = float(vdict['COBSRQID'])
        tval2 = float(vdict['3TSCPOS'])
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
        tval1 = vdict['AOPCADMD']
        tval2 = vdict['COBSRQID']
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
        tval = vdict['CORADMEN']
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

    else:
        return 'GREEN'