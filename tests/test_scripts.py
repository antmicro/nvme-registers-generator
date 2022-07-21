import subprocess
import pytest
import os
import tempfile

NVME_SPEC_NAME = "NVM-Express-1_4-2019.06.10-Ratified.pdf"

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nvme_spec_path = os.path.join(root_dir, NVME_SPEC_NAME)
build_dir = os.path.join(root_dir, "test", "build")

# -- helpers


def perform_default_script_operations(script, input, output):
    cmd = f"./{script} {input} {output}"
    subprocess.check_call(cmd, shell=True)

    with pytest.raises(Exception):
        cmd = f"./{script} {input} {output}"
        subprocess.check_call(cmd, shell=True)

    cmd = f"./{script} -f {input} {output}"
    subprocess.check_call(cmd, shell=True)

    with pytest.raises(Exception):
        cmd = f"./{script} -v non-existing-file-path {output}"
        subprocess.check_call(cmd, shell=True)


def generate_register_json(input, output, force=False):
    args = "-f" if force else ""
    cmd = f"./get_reg_fields.py {args} {input} {output}"
    subprocess.check_call(cmd, shell=True)


# -- tests


def test_get_reg_fields():
    script = "get_reg_fields.py"
    output_file = "registers.json"

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        perform_default_script_operations(script, nvme_spec_path, output_path)

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        cmd = f"./{script} -v {nvme_spec_path} {output_path}"
        subprocess.check_call(cmd, shell=True)


def test_get_reg_fields_chisel():
    script = "get_reg_fields_chisel.py"
    output_file = "RegisterDefs.scala"
    register_json_file = "registers.json"

    with tempfile.TemporaryDirectory() as output_dir:
        register_json_path = os.path.join(output_dir, register_json_file)
        generate_register_json(nvme_spec_path, register_json_path)

        output_path = os.path.join(output_dir, output_file)
        perform_default_script_operations(script, register_json_path, output_path)

    with tempfile.TemporaryDirectory() as output_dir:
        register_json_path = os.path.join(output_dir, register_json_file)
        generate_register_json(nvme_spec_path, register_json_path)
        output_path = os.path.join(output_dir, output_file)

        git_sha = "71cabda"
        cmd = f"./{script} --git-sha={git_sha} {register_json_path} {output_path}"
        subprocess.check_call(cmd, shell=True)


def test_get_reg_map_chisel():
    script = "get_reg_map_chisel.py"
    output_file = "CSRRegMap.scala"

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        perform_default_script_operations(script, nvme_spec_path, output_path)

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        cmd = f"./{script} -v {nvme_spec_path} {output_path}"
        subprocess.check_call(cmd, shell=True)

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        git_sha = "71cabda"
        cmd = f"./{script} --git-sha={git_sha} {nvme_spec_path} {output_path}"
        subprocess.check_call(cmd, shell=True)


def test_get_reg_fields_zephyr():
    script = "get_reg_fields_zephyr.py"
    output_file = "nvme_reg_fields.h"
    register_json_file = "registers.json"

    with tempfile.TemporaryDirectory() as output_dir:
        register_json_path = os.path.join(output_dir, register_json_file)
        generate_register_json(nvme_spec_path, register_json_path)

        output_path = os.path.join(output_dir, output_file)
        perform_default_script_operations(script, register_json_path, output_path)

    with tempfile.TemporaryDirectory() as output_dir:
        register_json_path = os.path.join(output_dir, register_json_file)
        generate_register_json(nvme_spec_path, register_json_path)
        output_path = os.path.join(output_dir, output_file)

        git_sha = "71cabda"
        cmd = f"./{script} --git-sha={git_sha} {register_json_path} {output_path}"
        subprocess.check_call(cmd, shell=True)


def test_get_identify_struct():
    script = "get_identify_struct.py"
    output_file = "nvme_ident_fields.h"

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        perform_default_script_operations(script, nvme_spec_path, output_path)

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)

        git_sha = "71cabda"
        cmd = f"./{script} --git-sha={git_sha} {nvme_spec_path} {output_path}"
        subprocess.check_call(cmd, shell=True)


def test_get_reg_map_zephyr():
    script = "get_reg_map_zephyr.py"
    output_file = "nvme_reg_map.h"

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        perform_default_script_operations(script, nvme_spec_path, output_path)

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)
        cmd = f"./{script} -v {nvme_spec_path} {output_path}"
        subprocess.check_call(cmd, shell=True)

    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, output_file)

        git_sha = "71cabda"
        cmd = f"./{script} --git-sha={git_sha} {nvme_spec_path} {output_path}"
        subprocess.check_call(cmd, shell=True)
