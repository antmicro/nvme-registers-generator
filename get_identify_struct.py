#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import tabula
from datetime import datetime
import subprocess
import re
import sys
from collections import OrderedDict
import os

from ident_config import ident_config as config

nvme_spec = "NVM-Express-1_4-2019.06.10-Ratified.pdf"

prefix = "NVME_ID_FIELD_"

ident_fields_fname = "nvme_ident_fields.h"

guard = ident_fields_fname.replace(".", "_").upper()

timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
git_hash = (
    subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
    .strip()
    .decode("ascii")
)
fname = os.path.basename(__file__)

table = tabula.read_pdf(
    nvme_spec, pages="172-193", options="--use-line-returns", lattice=True
)


def getname(description):
    name = re.search(r"\([A-Z0-9]+\)", description)
    if name is not None:
        name = name.group().strip("()")
    else:
        print(f"Unknown field [{description}]")
        raise
    return name


def fill_dict(name, offset, optional):
    fields = dict()
    fields[name] = dict()
    fields[name]["offset"] = offset
    fields[name]["optional"] = optional
    return fields


def validline(line, config):
    for field in config:
        if line[config[field]] == "None":
            return False
    return True


def parse(table, config):

    fields = OrderedDict()
    for line in table.iterrows():

        line = line[1]
        if validline(line, config):
            description = str(line[config["desc"]]).replace("\r", " ")
            offset = str(line[config["bytes"]]).replace("\r", " ")
            name = getname(description)
            optional = str(line[config["optional"]]).replace("\r", " ")
            fields.update(fill_dict(name, offset, optional))

    return fields


fields = OrderedDict()


def add_field(file, name, addr, size):
    file.write(f"#define\t{prefix}{name}\t{hex(addr)}\n")
    file.write(f"#define\t{prefix}{name}_SIZE\t{size}\n")


for tab in config:
    tmp_fields = parse(table[tab].fillna("None"), config[tab])
    fields.update(tmp_fields)

with open(ident_fields_fname, "w") as ident_fields:
    ident_fields.write(
        f"// Generated on {timestamp} with {fname}, git rev {git_hash}\n"
    )
    ident_fields.write(f"#ifndef {guard}\n#define {guard}\n\n")
    for field in fields:
        off = fields[field]["offset"].split(":")
        start = int(off[-1])
        end = int(off[0])
        add_field(ident_fields, field, start, end - start + 1)

    ident_fields.write(f"#endif\n")

from pprint import pprint as pp

pp(fields)
