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
from datetime import timedelta
from cxotime import CxoTime
import msid_plotting

#
#--- Define Directory Pathing
#
BIN_DIR = "/data/mta4/Script/SOH"
PLOT_DIR = "/data/mta4/www/CSH/Plots"
HOUSE_KEEPING = f"{BIN_DIR}/house_keeping"
PLOT_CONFIG_FILE = f"{HOUSE_KEEPING}/plot_configurations.json"
NOW = CxoTime()
BIN_SIZE = 300

def get_options(args=None):
    parser = argparse.ArgumentParser(description="Plot Maude CSH MSIDs")
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("--config", required = False, help="Pass alternative plot configuration JSON file.")
    opt = parser.parse_args(args)
    return opt

def main():

    with open(PLOT_CONFIG_FILE) as f:
        plot_configurations = json.load(f)
    
    stop = NOW
    start = NOW - timedelta(days=3)

    for category, config in plot_configurations.items():
        msid_ls = config.get('msid_ls')
        title = config.get('title')
        units = config.get('units')
        weight = config.get('weight')
        generate_plot(category, msid_ls, start, stop, title, units, weight)

def generate_plot(category, msid_ls, start, stop, title = None, units = None, weight = None):

    multivar_plot = msid_plotting.msid_plot.MSIDPlot(
        msids = msid_ls,
        start = start,
        stop = stop,
        bin_size = BIN_SIZE
    )

    params = {}
    if title is not None:
        params['title'] = title
    if units is not None:
        params['y_axis_labels'] = [f"{msid}({unit})" for msid, unit in zip(multivar_plot.msids, units)]
    if weight is not None:
        params['weights'] = weight
    
    multivar_plot.parameterize(params)
    multivar_plot.fetch_data()

    html = multivar_plot.generate_plot_html()
    file = f"{PLOT_DIR}/{category}.html"

    with open(file,'w') as f:
        f.write(html)


if __name__ == "__main__":
    opt = get_options()
    if opt.mode == 'test':
        HOUSE_KEEPING = f"{os.getcwd()}/house_keeping"
        PLOT_DIR = f"{os.getcwd()}/test/_outTest"
        os.makedirs(PLOT_DIR, exist_ok = True)
    if opt.config is not None:
        PLOT_CONFIG_FILE = opt.config
    main()