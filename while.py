#!/usr/bin/env python3
"""
Main driver for compiler/interpreter.
"""

import argparse
import sys

import err
import while_ast
from parse import Parser

cli = argparse.ArgumentParser(
    description="Compiler and interpreter for the While languge.",
    epilog="Use '-' to output to stdout.")

cli.add_argument(      "--eval",      action="store_true",              dest="eval",      help="interpret input program")
cli.add_argument("-o", "--output",    action="store", metavar="output", dest="output",    help="print program again")
cli.add_argument(      "--output-c",  action="store", metavar="output", dest="output_c",  help="compile program to C")
cli.add_argument(      "--output-py", action="store", metavar="output", dest="output_py", help="compile program to Python")
cli.add_argument("file",                                                                  help="input file")

args = cli.parse_args()

with open(args.file, "r", encoding='ASCII') as in_file:
    parser = Parser(in_file)
    prog   = parser.parse_prog()

def output(filename, emit):
    if filename is not None:
        while_ast.EMIT = emit
        if filename == "-":
            sys.stdout.write(str(prog))
        else:
            with open(filename, "w", encoding='ASCII') as out_file:
                out_file.write(str(prog))

output(args.output, while_ast.Emit.WHILE)

prog.check()
if err.NUM_ERRORS != 0:
    sys.exit(f"error: aborting due to {err.NUM_ERRORS} error(s)")

if args.eval:
    while_ast.EMIT = while_ast.Emit.EVAL
    prog.eval()

output(args.output_c,  while_ast.Emit.C)
output(args.output_py, while_ast.Emit.PY)
