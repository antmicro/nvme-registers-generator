#!/usr/bin/env python3
#
# Copyright (c) 2022 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import re
import subprocess
import sys
import tabula

from collections import OrderedDict
from datetime import datetime
from ident_config import ident_config as config

PREFIX = "NVME_ID_FIELD_"
PREFACE_TPL = "// Generated on {timestamp} with {file_name}{additional_info}\n\n"
REG_WIDTH = 32
SPEC_PAGES = "172-193"


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


def add_field(file, name, addr, size):
    file.write(f"#define\t{PREFIX}{name}\t{hex(addr)}\n")
    file.write(f"#define\t{PREFIX}{name}_SIZE\t{size}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a header file with the nvme field identifiers"
    )
    parser.add_argument("input", help="input PDF file with specification")
    parser.add_argument("output", help="output header file")
    parser.add_argument(
        "-f", "--force", action="store_true", help="overwrite output file if exists"
    )
    parser.add_argument(
        "--git-sha",
        default=None,
        help="Git sha written to generated file as additional info",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise Exception("Input file does not exist")

    if os.path.exists(args.output) and not args.force:
        raise Exception(f"{args.input} exists. Use -f to overwrite it")

    table = tabula.read_pdf(
        args.input, pages=SPEC_PAGES, options="--use-line-returns", lattice=True
    )

    fields = OrderedDict()
    for tab in config:
        tmp_fields = parse(table[tab].fillna("None"), config[tab])
        fields.update(tmp_fields)

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    file_name = os.path.basename(args.input)

    additional_info = ""
    if args.git_sha is not None:
        additional_info = ", git_sha {}".format(args.git_sha)

    preface = PREFACE_TPL.format(
        timestamp=timestamp, file_name=file_name, additional_info=additional_info
    )
    guard = args.input.replace(".", "_").upper()
    with open(args.output, "w") as ident_fields:
        ident_fields.write(preface)
        ident_fields.write(f"#ifndef {guard}\n#define {guard}\n\n")
        for field in fields:
            off = fields[field]["offset"].split(":")
            start = int(off[-1])
            end = int(off[0])
            add_field(ident_fields, field, start, end - start + 1)

        ident_fields.write(f"#endif\n")
