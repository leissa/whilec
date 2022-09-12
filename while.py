#!/usr/bin/env python3

import argparse
import sys

import err
import while_ast
from parser import Parser

cli = argparse.ArgumentParser(
    description="Compiler and interpreter for the While languge.",
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

def output(filename, emit):
    if filename != None:
        file = sys.stdout if filename == "-" else open(filename, "w")
        while_ast.emit = emit
        file.write(str(prog))
        if filename != "-":
            file.close()

output(args.output, while_ast.Emit.While)

prog.check()
if err.num_errors != 0:
    sys.exit(f"aborting due to {err.num_errors} error(s)")

if args.eval:
    prog.eval()

output(args.output_c,  while_ast.Emit.C)
output(args.output_py, while_ast.Emit.Py)
