NVMe register extraction tool
=============================

Copyright (c) 2021 [Antmicro](https://www.antmicro.com)

Those scripts can be used to generate register definitions needed by NVMe Chisel Core.

To install required dependencies use ``pip3 install -r requirements.txt``.

Usage
-----

First you need to generate ``registers.json`` file by using ``./get_reg_fields.py``.

Once that file is present you can then:

* Generate ``Bundle`` definitions that contain layout of each register using ``get_reg_fields_chisel.py``.
* Generate register map using ``get_reg_map_chisel.py``.
* Generate register definitions for use in the Zephyr app using ``get_reg_fields_zephyr.py`` and ``get_reg_map_zephyr.py``.

After executing those commands you should see generated ``RegisterDefs.scala`` and ``CSRRegMap.scala``, to use them in the NVMe Core move them to ``/path/to/nvme/core/repo/src/main/scala/NVMeCore/``.

To use generated C header files, move them to ``/path/to/zephyr/firmware/repo/src``.
