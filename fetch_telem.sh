#!/usr/bin/env bash
cd ${SOH_DIR}

#: Takes around 2-3 seconds to run. Runs every 20 seconds.
python fetch_telemetry.py -m flight
sleep 17
python fetch_telemetry.py -m flight
sleep 17
python fetch_telemetry.py -m flight
sleep 14
#: Allow three seconds for file copying of blobs and comparison values to occur
cp -f ${SOH_WEB_DIR}/blob_*.json ${SOH_WEB_DIR}/Backup/
cp -f ${SOH_DIR}/house_keeping/comp_limit_values.json ${SOH_DIR}/house_keeping/comp_limit_values.json~