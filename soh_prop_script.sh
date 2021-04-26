#!/bin/sh

if ps -ef | grep -v grep | grep "/data/mta4/Script/SOH/copy_data_from_occ.py prop" ; then
    exit 0
else
    export PYTHONPATH='/data/mta4/Script/Python3.8/envs/ska3-shiny/lib/python3.8/site-packages:/data/mta4/Script/Python3.8/lib/python3.8/site-packages/'
    export SKA='/proj/sot/ska'

    /data/mta4/Script/SOH/copy_data_from_occ.py prop
    exit 0
fi

