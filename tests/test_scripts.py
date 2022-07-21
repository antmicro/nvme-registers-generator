import subprocess
import pytest
import os
import tempfile

NVME_SPEC_NAME = "NVM-Express-1_4-2019.06.10-Ratified.pdf"

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nvme_spec_path = os.path.join(root_dir, NVME_SPEC_NAME)
build_dir = os.path.join(root_dir, "test", "build")

# -- helpers


def perform_script_operations(
    script, input_path, output_name, with_sha=False, with_verbose=False
):
    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_name)

        # run script in standard way
        cmd = f"./{script} {input_path} {output_path}"
        subprocess.check_call(cmd, shell=True)

        # fail when the output already exists
        with pytest.raises(Exception):
            cmd = f"./{script} {input_path} {output_path}"
            subprocess.check_call(cmd, shell=True)

        # run script forcing output overwrite
        cmd = f"./{script} -f {input_path} {output_path}"
        subprocess.check_call(cmd, shell=True)

        # run script with non-existing input file
        with pytest.raises(Exception):
            cmd = f"./{script} -v non-existing-file-path {output_path}"
            subprocess.check_call(cmd, shell=True)

    # run script adding information about git sha
    if with_sha:
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, output_name)
            git_sha = "71cabda"
            cmd = f"./{script} --git-sha={git_sha} {input_path} {output_path}"
            subprocess.check_call(cmd, shell=True)

    # run script in verbose mode
    if with_verbose:
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = os.path.join(output_dir, output_name)
            cmd = f"./{script} -v {nvme_spec_path} {output_path}"
            subprocess.check_call(cmd, shell=True)


def generate_register_json(input_path, output_path, force=False):
    args = "-f" if force else ""
    cmd = f"./get_reg_fields.py {args} {input_path} {output_path}"
    subprocess.check_call(cmd, shell=True)


# -- tests


def test_get_reg_fields():
    script = "get_reg_fields.py"
    output_name = "registers.json"

    perform_script_operations(script, nvme_spec_path, output_name, with_verbose=True)


def test_get_reg_fields_chisel():
    script = "get_reg_fields_chisel.py"
    output_name = "RegisterDefs.scala"
    register_json_name = "registers.json"

    with tempfile.TemporaryDirectory() as output_dir:
        register_json_path = os.path.join(output_dir, register_json_name)
        generate_register_json(nvme_spec_path, register_json_path)
        perform_script_operations(
            script, register_json_path, output_name, with_sha=True
        )


def test_get_reg_map_chisel():
    script = "get_reg_map_chisel.py"
    output_name = "CSRRegMap.scala"

    perform_script_operations(
        script, nvme_spec_path, output_name, with_sha=True, with_verbose=True
    )


def test_get_reg_fields_zephyr():
    script = "get_reg_fields_zephyr.py"
    output_name = "nvme_reg_fields.h"
    register_json_name = "registers.json"

    with tempfile.TemporaryDirectory() as output_dir:
        register_json_path = os.path.join(output_dir, register_json_name)
        generate_register_json(nvme_spec_path, register_json_path)
        perform_script_operations(
            script, register_json_path, output_name, with_sha=True
        )


def test_get_identify_struct():
    script = "get_identify_struct.py"
    output_name = "nvme_ident_fields.h"

    perform_script_operations(script, nvme_spec_path, output_name, with_sha=True)


def test_get_reg_map_zephyr():
    script = "get_reg_map_zephyr.py"
    output_name = "nvme_reg_map.h"

    perform_script_operations(
        script, nvme_spec_path, output_name, with_sha=True, with_verbose=True
    )
