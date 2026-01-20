#!/proj/sot/ska3/flight/bin/python

"""
**csh_plots.py**: Use the msid_plotting package to generate recent plots of maude CSH MSID's.

:Author: W. Aaron (william.aaron@cfa.harvad.edu)
:Last Updated: Jan 06, 2026

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "msid_plotting>=0.3",
# ]
# ///

# /// testing
# tested-ska-release = "2026.1"
# ///
"""
import os
import json
import argparse
from typing import Dict, Any
from datetime import timedelta
from cxotime import CxoTime

import msid_plotting
from msid_plotting import comm_check

#
#--- Define Directory Pathing
#
BIN_DIR = "/data/mta4/Script/SOH"
PLOT_DIR = "/data/mta4/www/CSH/Plots"
HOUSE_KEEPING = f"{BIN_DIR}/house_keeping"
PLOT_CONFIG_FILE = f"{HOUSE_KEEPING}/plot_configurations.json"
NOW = CxoTime()
BIN_SIZE = 500
RUN = False #: Override the comm check and run regardless
_NCOLS = {
    1:1,
    2:2,
    3:3,
    4:2,
    5:3,
    6:3,
    7:3,
    8:3,
    9:3
}

def get_options(args=None):
    parser = argparse.ArgumentParser(description="Plot Maude CSH MSIDs")
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("--config", required = False, help="Pass alternative plot configuration JSON file.")
    parser.add_argument("--force-run", action='store_true', help="Force the script to run regardless of being in comm.")
    opt = parser.parse_args(args)
    return opt

def main():
    """
    Check if we are in comm and plot recent maude data.
    """
    #: Pull DSN Comm Information
    comm_info = comm_check.comm_check()
    comm_time_info = comm_check.translate(comm_info['comm'])
    state_info = comm_check.in_state(**comm_time_info)

    #: Format the DSN Comm information as a title annotation to plots
    if state_info['in_track']:
        #: Updating the data in plot right now
        run = True
        comm_annotation = f"Last Updated: {NOW.date}\n"
        comm_annotation += f"Current Comm Ends: {comm_time_info['track_stop'].date}"
    elif comm_time_info['track_stop'] < NOW < comm_time_info['support_stop']:
        #: Just finished comm. Run once more and format the annotation for the next comm
        run = True
        comm_annotation = f"Last Updated: {comm_time_info['track_stop'].date}\n"
        _time_info = comm_check.translate(comm_info['dsn_query'][1])
        comm_annotation += f"Next DSN Comm: {_time_info['track_start'].date}"
    else:
        run = False
        #: Automated run choice is to not run the script,
        #: but generate the annotations in case the global RUN choice is true.
        _time_info = comm_check.translate(comm_info['previous_comm'])
        comm_annotation = f"Last Updated: {_time_info['track_stop'].date}\n"
        comm_annotation += f"Next DSN Comm: {comm_time_info['track_start'].date}"

    if run or RUN:        
        with open(PLOT_CONFIG_FILE) as f:
            plot_configurations = json.load(f)
        
        stop = NOW
        start = NOW - timedelta(days=2)

        #: Add Template Directory
        msid_plotting.msid_plot.JINJA_TEMPLATE_ENV.add_template_directory(
            f"{os.path.dirname(__file__)}/template"
        )

        for category, config in plot_configurations.items():
            msid_ls = config.get('msid_ls')
            title = config.get('title')
            units = config.get('units')
            weight = config.get('weight')

            template_variables = {
                'title': f"Plot: {category}",
                }
            generate_plot(category, msid_ls, start, stop, comm_annotation, title, units, weight, template_variables)

def generate_plot(category, msid_ls, start, stop, comm_annotation = None, title = None, units = None, weight = None, template_variables = {}):
    """
    Generate the plot html subpage for a given MSID set and associated parameters.
    """
    multivar_plot = msid_plotting.msid_plot.MSIDPlot(
        msids = msid_ls,
        start = start,
        stop = stop,
        bin_size = BIN_SIZE
    )

    params : Dict[str, Any] = {'size': 5}
    if title is not None:
        params['title'] = title
        if comm_annotation is not None:
            params['title'] += f"\n{comm_annotation}"
    if units is not None:
        params['y_axis_labels'] = [f"{msid}({unit})" for msid, unit in zip(multivar_plot.msids, units)]
    if weight is not None:
        params['weights'] = weight
    
    multivar_plot.parameterize(params)
    multivar_plot.fetch_data()

    html = multivar_plot.generate_plot_html(
        template_name='maude_csh_plot.jinja',
        template_variables = template_variables,
        ncols = _NCOLS[len(msid_ls)]
        )
    file = f"{PLOT_DIR}/{category}.html"

    with open(file,'w') as f:
        f.write(html)


if __name__ == "__main__":
    opt = get_options()
    if opt.mode == 'test':
        HOUSE_KEEPING = f"{os.getcwd()}/house_keeping"
        PLOT_CONFIG_FILE = f"{HOUSE_KEEPING}/plot_configurations.json"
        PLOT_DIR = f"{os.getcwd()}/test/_outTest/Plots"
        os.makedirs(PLOT_DIR, exist_ok = True)
        RUN = True
    if opt.config is not None:
        PLOT_CONFIG_FILE = opt.config
    RUN = RUN or opt.force_run
    main()