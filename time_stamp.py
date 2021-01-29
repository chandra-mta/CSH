#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python


import os
import sys
import re
import string
import math
import time
import Chandra.Time

out = time.strftime('Current Time: %Y:%j:%H:%M Z', time.gmtime()) + '\n'
with open('/data/mta4/www/CSH/ctest', 'w') as fo:
    fo.write(out)
