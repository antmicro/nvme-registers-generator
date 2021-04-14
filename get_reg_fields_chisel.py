#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import json
from datetime import datetime
from collections import OrderedDict

reg_info_fname = 'registers.json'

reg_defs_pkg = 'NVMeCore'
reg_defs_fname = 'RegisterDefs.scala'
reg_defs_base = 'RegisterDef'

reg_file_fname = 'CSRMap.scala'
reg_file_cls = 'CSRFile'

timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

reg_width = 32

try:
	regs = json.load(open(reg_info_fname, "r"), object_pairs_hook=OrderedDict)
except Exception as e:
	print(f"failed to parse file {reg_info_fname}: {e}")
	exit(1)

def get_reg_width(reg):
	width = 0
	for field in reg:
		width += int(reg[field]['width'])

	return width

def write_fields(file, name, fields, start, end):
	file.write(f"class {name} extends {reg_defs_base} {{\n")
	cnt = 0
	for field in fields:
		bits = fields[field]['bits'].split(':')

		fstart = int(bits[-1])
		fend = int(bits[0])

		if (fstart > end) or (fend < start):
			continue

		fstart = max(fstart, start)
		fend = min(fend, end)
		width = fend - fstart + 1

		file.write(f"\tval {field} = ")
		file.write("Bool()" if width == 1 else f"UInt({width}.W)")
		file.write("\n")

	file.write("}\n\n\n")

with open(reg_defs_fname, "w") as reg_defs:
	reg_defs.write(f"// Generated on {timestamp}\n")
	reg_defs.write(f"package {reg_defs_pkg}\n\nimport chisel3._\n\n")
	for reg in regs:
		total_width = get_reg_width(regs[reg])

		assert((total_width % reg_width) == 0)

		if reg_width == total_width:
			write_fields(reg_defs, reg, regs[reg], 0, reg_width - 1)
		else:
			for i in range(int(total_width/reg_width)):
				write_fields(reg_defs, reg + '_' + str(i), regs[reg], i*reg_width, (i+1)*reg_width - 1)


