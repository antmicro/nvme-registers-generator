#!/usr/bin/env python3
import tabula
import re
import sys
from collections import OrderedDict

from regs_config import regs_config as config

nvme_spec = 'NVM-Express-1_4-2019.06.10-Ratified.pdf'

table = tabula.read_pdf(nvme_spec, pages='43-62', options="--use-line-returns", lattice=True)
regname = re.compile("\([A-Z]+\)")

def getname(description, reserved_count):

    if description == "Reserved":
        name = f"Reserved_{reserved_count}"
        reserved_count = reserved_count + 1
    else:
        name = re.search(r"\([A-Z]+\)", description)
        if name is not None:
            name = name.group().strip('()')
        else:
            print(f"Unknown field [{description}]")
            raise
    return name, reserved_count

def fill_dict(name, bits, access, description, reset, width):
    fields = dict()
    fields[name] = dict()
    fields[name]['bits'] = bits
    fields[name]['type'] = access
    fields[name]['description'] = description
    fields[name]['reset'] = reset
    fields[name]['width'] = width
    return fields

def getwidth(bits):
    if ':' in bits:
        return int(bits.split(':')[0]) - int(bits.split(':')[1]) + 1
    else:
        return 1

def dump(table):
    for line in table.iterrows():
        line = line[1]
        print(line)

def validline(line, config):
    for field in config:
        if field == 'names':
            continue
        if line[config[field]] == "None":
            return False
    return True

def parse(table, config, reserved_count):

    fields = OrderedDict()
    for line in table.iterrows():

        #print(line)
        line = line[1]
        if validline(line, config):
            description = str(line[config['desc']]).replace('\r', ' ')

            bits = str(line[config['bits']]).replace('\r', ' ')
            name = None
            if 'names' in config:
                if bits in config['names']:
                    name = config['names'][bits]
            if name is None:
                name, reserved_count = getname(description, reserved_count)

            access = str(line[config['access']]).replace('\r', ' ')
            reset = str(line[config['reset']]).replace('\r', ' ')
            width = getwidth(bits)
            fields.update(fill_dict(name, bits, access, description, reset, width))

    return fields, reserved_count

regs = OrderedDict()
test = False
if not test:
    for reg in config:
        regs[reg] = OrderedDict()
        reserved_count = 0
        for tab in config[reg]:
            print(f"reg: {reg}, tab: {tab}")
            tmp_regs, reserved_count = parse(table[tab].fillna("None"), config[reg][tab], reserved_count)
            regs[reg].update(tmp_regs)
else:
    reg = 'PMRMSCL'
    for tab in config[reg]:
        print(f"reg: {reg}, tab: {tab}")
        dump(table[tab].fillna("None"))

import json
with open("registers.json", "w") as fp:
        json.dump(regs, fp, indent=4)

from pprint import pprint as pp
pp(regs)
