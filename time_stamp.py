#!/usr/bin/env /data/mta4/Script/Python3.8/envs/ska3-shiny/bin/python


import os
import sys
import re
import string
import math
import time
import Chandra.Time

out = time.strftime('Current Time: %Y:%j:%H:%M Z', time.gmtime()) + '\n'
with open('/data/mta4/www/CSH/ctest.xml', 'w') as fo:
    fo.write(out)
