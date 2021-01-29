#!/usr/bin/env /data/mta4/Script/Python3.6/envs/ska3/bin/python

import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description = "test")
parser.add_argument('msid_group', help = "MSID Grouping")
args = parser.parse_args()
msid_group = args.msid_group

message = """
Testing this nonsense
%s
%s
"""%(msid_group, str(datetime.now()))

file_name = msid_group + '_text.html'
with open(file_name, 'w') as f:
	f.write(message)

#print('Content-type: text/html\n')
#print('<title>Hello World</title>')
#print('Hello World!')
