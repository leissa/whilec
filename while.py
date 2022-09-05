#!/usr/bin/env python3

import argparse
import sys

import err
import while_ast
from parser import Parser

def write(filename):
    if filename == "-":
        return sys.stdout
    return open(filename, "w")

cli = argparse.ArgumentParser(
    description="Compiler and interpreter for the while languge.",
    epilog="Use '-' to output to stdout.")

cli.add_argument(      "--eval",      action="store_true",              dest="eval",      help="interpret input program")
cli.add_argument("-o", "--output",    action="store", metavar="output", dest="output",    help="print program again")
cli.add_argument(      "--output-c",  action="store", metavar="output", dest="output_c",  help="compile program to C")
cli.add_argument(      "--output-py", action="store", metavar="output", dest="output_py", help="compile program to Python")
cli.add_argument("file",                                                                  help="input file")

args = cli.parse_args()

with open(args.file, "r") as file:
    parser = Parser(file)
    prog   = parser.parse_prog()

if args.output != None:
    with write(args.output) as file:
        while_ast.emit = while_ast.Emit.While
        file.write(str(prog))

prog.check()
if err.num_errors != 0:
    sys.exit(f"aborting due to {err.num_errors} error(s)")

if args.eval:
    prog.eval()

if args.output_c != None:
    with write(args.output_c) as file:
        while_ast.emit = while_ast.Emit.C
        file.write(str(prog))

if args.output_py != None:
    with open(args.output_py, "w") as file:
        while_ast.emit = while_ast.Emit.Py
        file.write(str(prog))
