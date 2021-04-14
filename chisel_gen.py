#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import json
from datetime import datetime

reg_info_fname = 'registers.json'

reg_defs_pkg = 'NVMeCore'
reg_defs_fname = 'RegisterDefs.scala'
reg_defs_base = 'RegisterDef'

reg_file_fname = 'CSRMap.scala'
reg_file_cls = 'CSRFile'

timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

try:
	regs = json.loads(open(reg_info_fname, "r").read())
except Exception as e:
	print(f"failed to parse file {reg_info_fname}: {e}")
	exit(1)

with open(reg_defs_fname, "w") as reg_defs:
	reg_defs.write(f"// Generated on {timestamp}\n")
	reg_defs.write(f"package {reg_defs_pkg}\n\nimport chisel3._\n\n")
	for reg in regs:
		reg_defs.write(f"class {reg} extends {reg_defs_base} {{\n")
		for field in regs[reg]:
			reg_defs.write(f"\tval {field} = ")
			width = int(regs[reg][field]['width'])
			if width == 1:
				reg_defs.write("Bool()")
			else:
				reg_defs.write(f"UInt({width}.W)")
			reg_defs.write("\n")
		reg_defs.write("}\n\n\n")
