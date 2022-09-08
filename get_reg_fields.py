#!/usr/bin/env python3
#
# Copyright 2021-2022 Western Digital Corporation or its affiliates
# Copyright 2021-2022 Antmicro
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import os
import re
import tabula

from collections import OrderedDict
from regs_config import regs_config as config

SPEC_PAGES = "43-62"


def getname(description, reserved_count):
    if description == "Reserved":
        name = f"Reserved_{reserved_count}"
        reserved_count = reserved_count + 1
    else:
        name = re.search(r"\([A-Z]+\)", description)
        if name is not None:
            name = name.group().strip("()")
        else:
            raise Exception(f"Unknown field [{description}]")
    return name, reserved_count


def fill_dict(name, bits, access, description, reset, width):
    fields = {}
    fields[name] = {}
    fields[name]["bits"] = bits
    fields[name]["type"] = access
    fields[name]["description"] = description
    fields[name]["reset"] = reset
    fields[name]["width"] = width
    return fields


def getwidth(bits):
    if ":" in bits:
        return int(bits.split(":")[0]) - int(bits.split(":")[1]) + 1

    return 1


def dump(table):
    for line in table.iterrows():
        line = line[1]
        print(line)


def validline(line, config):
    for field in config:
        if field == "names":
            continue
        if line[config[field]] == "None":
            return False
    return True


def parse(table, config, reserved_count):
    fields = OrderedDict()
    for line in table.iterrows():
        line = line[1]
        if validline(line, config):
            description = str(line[config["desc"]]).replace("\r", " ")
            bits = str(line[config["bits"]]).replace("\r", " ")
            name = None

            if "names" in config:
                if bits in config["names"]:
                    name = config["names"][bits]
            if name is None:
                name, reserved_count = getname(description, reserved_count)

            access = str(line[config["access"]]).replace("\r", " ")
            reset = str(line[config["reset"]]).replace("\r", " ")
            width = getwidth(bits)
            fields.update(fill_dict(name, bits, access, description, reset, width))

    return fields, reserved_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract the description of the nvme registers form PDF to JSON"
    )
    parser.add_argument("input", help="input PDF file with specification")
    parser.add_argument("output", help="output JSON file")
    parser.add_argument(
        "-f", "--force", action="store_true", help="overwrite output file if exists"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise Exception("Input file does not exist")

    if os.path.exists(args.output) and not args.force:
        raise Exception(f"{args.output} exists. Use -f to overwrite it")

    table = tabula.read_pdf(
        args.input, pages=SPEC_PAGES, options="--use-line-returns", lattice=True
    )

    regs = OrderedDict()
    for reg in config:
        regs[reg] = OrderedDict()
        reserved_count = 0
        for tab in config[reg]:
            if args.verbose:
                print(f"reg: {reg}, tab: {tab}")
            tmp_regs, reserved_count = parse(
                table[tab].fillna("None"), config[reg][tab], reserved_count
            )
            regs[reg].update(tmp_regs)

    with open(args.output, "w") as fp:
        json.dump(regs, fp, indent=4)
