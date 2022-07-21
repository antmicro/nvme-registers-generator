#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import os
import subprocess

from collections import OrderedDict
from datetime import datetime

PREFIX = "NVME_TC_REG_"
PREFACE_TPL = "// Generated on {timestamp} with {file_name}{additional_info}\n\n"
REG_WIDTH = 32


def get_REG_WIDTH(reg):
    width = 0
    for field in reg:
        width += int(reg[field]["width"])

    return width


def write_fields(file, name, fields, start, end):
    for field in fields:
        bits = fields[field]["bits"].split(":")

        fstart = int(bits[-1])
        fend = int(bits[0])

        if (fstart > end) or (fend < start):
            continue

        fstart = max(fstart, start) - start
        fend = min(fend, end) - start
        width = fend - fstart + 1

        define = f"{PREFIX}{name}_{field}"

        if width == 1:
            file.write(f"#define {define}\t(1<<{fstart})\n")
        else:
            file.write(f"#define {define}_MASK\t{hex(pow(2, width) - 1)}\n")
            file.write(f"#define {define}_SHIFT\t{fstart}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a header file with the nvme registers for zephyr"
    )
    parser.add_argument("input", help="input JSON file with registers description")
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
        raise Exception(f"{args.output} exists. Use -f to overwrite it")

    with open(args.input, "r") as registers_json:
        try:
            regs = json.load(registers_json, object_pairs_hook=OrderedDict)
        except Exception as e:
            print(f"failed to parse file {args.input}: {e}")
            exit(1)

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    file_name = os.path.basename(args.input)
    additional_info = ""
    if args.git_sha is not None:
        additional_info = ", git_sha {}".format(args.git_sha)

    preface = PREFACE_TPL.format(
        timestamp=timestamp, file_name=file_name, additional_info=additional_info
    )
    guard = args.output.replace(".", "_").upper()
    with open(args.output, "w") as reg_defs:
        reg_defs.write(preface)
        reg_defs.write(f"#ifndef {guard}\n#define {guard}\n\n")

        for reg in regs:
            total_width = get_REG_WIDTH(regs[reg])
            assert (total_width % REG_WIDTH) == 0

            if REG_WIDTH == total_width:
                write_fields(reg_defs, reg, regs[reg], 0, REG_WIDTH - 1)
            else:
                for i in range(int(total_width / REG_WIDTH)):
                    write_fields(
                        reg_defs,
                        reg + "_" + str(i),
                        regs[reg],
                        i * REG_WIDTH,
                        (i + 1) * REG_WIDTH - 1,
                    )

        reg_defs.write(f"\n#endif\n")
