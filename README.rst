#########################################################
Fetch Blob Data from OCC Side to SOT Side
#########################################################

Scripts:
========

fetch_telemetry.py
------------------
Fetch the latest telemetry data using maude.get_blobs() and then structure them into
the CSH blob_<part>.json files.

check_msid_status.py
--------------------
Called by fetch_telemetry.py; check status of MSIDs.

read_comm_time.py
-----------------
Read comm timing and create a table.
        
Input: http://cxc.harvard.edu/mta/ASPECT/arc/
        
Output:
        
* <html_dir>/comm_list.html
* <house_keeping>/comm_list

mk_limit_table.py
-----------------
Update MSID limit table.
        
Input: /data/mta4/MTA/data/op_limits/glimmondb.sqlite3
        
Output: <house_keeping>/limit_table (also in SOH_ASVT)

update_msididx_data.py
----------------------
Update msididx.json
        
Input: 
* <house_keeping>/msididx_base
* <house_keeping>/limit_table
        
Output: <html_dir>/msididx.json

next_comm_check.py
------------------
Create a display time span till the next comm.
        
Input: None
        
Output: <web_dir>/ctest.xml

csh_plots.py
------------
Use the msid_plotting MTA package to generate multivariate MSID plot subpages

Input: <house_keeping>/plot_configurations.json

Output: <html_dir>/Plots/*.html

Data:
=====

blob_<part>.json:
----------
blob_<part>.json is constructed locally by copy_data_from_occ.py using maude function.

Example: {"msid":"AOPCADMD","index":"2416","time":"2018131120936.285","value":"NPNT","f": "1"}
        
* msid    --- MSID of this data
* index   --- Index of this MSID corresponding to that of msididx.json
* time    --- Time: 2018:131:12:09:36.285
* value   --- Current value
* f       --- This is a dummy input for this app

msididx.json:
-------------
Example: {"name": "AOPCADMD", "idx": 2416, "description": "PCAD MODE", "sc": ["STBY","NPNT","NMAN","NSUN","PWRF","RMAN","NULL"]}

* name    --- MSID
* idx     --- Index of this MSID
* description --- Description of this MSID
* sc          --- Possible values
* limit/switch/set  --- If switch value takes a certain value, set is used for expected value.

.. code-block:: python

        "lim": [
                {"switch": {"AOPCADMD":"NMAN"},
                 "set": {"wl":-0.03490658,"cl":-0.026179935,"ch":0.026179935,"wh":0.03490658}},
                {"switch":{"AOPCADMD":"NPNT"},
                 "set":{"wl":-0.0000977384,"cl":-0.0000488692,"ch":0.0000488692,"wh":0.0000977384}}
        ]
         
        * wl --- Lower warning
        * cl --- Lower caution
        * ch --- Upper caution
        * wh --- Upper warning

msididx.json was originally copied from:
    https://occweb.cfa.harvard.edu/occweb/web/fot_web/software/sandbox/SOT_area/msididx.json

Directory:
==========

* bin_dir: /data/mta4/Script/SOH/
* house_keeping: /data/mta4/Script/SOH/house_keeping/
* outdir: /data/mta4/www/CSH/

Web Address:
============

/data/mta4/www/CSH

* https://cxc.cfa.harvard.edu/mta/CSH/index.html
* https://cxc.cfa.harvard.edu/mta/CSH/soh_snap_tab.html

Environment Settings:
=====================

/proj/sot/ska3/flight/bin/skare

Cron Job:
=========

boba-v as mta:
--------------

- 40 1 1 \* \* cd /data/mta4/Script/SOH/; /data/mta4/Script/SOH/update_lim_desc_wrap_script
- \* \* \* \* \* /proj/sot/ska3/flight/bin/skare /data/mta4/Script/SOH/next_comm_check.py -m flight
- 34 1 \* \* \* cd /data/mta4/Script/SOH/; /proj/sot/ska3/flight/bin/skare /data/mta4/Script/SOH/read_comm_time.py -m flight
- \* \* \* \* \* cd /data/mta4/Script/SOH/; /data/mta4/Script/SOH/fetch_telem_wrap_script
- \*/10 \* \* \* \* cd /data/mta4/Script/SOH/; /data/mta4/Script/SOH/generate_plots_wrap_script

Notes on HTMLs:
===============

<outdir> contains the HTML files, JSON data, and Backbone.js related scripts.

js/lib          --- Contains library of Backbone.js related JavaScript files.

js/models       --- Contains models to be used.
                    msid.js      --- MSID model.
                    blob.js     --- Blob model.
                    msidinfo.js --- msididx model.

js/view         --- Contains view (HTML page construction related) JavaScript.
                    msidview.js --- This creates view of MSID. It can contain some computation related to the MSID.

js/collection   --- Collections of JavaScript files.

Note on Special Limits:
=======================

See: https://docs.google.com/spreadsheets/d/180iuA1_TPXOGpoOlZuk5OMqVH-O1-HD861XB5CSHKOg/edit#gid=0
Let me know if you need any further adjustments or additional information!
