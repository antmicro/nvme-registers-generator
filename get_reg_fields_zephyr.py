#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import json
from datetime import datetime
from collections import OrderedDict
import subprocess
import os

prefix = "NVME_TC_REG_"

reg_info_fname = "registers.json"

reg_defs_fname = "nvme_reg_fields.h"
guard = reg_defs_fname.replace(".", "_").upper()

timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
git_hash = (
    subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
    .strip()
    .decode("ascii")
)
fname = os.path.basename(__file__)

reg_width = 32

try:
    regs = json.load(open(reg_info_fname, "r"), object_pairs_hook=OrderedDict)
except Exception as e:
    print(f"failed to parse file {reg_info_fname}: {e}")
    exit(1)


def get_reg_width(reg):
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

        define = f"{prefix}{name}_{field}"

        if width == 1:
            file.write(f"#define {define}\t(1<<{fstart})\n")
        else:
            file.write(f"#define {define}_MASK\t{hex(pow(2, width) - 1)}\n")
            file.write(f"#define {define}_SHIFT\t{fstart}\n")


with open(reg_defs_fname, "w") as reg_defs:
    reg_defs.write(f"// Generated on {timestamp} with {fname}, git rev {git_hash}\n")
    reg_defs.write(f"#ifndef {guard}\n#define {guard}\n\n")
    for reg in regs:
        total_width = get_reg_width(regs[reg])

        assert (total_width % reg_width) == 0

        if reg_width == total_width:
            write_fields(reg_defs, reg, regs[reg], 0, reg_width - 1)
        else:
            for i in range(int(total_width / reg_width)):
                write_fields(
                    reg_defs,
                    reg + "_" + str(i),
                    regs[reg],
                    i * reg_width,
                    (i + 1) * reg_width - 1,
                )

    reg_defs.write(f"\n#endif\n")
