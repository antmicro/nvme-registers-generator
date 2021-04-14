#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import tabula
from datetime import datetime

nvme_spec = 'NVM-Express-1_4-2019.06.10-Ratified.pdf'

obj_name = 'CSRRegMap'

reg_map_pkg = 'NVMeCore'
reg_map_fname = 'CSRRegMap.scala'

reg_width = 4
reg_type = 'SimpleRegRegister'
reg_def_base = 'Register'

timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

table = tabula.read_pdf(nvme_spec, pages='42-43', options="--use-line-returns", lattice=True)

def add_reg(file, name, addr, reg_type):
	file.write(f"\t\t {hex(addr)} -> Module(new {reg_type}(new {name}, {reg_width*8})),\n")

with open(reg_map_fname, "w") as reg_map:
	reg_map.write(f"// Generated on {timestamp}\n")
	reg_map.write(f"package {reg_map_pkg}\n\nimport chisel3._\n\n")
	reg_map.write(f"object {obj_name} {{\n")
	reg_map.write(f"\tval regMap = Map [Int, {reg_def_base}] (\n")
	for line in table[0].iterrows():
		line = line[1]

		name = line['Unnamed: 1']

		if name == 'Reserved':
			continue

		try:
			start = int(line['Unnamed: 0'][:-1], base=16)
			end = int(line['Start'][:-1], base=16)
			size = end - start + 1
		except ValueError:
			continue

		print(f"Register: {name} {hex(start)}-{hex(end)}, {size} bytes")

		assert((size % reg_width) == 0)

		if size == reg_width:
			add_reg(reg_map, name, start, reg_type)
		else:
			for i in range(int(size/reg_width)):
				add_reg(reg_map, name + '_' + str(i), start + i*reg_width, reg_type)

	
	reg_map.write("\t)\n}\n")
