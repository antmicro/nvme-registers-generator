#!/usr/bin/env python3
#
# Copyright 2021-2022 Western Digital Corporation or its affiliates
# Copyright 2021-2022 Antmicro
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import subprocess
import tabula

from datetime import datetime

PREFIX = "NVME_TC_REG_"
PREFACE_TPL = "// Generated on {timestamp} with {file_name}{additional_info}\n\n"
REG_WIDTH = 4
SPEC_PAGES = "42-43"


def add_reg(file, name, addr):
    file.write(f"#define\t{PREFIX}{name}\t{hex(addr)}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a header file with the registers map for zephyr"
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
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise Exception("Input file does not exist")

    if os.path.exists(args.output) and not args.force:
        raise Exception(f"{args.output} exists. Use -f to overwrite it")

    table = tabula.read_pdf(
        args.input, pages=SPEC_PAGES, options="--use-line-returns", lattice=True
    )

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    file_name = os.path.basename(args.input)
    additional_info = ""
    if args.git_sha is not None:
        additional_info = ", git_sha {}".format(args.git_sha)

    preface = PREFACE_TPL.format(
        timestamp=timestamp, file_name=file_name, additional_info=additional_info
    )
    guard = os.path.basename(args.output.replace(".", "_").upper())
    with open(args.output, "w") as reg_map:
        reg_map.write(preface)
        reg_map.write(f"#ifndef {guard}\n#define {guard}\n\n")

        for line in table[0].iterrows():
            line = line[1]
            name = line["Unnamed: 1"]

            if name == "Reserved" or name == "SQ0TDBL":
                continue

            try:
                start = int(line["Unnamed: 0"][:-1], base=16)
                end = int(line["Start"][:-1], base=16)
                size = end - start + 1
            except ValueError:
                continue

            if args.verbose:
                print(f"Register: {name} {hex(start)}-{hex(end)}, {size} bytes")

            assert (size % REG_WIDTH) == 0

            if size == REG_WIDTH:
                add_reg(reg_map, name, start)
            else:
                for i in range(int(size / REG_WIDTH)):
                    add_reg(reg_map, name + "_" + str(i), start + i * REG_WIDTH)

        reg_map.write("\n#endif\n")
