#!/usr/bin/python3
"""
fetches Zscaler's JSON list of outbound IP address ranges
processes IPv4 address ranges
outputs CSV compatible with our corporate proxies table

curl -o zscaler.json https://config.zscaler.com/api/zscaler.net/cenr/json
"""
import re
import csv
import sys
import json
import ipaddress

input_filename = 'zscaler.json'
output_filename = 'zscaler.csv'

with open(input_filename, 'r') as f:
    my_data = json.load(f)

fields = ['type', 'vendor', 'start', 'end', 'location', 'node']

with open(output_filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for continent in my_data['zscaler.net']:
        for city in  my_data['zscaler.net'][continent]:
            match = re.search(r'^city : ([A-Za-z ]+)$', city)
            if match:
                node = match.group(1)
                match2 = re.search(r'^([A-Za-z ]+)( [IV]+)$', node)
                if match2:
                    real_city = match2.group(1)
                else:
                    real_city = node
            else:
                print('internal error')
                sys.exit(1)
            print(f"{real_city} - {node}")
            for pop in my_data['zscaler.net'][continent][city]:
                try:
                    n = ipaddress.IPv4Network(pop['range'])
                    first, last = n[1], n[-2]
                    first_dec = int(first)
                    last_dec = int(last)
                    print(first, last)
                    csvwriter.writerow(['swg', 'zscaler', first_dec, last_dec, real_city, node])
                except ValueError:
                    pass # not IPv4 CIDR
