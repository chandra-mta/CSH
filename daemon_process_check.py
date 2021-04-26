#!/usr/bin/env /data/mta4/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#   daemon_process_check.py: check whether SOH related daemon is running.   #
#                                                                           #
#               author: t. isobe@cfa.harvard.edu                            #
#                                                                           #
#               last update Mar 15, 2021                                    #
#                                                                           #
#############################################################################

import sys
import os
import string
import re
import time
import Chandra.Time
import random

#
#--- temp writing file name
#
rtail  = int(time.time() * random.random())
zspace = '/tmp/zspace' + str(rtail)

admin  = 'tisobe@cfa.harvard.edu'

#----------------------------------------------------------------------------
#--- daemon_process_check: check whether SOH related daemon is running     --
#----------------------------------------------------------------------------

def  daemon_process_check():
    """
    check whether SOH related daemon is running
    input: none
    output: email sent to admin, if the script found non-active daemon process
            Note: this must be run on the same cpu where the daemon processes
                  are running. (currently boba-v)
    """
#
#--- check SOH daemon processes
#
    cmd = 'ps aux|grep daemonize > ' + zspace
    os.system(cmd)

    with open(zspace, 'r') as f:
        out = [line.strip() for line in f.readlines()]
    cmd = 'rm -rf ' + zspace
    os.system(cmd)
    line = ''
    for ent in out:
        atemp = re.split('\s+', ent)
        line = line + ' ' + atemp[-1]
#
#--- there should be 11 SOH daemon processes running
#
    mc1  = re.search('soh_main_daemonize', line)
    mc2  = re.search('soh_snap_daemonize', line)
    mc3  = re.search('soh_ccdm_daemonize', line)
    mc4  = re.search('soh_eps_daemonize', line)
    mc5  = re.search('soh_load_daemonize', line)
    mc6  = re.search('soh_mech_daemonize', line)
    mc7  = re.search('soh_pcad_daemonize', line)
    mc8  = re.search('soh_prop_daemonize', line)
    mc9  = re.search('soh_sc_config_daemonize', line)
    mc10 = re.search('soh_smode_daemonize', line)
    mc11 = re.search('soh_thermal_daemonize', line)
#
#---- if the process is not running, send out email to admin
#
    if mc1 is None:
       send_email('main')
    if mc2 is None:
       send_email('snap')
    if mc3 is None:
       send_email('ccdm')
    if mc4 is None:
       send_email('eps')
    if mc5 is None:
       send_email('load')
    if mc6 is None:
       send_email('mech')
    if mc7 is None:
       send_email('pacd')
    if mc8 is None:
       send_email('prop')
    if mc9 is None:
       send_email('sc config')
    if mc10 is None:
       send_email('smode')
    if mc11 is None:
       send_email('thermal')

#----------------------------------------------------------------------------
#-- send_email: send out email to admin                                    --
#----------------------------------------------------------------------------

def send_email(inst):
    """
    send out email to admin
    input:  inst    --- SOH category of the instrument
    output: email sent to admin
    """

    text = 'daemon process of ' + inst.capitalize()  + ' page is not running.\n'
    text = text + 'Please check mta/boba-v daemon process.\n'

    with open(zspace, 'w') as fo:
        fo.write(text)

    cmd = 'cat ' + zspace + " | mailx -s'SOH Daemon Process Problem' " + admin
    os.system(cmd)

    cmd = 'rm -rf ' + zspace
    os.system(cmd)

#----------------------------------------------------------------------------

if __name__ == "__main__":

    daemon_process_check()
