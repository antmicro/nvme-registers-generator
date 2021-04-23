#!/usr/bin/env python3
#
# Copyright (c) 2021 Antmicro <www.antmicro.com>
#
# SPDX-License-Identifier: Apache-2.0
#

import tabula
from datetime import datetime
import subprocess
import os

nvme_spec = 'NVM-Express-1_4-2019.06.10-Ratified.pdf'

prefix = 'NVME_TC_REG_'

reg_map_fname = 'nvme_reg_map.h'

guard = reg_map_fname.replace('.', '_').upper()

reg_width = 4

timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('ascii')
fname = os.path.basename(__file__)

table = tabula.read_pdf(nvme_spec, pages='42-43', options="--use-line-returns", lattice=True)

def add_reg(file, name, addr):
	file.write(f"#define\t{prefix}{name}\t{hex(addr)}\n")

with open(reg_map_fname, "w") as reg_map:
	reg_map.write(f"// Generated on {timestamp} with {fname}, git rev {git_hash}\n")
	reg_map.write(f"#ifndef {guard}\n#define {guard}\n\n")
	for line in table[0].iterrows():
		line = line[1]

		name = line['Unnamed: 1']

		if name == 'Reserved' or name == 'SQ0TDBL':
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
			add_reg(reg_map, name, start)
		else:
			for i in range(int(size/reg_width)):
				add_reg(reg_map, name + '_' + str(i), start + i*reg_width)


	reg_map.write("\n#endif\n")
