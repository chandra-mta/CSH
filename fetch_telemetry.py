#!/usr/bin/env python
"""
**fetch_telemetry.py**: extract maude blobs from occ and categorize

:Author: W. Aaron (william.aaron@cfa.harvad.edu)
:Last Updated: Mar 25, 2026

# /// testing
# tested-ska-release = "2026.1"
# ///
"""
import os
from subprocess import PIPE, Popen
import sys
from cxotime import CxoTime
import maude
import argparse
import json
import astropy.units as u
from email.mime.text import MIMEText
from pathlib import Path
import psutil
import shutil
import signal
ADMIN = 'mtadude@cfa.harvard.edu'
_TESTMAIL = False

#
#--- Define Directory Pathing
#
SOH_DIR = Path(os.getenv("SOH_DIR", "/data/mta4/Script/SOH"))
SOH_WEB_DIR = Path(os.getenv("SOH_WEB_DIR", "/data/mta4/www/CSH"))
SCRIPT_DIR = Path(__file__).parent
HOUSE_KEEPING = SCRIPT_DIR / "house_keeping"
#
#--- Append path to a private folder
#
sys.path.append(SCRIPT_DIR)
import check_msid_status as cms  # noqa: E402 #: TODO make portable with relative imports by using package implementation

#
#--- Defining Globals
#
NOW = CxoTime()
BLOB_SECTIONS = ['ccdm', 'eps', 'load', 'main', 'mech', 'pcad', 'prop', 'sc_config', 'smode', 'snap', 'thermal']
FETCH_SECONDS = 30
FETCH_KWARGS = {
    "channel": "FLIGHT", # options (FLIGHT, FLTCOMP, ASVT, TEST)
    #"highrate": True, #High data rate
    #"allpoints": True, #Include all points in the query fetch
    #"include_calcs": True, #include calc-type blobs in spacecraft blob queries
}
with open(HOUSE_KEEPING / "CSH_limit_table.json") as f:
    LIMIT_DICT = json.load(f)
#
#--- For selecting msid values from previous blobs for limit checking
#
COMP_LIM_SELECTION = ['COTLRDSF', 'COSCS128S', 'COSCS129S', 'COSCS130S', 'COTLRDSF', 'COBSRQID', '3TSCPOS', 'AOPCADMD', 'COBSRQID', 'CORADMEN']

def fetch_telemetry(stop = None):
    fetch_result, stop = get_blobs(stop)
#
#--- If the fetch result contains no blobs, then we are out of comm. 
#
    if len(fetch_result['blobs']) > 0:
        latest_data_points = keep_latest_data_point(fetch_result)

        unit_converted_data = unit_conversion(latest_data_points)

        pseudo_update_data = generate_psuedo_msids(unit_converted_data)
#
#--- Pull the last known values of other msids used in comparing limit values
#--- If there is a file corruption of the comparison values, then pull the backup copy.
#
        _comp_limit = HOUSE_KEEPING / 'comp_limit_values.json'
        try:
            with open(_comp_limit) as f:
                comp_lim_values = json.load(f)
        except json.JSONDecodeError:
            shutil.copyfile(HOUSE_KEEPING / 'comp_limit_values.json~', _comp_limit)
            with open(_comp_limit) as f:
                comp_lim_values = json.load(f)

#
#--- If the current blob update contains data from COMP_LIM_SELECTION, then update
#
        for msid in COMP_LIM_SELECTION:
            x = pseudo_update_data.get(msid)
            if x is not None:
                comp_lim_values[msid] = str(x['value'])
        
        with open(_comp_limit,"w") as f:
            json.dump(comp_lim_values,f,indent = 4)

        limit_checked_data = check_limit_status(pseudo_update_data, comp_lim_values)

        update_json_blobs(limit_checked_data)

def get_blobs(stop = None):
    """
    Fetch the telemetry data using maude
    """
#
#--- If no time frame is passed, then pull current time and format into cxotime
#
    if stop is None:
        stop = CxoTime().secs
    else:
        stop = CxoTime(stop).secs
    start = stop - FETCH_SECONDS
#
#--- Fetch the blobs in question
#
    result = maude.get_blobs(start = start, stop = stop, **FETCH_KWARGS)

    return result, stop

def keep_latest_data_point(fetch_result):
    """
    Format fetch result to only contain the latest data point
    """
#
#--- Iterate over results in time reverse order, therefore added data is latest in result
#
    latest_data_points = {}
    for blob in fetch_result['blobs'][::-1]:
#
#--- For each time point, iterate over msid's recorded in this section
#
        for val in blob['values']:
            if val['n'] not in latest_data_points.keys():
                latest_data_points[val['n']] = {'time': blob['time'], 'value': val['vc'] }

    return latest_data_points

def unit_conversion(data):
    """
    Perform a unit conversion for a few special edge cases.
    If statement check since it's possible that one of the MSID's is not in this round of blob updates
    """
    update_msids = data.keys()
#
#--- Shield Rates
#
    for msid in ['2DETART', '2SHLDART', '2SHLDBRT', '2DETBRT']:
        if msid in update_msids:
            data[msid]['value'] = f"{round((float(data[msid]['value']) / 256.0), 2)}"
#
#--- ACA Integration Time
#
    if 'AOACINTT' in update_msids:
        data['AOACINTT']['value'] = f"{float(data['AOACINTT']['value']) / 1000}"
#
#--- Momentum and Bias
#
    for msid in ['AOGBIAS1', 'AOGBIAS2', 'AOGBIAS3', 'AORATE1', 'AORATE2', 'AORATE3']:
        if msid in update_msids:
#
#----arcsec/sec
#
            data[msid]['value'] = (float(data[msid]['value']) * u.rad/u.s).to('arcsec/s').value
#    
#--- Dither
#
    for msid in ['AODITHR2', 'AODITHR3']:
        if msid in update_msids:
            data[msid]['value'] = f"{float(data[msid]['value']) * 3600.0}"
#
#--- AC CCD Temperature
#
    if 'AACCCDPT' in update_msids:
#
#---Convert F to C
#
        data['AACCCDPT']['value'] = f"{5.0 * (float(data['AACCCDPT']['value']) -32) / 9.0}"
#
#--- Battery SOC Range
#
    for msid in ['EOCHRGB1', 'EOCHRGB2', 'EOCHRGB3']:
        if msid in update_msids:
            data[msid]['value'] = f"{float(data[msid]['value']) * 100.0}"

    return data


def generate_psuedo_msids(data):
    """
    Create psuedo MSIDs for display
    """
#
#--- Create "ACIS Stat7-0" msid
#
    stat_set = ['1STAT7ST', '1STAT6ST', '1STAT5ST', '1STAT4ST', '1STAT3ST', '1STAT2ST', '1STAT1ST', '1STAT0ST']
    if all(msid in data.keys() for msid in stat_set):
        string = ''
        time = 0
        for msid in stat_set:
            if data[msid]['time'] > time:
                time = data[msid]['time']
            if float(data[msid]['value']) == 1:
                string += 'T'
            else:
                string += 'F'
        data['ACISSTAT'] = {'time': time, 'value': string}
#
#--- Compute ACA Fiducial
#
    aca_fid_set = ['AOACFID0', 'AOACFID1','AOACFID2','AOACFID3','AOACFID4','AOACFID5','AOACFID6','AOACFID7']
    if all(msid in data.keys() for msid in aca_fid_set):
        string = ''
        time = 0
        for msid in aca_fid_set:
            if data[msid]['time'] > time:
                time = data[msid]['time']
#
#--- First letter in string
#
            string += data[msid]['value'][0]
        data['AOACFIDC'] = {'time': time, 'value': string}
#
#--- Compute ACA Image
#
    aca_image_set = ['AOACFCT0', 'AOACFCT1','AOACFCT2','AOACFCT3','AOACFCT4','AOACFCT5','AOACFCT6','AOACFCT7']
    if all(msid in data.keys() for msid in aca_image_set):
        string = ''
        time = 0
        for msid in aca_image_set:
            if data[msid]['time'] > time:
                time = data[msid]['time']
#
#--- First letter in string
#
            string += data[msid]['value'][0]
        data['AOACFCTC'] = {'time': time, 'value': string}

    return data

def check_limit_status(data, comp_limit_values):
    """
    Include the limit status into the data structure
    """
    for msid, entry in data.items():
        status = cms.check_status(msid, entry['value'], LIMIT_DICT, comp_limit_values)
        data[msid]['scheck'] = status
    return data

def update_json_blobs(data):
    """
    Iterate through blob_<part>.json updating each data value
    """
    for part in BLOB_SECTIONS:
#
#--- If there is a file corruption of the JSON blob, then notify admin and pull the backup copy up.
#
        _blob_file = SOH_WEB_DIR / f"blob_{part}.json"
        try:
            with open(_blob_file) as f:
                data_list = json.load(f)
        except json.JSONDecodeError:
#
#--- Copy from backup
#
            shutil.copy2(_blob_file, SOH_WEB_DIR / "Backup" / f"error_{part}")
            shutil.copyfile(SOH_WEB_DIR / "Backup" / f"blob_{part}.json", _blob_file)
            with open(_blob_file) as f:
                data_list = json.load(f)
#
#--- Notify
#           
            content = f"CSH Json file corruption. Please check {SOH_WEB_DIR}/Backup/error_{part}."
            subject = f"Corrupted CSH File {SOH_WEB_DIR}/Backup/error_{part}"
            send_mail(content, subject, ADMIN)
#
#--- Remove the dummy time entry
#
        for i in range(len(data_list)):
            if data_list[i]['msid'] == "LASTDCHECK":
                data_list.pop(i)
                break

#
#--- Iterate over the specific parts entires via indexing, so that the list can be edited
#
        for i in range(len(data_list)):
            msid = data_list[i]['msid']
            if msid in data.keys():
                if data[msid]['time'] > data_list[i]['time']:
#
#--- Run the update
#
                    data_list[i]['time'] = float(data[msid]['time'])
                    data_list[i]['value'] = str(data[msid]['value'])
                    data_list[i]['scheck'] = str(data[msid]['scheck'])
#
#--- Include a dummy time entry for the last updated time
#--- Javascript built to read custom time format.
#
        data_list.append({'msid': "LASTDCHECK", 
                          'index': "97989",
                          'time': NOW.strftime("%Y%j%H%M%S.000"),
                          'value': NOW.strftime("%Y-%m-%dT%H:%Mz"),
                          'f': "1"
                          })
        with open(_blob_file, 'w') as f:
            json.dump(data_list, f, indent = 4)

def send_mail(subject, content, address):
    """Send Emails

    :param subject: Subject line
    :type subject: str
    :param content: Email content as string
    :type content: str
    :param address: Email address of the recipient
    :type address: str
    """
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['To'] = address

    if _TESTMAIL:
        print(msg)
    else:
        p = Popen(["/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        p.communicate(msg.as_bytes())

def _fetch_comp_limit_values(stop = None):
    """
    Setup comparison limit values for limit checking between runs if values no in recent blobs.
    """
    fetch_result = maude.get_msids(msids = COMP_LIM_SELECTION, stop = args.stop, nearest = True)
    comp_lim_values = {}
    for entry in fetch_result['data']:
        comp_lim_values[entry['msid']] = str(entry['values'][-1])
    return comp_lim_values

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of json blob.")
    parser.add_argument("--stop", help= "CXO formatted stop time for a specific blob fetch.")
    args = parser.parse_args()

    #: Setup comparison limit values if not present
    _comp_lim_values_json = HOUSE_KEEPING / "comp_limit_values.json"
    if not _comp_lim_values_json.is_file():
        _fetch = _fetch_comp_limit_values(args.stop)
        with open(_comp_lim_values_json,"w") as f:
            json.dump(_fetch, f, indent = 4)
#
#--- Determine if running in test mode and change pathing if so
#
    if args.mode == "test":
#
#--- Path output to same location as unit tests
#       
        _old = SOH_WEB_DIR
        if args.path:
            SOH_WEB_DIR = Path(args.path)
        else:
            SOH_WEB_DIR = Path(os.getcwd(), "test", "_outTest")
        os.makedirs(SOH_WEB_DIR, exist_ok=True)
        for part in BLOB_SECTIONS:
            #: Copy blob from live running if not present in test case
            _blob_file = SOH_WEB_DIR / f"blob_{part}.json"
            if not _blob_file.is_file():
                shutil.copyfile(_old / f"blob_{part}.json", _blob_file)
        
        fetch_telemetry(stop = args.stop)

    elif args.mode == "flight":
        #: Create a lock file and exit strategy in case of race conditions.
        name = os.path.basename(__file__).split(".")[0]
        user = os.getenv("USER", "mta")
        lock = Path("/tmp", user, f"{name}.lock")

        #: If lock file exists, read the pid and kill the process, then remove the lock file
        if os.path.isfile(lock):
            #: Notify stall or error 
            notification = f"Lock file exists as {lock}. Process already running/errored out for script {os.path.abspath(__file__)}"
            send_mail(notification, f"Stalled Script: {name}", ADMIN)
            with open(lock) as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGTERM)
            os.remove(lock)
        
        #: Lock file with current pid
        pid = os.getpid()
        os.makedirs(os.path.dirname(lock), exist_ok = True)
        with open(lock, 'w') as f:
            f.write(str(pid))

        fetch_telemetry(stop = args.stop)

        #: Remove lock file once process is completed
        os.remove(lock)