#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import tabula
import re
import sys
from collections import OrderedDict

from ident_config import ident_config as config

nvme_spec = 'NVM-Express-1_4-2019.06.10-Ratified.pdf'

table = tabula.read_pdf(nvme_spec, pages='172-193', options="--use-line-returns", lattice=True)
regname = re.compile("\([A-Z]+\)")

def getname(description, reserved_count):

    if description == "Reserved":
        name = f"Reserved_{reserved_count}"
        reserved_count = reserved_count + 1
    else:
        name = re.search(r"\([A-Z0-9]+\)", description)
        if name is not None:
            name = name.group().strip('()')
        else:
            print(f"Unknown field [{description}]")
            raise
    return name, reserved_count

def fill_dict(name, offset, optional):
    fields = dict()
    fields[name] = dict()
    fields[name]['offset'] = offset
    fields[name]['optional'] = optional
    return fields

def validline(line, config):
    for field in config:
        if line[config[field]] == "None":
            return False
    return True

def parse(table, config, reserved_count):

    fields = OrderedDict()
    for line in table.iterrows():

        line = line[1]
        if validline(line, config):
            description = str(line[config['desc']]).replace('\r', ' ')
            offset = str(line[config['bytes']]).replace('\r', ' ')
            name, reserved_count = getname(description, reserved_count)
            optional = str(line[config['optional']]).replace('\r', ' ')
            fields.update(fill_dict(name, offset, optional))

    return fields, reserved_count

reserved_count = 0
fields = OrderedDict()

for tab in config:
    tmp_fields, reserved_count = parse(table[tab].fillna("None"), config[tab], reserved_count)
    fields.update(tmp_fields)

from pprint import pprint as pp
pp(fields)
