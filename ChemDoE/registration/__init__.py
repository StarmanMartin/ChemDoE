import importlib.util
import os
import runpy
import shutil
import tempfile
import uuid
from functools import wraps
from pathlib import Path
from subprocess import Popen, PIPE
from typing import LiteralString, Literal

from ChemDoE.config import ConfigManager
from ChemDoE.registration.result_validater import validate_results
from ChemDoE.registration.loader import read_results
from _pytest.monkeypatch import MonkeyPatch
import sys

def _get_absolute_path(module_name):
    spec = importlib.util.find_spec(module_name)
    if spec and spec.origin:
        return os.path.abspath(spec.origin)
    return None


def _generate_test_args(tmp_path: Path, input_type: Literal['json', 'csv'],
                        output_type: Literal['json', 'csv']):
    # Create temporary input and output files
    input_file_name = f"{input_type}_sample.{input_type}"
    output_file_name = f"out_{output_type}_sample.{output_type}"
    input_file = tmp_path / input_file_name
    output_file = tmp_path / output_file_name

    src = Path(__file__).parent.parent / 'examples'

    shutil.copyfile(src / input_file_name, input_file)


    # Simulate command-line arguments
    return  [sys.argv[0], str(input_file), str(output_file)]


def check_doe_script(input_type: Literal['json', 'csv'], output_type: Literal['json', 'csv']):
    """Pytest decorator to test if the decorated function works according to the requirements of a DoE run script."""

    def decorator(test_func):
        @wraps(test_func)
        def wrapper(*test_args, **test_kwargs):
            with tempfile.TemporaryDirectory() as tmpdir:
                mp = MonkeyPatch()
                new_args = _generate_test_args(Path(tmpdir), input_type, output_type)
                # Simulate command-line arguments
                mp.setattr(sys, "argv", new_args)
                try:
                    test_func(*test_args, **test_kwargs)
                    _load_and_test_results(sys.argv[-1])# Run the test
                finally:
                    mp.undo()  # Restore original sys.argv after the test

        return wrapper

    return decorator


def _load_and_test_results(result_path: str | Path | LiteralString):
    try:
        res = read_results(result_path)
    except FileNotFoundError:
        raise ValueError('Script did not write an output file')
    assert validate_results(res) == []



def _from_abs_path_run_python_doe_script(script_path):
    cmd = [sys.executable, script_path, sys.argv[1], sys.argv[2]]
    p = Popen(cmd, stdout=PIPE,
              stderr=PIPE,
              text=True,  # Ensures output is in string format instead of bytes
              bufsize=1,  # Line-buffered output
              universal_newlines=True,  # Handles newlines properly across platforms
              cwd=os.path.dirname(script_path)
              )
    for line in iter(p.stdout.readline, ''):
        print(line, end="")
        
def _from_import_path_run_python_doe_script(script_path):
    runpy.run_module(script_path, run_name="__main__")
    
def register_python_doe_script(script_path, input_type: Literal['json', 'csv'],  output_type: Literal['json', 'csv']):
    """
    Executes a Python script with test DoE Table and adds it to the run scripts of ChemDoE if the results are in the correct format

    :param script_path: Ether the file path of the Python script or the import path
    :param input_type: File format of the input file
    :param output_type: File format of the output file
    :return:
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        sys.argv = _generate_test_args(Path(tmpdir), input_type, output_type)

        if os.path.exists(script_path):
            _from_abs_path_run_python_doe_script(script_path)
            abs_path = os.path.abspath(script_path)
        else:
            abs_path = _get_absolute_path(script_path)
            _from_import_path_run_python_doe_script(script_path)

        _load_and_test_results(sys.argv[-1])
        scripts = ConfigManager().load_scripts()
        values = next((x for x in scripts if x["file"] == abs_path), None)

        if values is None:
            values = {'id': uuid.uuid4().__str__()}
            scripts.append(values)

        values["name"] = abs_path
        values["file_type"] = "Python"
        values["input"] = input_type.upper()
        values["output"] = output_type.upper()
        values["file"] = abs_path
        values["interpreter"] = sys.executable

        ConfigManager().save_scripts(scripts)


def register_r_doe_script(script_path, input_type: Literal['json', 'csv'], output_type: Literal['json', 'csv']):
    """
    Executes an R script with test DoE Table and adds it to the run scripts of ChemDoE if the results are in the correct format

    :param script_path: File path of the R script
    :param input_type: File format of the input file
    :param output_type: File format of the output file
    :return:
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        sys_argv = _generate_test_args(Path(tmpdir), input_type, output_type)
        r = ConfigManager().r_interpreters[0]
        cmd = [r, script_path, sys_argv[1], sys_argv[2]]
        p = Popen(cmd, stdout=PIPE,
                  stderr=PIPE,
                  text=True,  # Ensures output is in string format instead of bytes
                  bufsize=1,  # Line-buffered output
                  universal_newlines=True,  # Handles newlines properly across platforms
                  cwd=os.path.dirname(script_path)
                  )
        for line in iter(p.stdout.readline, ''):
            print(line)
        _load_and_test_results(sys_argv[2])
        scripts = ConfigManager().load_scripts()

        abs_path = os.path.abspath(script_path)
        values = next((x for x in scripts if x["file"] == abs_path), None)

        if values is None:
            values = {'id': uuid.uuid4().__str__()}
            scripts.append(values)

        values["name"] = script_path
        values["file_type"] = "R"
        values["input"] = input_type.upper()
        values["output"] = output_type.upper()
        values["file"] = abs_path
        values["interpreter"] = sys.executable

        ConfigManager().save_scripts(scripts)
