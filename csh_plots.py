#!/proj/sot/ska3/flight/bin/python

"""
**csh_plots.py**: Use the msid_plotting package to generate recent plots of maude CSH MSID's.

:Author: W. Aaron (william.aaron@cfa.harvad.edu)
:Last Updated: Jan 02, 2026

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "msid_plotting>=0.2",
# ]
# ///
"""
import sys
import os
import json
import argparse

import msid_plotting

#
#--- Define Directory Pathing
#
BIN_DIR = "/data/mta4/Script/SOH"
HTML_DIR = "/data/mta4/www/CSH"
HOUSE_KEEPING = f"{BIN_DIR}/house_keeping"

def get_options(args=None):
    parser = argparse.ArgumentParser(description="Plot Maude CSH MSIDs")
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    opt = parser.parse_args(args)
    return opt

def main(sys_args=None):
    opt = get_options()
    
    if opt.mode == 'test':
        HOUSE_KEEPING = f"{os.getcwd()}/house_keeping"
        HTML_DIR = f"{os.getcwd()}/test/_outTest"
        os.makedirs(HTML_DIR, exist_ok = True)

    with open(f"{HOUSE_KEEPING}/plot_configurations.json") as f:
        plot_configurations = json.load(f)
    

if __name__ == "__main__":
    main()