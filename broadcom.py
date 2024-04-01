#!/usr/bin/python3
"""
fetches Broadcom's JSON list of outbound IP address ranges
processes IPv4 address ranges
outputs CSV compatible with our corporate proxies table

curl -o broadcom.json https://servicepoints.threatpulse.com/
"""
import re
import csv
import sys
import json
import ipaddress

input_filename = 'broadcom.json'
output_filename = 'broadcom.csv'

with open(input_filename, 'r') as f:
    my_data = json.load(f)

fields = ['type', 'vendor', 'start', 'end', 'location', 'node']

with open(output_filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for dit in my_data:
        if dit in ['web_isolation', 'wss_datapath']:
            for dat in my_data[dit]:
                if dit == "web_isolation":
                    node = dat['location']
                    match = re.search(r'^(A-Za-z ]+),', node)
                    if match:
                        location = match.group(1)
                    else:
                        location = dat['location']
                    for my_range in dat['ranges']:
                        range = my_range['range']
                        try:
                            n = ipaddress.IPv4Network(range)
                            first, last = n[1], n[-2]
                            first_dec = int(first)
                            last_dec = int(last)
                            csvwriter.writerow(['isolation', 'broadcom', first_dec, last_dec, location, node])
                        except ValueError:
                            pass # not IPv4 CIDR
                else: # wss_datapath
                    node = dat['cluster']
                    location = dat['location']
                    for my_range in dat['ingress_egress_ranges']:
                        range = my_range['range']
                        try:
                            n = ipaddress.IPv4Network(range)
                            first, last = n[1], n[-2]
                            first_dec = int(first)
                            last_dec = int(last)
                            csvwriter.writerow(['swg', 'broadcom', first_dec, last_dec, location, node])
                        except ValueError:
                            pass # not IPv4 CIDR
