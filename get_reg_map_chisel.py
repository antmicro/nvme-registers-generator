#!/usr/bin/env python3
#
# Copyright (c) 2022 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import subprocess
import tabula

from datetime import datetime

REG_WIDTH = 4
PREFACE_TPL = "// Generated on {timestamp} with {file_name}{additional_info}\n\n"

OBJ_NAME = "CSRRegMap"
REG_MAP_PKG = "NVMeCore"
REG_DEF_BASE = "BaseRegister"
RW_REG_TYPE = "StorageRegister"
RO_REG_TYPE = "ReadOnlyRegister"
RO_REGS = ["CAP", "VS"]
SPEC_PAGES = "42-43"


def add_reg(file, name, addr, reg_type):
    file.write(
        f"\t\t {hex(addr)} -> Module(new {reg_type}(new {name}, {REG_WIDTH * 8})),\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a chisel file with the nvme registers map"
    )
    parser.add_argument("input", help="input PDF file with specification")
    parser.add_argument("output", help="output chisel file")
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

    with open(args.output, "w") as reg_map:
        reg_map.write(preface)
        reg_map.write(f"package {REG_MAP_PKG}\n\nimport chisel3._\n\n")
        reg_map.write(f"object {OBJ_NAME} {{\n")
        reg_map.write(f"\tval regMap = Map [Int, {REG_DEF_BASE}] (\n")

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

            reg_type = RW_REG_TYPE
            if name in RO_REGS:
                reg_type = RW_REG_TYPE

            if size == REG_WIDTH:
                add_reg(reg_map, name, start, reg_type)
            else:
                for i in range(int(size / REG_WIDTH)):
                    add_reg(
                        reg_map, name + "_" + str(i), start + i * REG_WIDTH, reg_type
                    )

        reg_map.write("\t)\n}\n")
