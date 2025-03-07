from typing import Literal

import click
from ChemDoE.main import run as run_ui
from ChemDoE.registration import register_r_doe_script, register_python_doe_script

FileFormat = ['csv', 'json']


@click.group()
def cli():
    pass


@cli.command(help="Runs the CheDoE UI")
def run():
    run_ui()


@cli.command(
    help="Executes a R script with test DoE Table and adds it to the run scripts of ChemDoE if the results are in the correct format")
@click.option('--r-script-path', '-src', prompt='Path to the R script', help='Path to the R script')
@click.option('--output-format', '-o', type=click.Choice(FileFormat), prompt='Output file format',
              default=FileFormat[0], help='Output file format must be csv or json')
@click.option('--input-format', '-i', type=click.Choice(FileFormat), prompt='Input file format', default=FileFormat[0],
              help='Input file format must be csv or json')
def add_r_script(r_script_path: str, input_format: Literal['csv', 'json'] , output_format: Literal['csv', 'json']):
    register_r_doe_script(r_script_path, input_format, output_format)


@cli.command(
    help="Executes a Python script with test DoE Table and adds it to the run scripts of ChemDoE if the results are in the correct format")
@click.option('--python-script-path', '-src', prompt='Path to the Python script', help='Path to the Python script')
@click.option('--output-format', '-o', type=click.Choice(FileFormat), prompt='Output file format',
              default=FileFormat[0], help='Output file format must be csv or json')
@click.option('--input-format', '-i', type=click.Choice(FileFormat), prompt='Input file format', default=FileFormat[0],
              help='Input file format must be csv or json')
def add_python_script(python_script_path: str, input_format: Literal['csv', 'json'] , output_format: Literal['csv', 'json']):
    register_python_doe_script(python_script_path, input_format, output_format)


if __name__ == '__main__':
    cli()
