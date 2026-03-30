# Fetch Blob Data from OCC Side to SOT Side

## Scripts:

### fetch_telem.sh
Shell script to handle twenty second updates to fetching telemetry and comm information

### fetch_telemetry.py
Fetch the latest telemetry data using maude.get_blobs() and then structure them into
the CSH blob_<part>.json files.

### check_msid_status.py

Submodule called by fetch_telemetry.py; check status of MSIDs.

### next_comm_check.py
Create a display time span till the next comm.
        
#### Output:
- <soh_web_dir>/ncomm.xml

### read_comm_time.py

Read comm timing and create a table.

#### Input:      
- http://cxc.harvard.edu/mta/ASPECT/arc/
        
#### Output:
- <soh_web_dir>/comm_list.html

### csh_plots.py
Use the msid_plotting MTA package to generate multivariate MSID plot subpages

#### Input:
- <house_keeping>/plot_configurations.json

#### Output:
- <soh_web_dir>/Plots/*.html

### csh_limits_supplemental.py
Update the supplemental limit information, including descriptions and thresholds.

#### Input:
- /data/mta4/MTA/data/op_limits/glimmondb.sqlite3
- https://occweb.cfa.harvard.edu/occweb/web/fot_web/software/sandbox/SOT_area/msididx.json
     
#### Output:
- <house_keeping>/CSH_limit_table.json
- <house_keeping>/msididx.json
- <soh_web_dir>/msididx.json

### Data:

#### blob_<part>.json:

blob_<part>.json is constructed locally by copy_data_from_occ.py using maude function.

Example: `{"msid":"AOPCADMD","index":"2416","time":"2018131120936.285","value":"NPNT","f": "1"}`
        
- msid    --- MSID of this data
- index   --- Index of this MSID corresponding to that of msididx.json
- time    --- Time: 2018:131:12:09:36.285
- value   --- Current value
- f       --- This is a dummy input for this app

#### msididx.json:

Example: `{"name": "AOPCADMD", "idx": 2416, "description": "PCAD MODE", "sc": ["STBY","NPNT","NMAN","NSUN","PWRF","RMAN","NULL"]}`

- name    --- MSID
- idx     --- Index of this MSID
- description --- Description of this MSID
- sc          --- Possible values
- limit/switch/set  --- If switch value takes a certain value, set is used for expected value.

```
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
```

msididx.json is downloaded from https://occweb.cfa.harvard.edu/occweb/web/fot_web/software/sandbox/SOT_area/msididx.json

## Cron Variables:
###### Primary
```
SOH_DIR=/data/mta4/Script/SOH
SOH_WEB_DIR=/data/mta4/www/CSH
ENV_FLIGHT=/proj/sot/ska3/flight
```
###### Secondary
```
SOH_DIR=/data/mta/Script/SOH
SOH_WEB_DIR=/data/mta_www/MIRROR/CSH
ENV_FLIGHT=/proj/sot/ska3/flight
```
###### ASVT
```
SOH_DIR=/data/mta/Script/SOH_ASVT
SOH_WEB_DIR=/data/mta4/www/CSH_ASVT
ENV_FLIGHT=/proj/sot/ska3/flight
```

## Cron Jobs:
###### Primary (mta@boba-v)
```
* * * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/fetch_telem.sh >> ${HOME}/Logs/soh_fetch_telem.cron 2>&1
34 1 * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/read_comm_time.py -m flight >> ${HOME}/Logs/soh_read_comm.cron 2>&1
*/10 * * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/csh_plots -m flight >> ${HOME}/Logs/generate_csh_plots.cron 2>&1
40 1 1 * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/csh_limits_supplemental.py >> ${HOME}/Logs/soh_lim_desc.cron 2>&1

```
###### Secondary (mta@c3po-v)
```
* * * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/fetch_telem.sh >> ${HOME}/Logs/soh_fetch_telem_bu.cron 2>&1
34 1 * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/read_comm_time.py -m flight >> ${HOME}/Logs/soh_read_comm_bu.cron 2>&1
*/10 * * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/csh_plots -m flight >> ${HOME}/Logs/generate_csh_plots_bu.cron 2>&1
40 1 1 * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/csh_limits_supplemental.py >> ${HOME}/Logs/soh_lim_desc_bu.cron 2>&1
```
###### ASVT (mta@luke-v)
```
* * * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/fetch_telem.sh >> ${HOME}/Logs/asvt_fetch_telem.cron 2>&1
34 1 * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/read_comm_time.py -m flight >> ${HOME}/Logs/asvt_read_comm.cron 2>&1
*/10 * * * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/csh_plots -m flight >> ${HOME}/Logs/generate_asvt_plots.cron 2>&1
40 1 1 * * ${ENV_FLIGHT}/bin/skare ${SOH_DIR}/csh_limits_supplemental.py >> ${HOME}/Logs/asvt_lim_desc.cron 2>&1
```

## Web:

* https://cxc.cfa.harvard.edu/mta/CSH/index.html
* https://cxc.cfa.harvard.edu/mta/CSH/soh_snap_tab.html


### Notes on HTMLs:

<outdir> contains the HTML files, JSON data, and Backbone.js related scripts.

js/lib          --- Contains library of Backbone.js related JavaScript files.

js/models       --- Contains models to be used.
                    msid.js      --- MSID model.
                    blob.js     --- Blob model.
                    msidinfo.js --- msididx model.

js/view         --- Contains view (HTML page construction related) JavaScript.
                    msidview.js --- This creates view of MSID. It can contain some computation related to the MSID.

js/collection   --- Collections of JavaScript files.