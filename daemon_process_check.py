#!/usr/bin/env /data/mta4/Script/Python3.8/envs/ska3-shiny/bin/python

#############################################################################
#                                                                           #
#   daemon_process_check.py: check whether SOH related daemon is running.   #
#                                                                           #
#               author: t. isobe@cfa.harvard.edu                            #
#                                                                           #
#               last update Oct 12, 2022                                    #
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

#
#--Create admin list through emails passed as sys args
#
ADMIN = ['mtadude@cfa.harvard.edu']
for i in range(1,len(sys.argv)):
    if sys.argv[i][:6] == 'email=':
        ADMIN.append(sys.argv[i][6:])

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
       os.system("/data/mta4/Script/SOH/soh_main_daemonize")
    if mc2 is None:
       send_email('snap')
       os.system("/data/mta4/Script/SOH/soh_snap_daemonize")
    if mc3 is None:
       send_email('ccdm')
       os.system("/data/mta4/Script/SOH/soh_ccdm_daemonize")
    if mc4 is None:
       send_email('eps')
       os.system("/data/mta4/Script/SOH/soh_eps_daemonize")
    if mc5 is None:
       send_email('load')
       os.system("/data/mta4/Script/SOH/soh_load_daemonize")
    if mc6 is None:
       send_email('mech')
       os.system("/data/mta4/Script/SOH/soh_mech_daemonize")
    if mc7 is None:
       send_email('pacd')
       os.system("/data/mta4/Script/SOH/soh_pcad_daemonize")
    if mc8 is None:
       send_email('prop')
       os.system("/data/mta4/Script/SOH/soh_prop_daemonize")
    if mc9 is None:
       send_email('sc config')
       os.system("/data/mta4/Script/SOH/soh_sc_config_daemonize")
    if mc10 is None:
       send_email('smode')
       os.system("/data/mta4/Script/SOH/soh_smode_daemonize")
    if mc11 is None:
       send_email('thermal')
       os.system("/data/mta4/Script/SOH/soh_thermal_daemonize")

#----------------------------------------------------------------------------
#-- send_email: send out email to admin                                    --
#----------------------------------------------------------------------------

def send_email(inst):
    """
    send out email to admin
    input:  inst    --- SOH category of the instrument
    output: email sent to admin
    """

    text = 'daemon process of ' + inst.capitalize()  + ' page was not running, '
    text = text + 'and restarted. Please make sure that it is actually restarted on: ' 
    text = text + ' mta/boba-v.\n'

    with open(zspace, 'w') as fo:
        fo.write(text)

    cmd = 'cat ' + zspace + " | mailx -s'SOH Daemon Process Problem' " + ' '.join(ADMIN)
    os.system(cmd)

    cmd = 'rm -rf ' + zspace
    os.system(cmd)

#----------------------------------------------------------------------------

if __name__ == "__main__":

    daemon_process_check()
