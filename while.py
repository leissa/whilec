#!/usr/bin/env python3

import argparse
import sys

import err
from parser import Parser

cli = argparse.ArgumentParser(description="Compiler and interpreter for the while languge.")

cli.add_argument("--eval",    dest="eval",    action="store_true", help="interpret input program")
cli.add_argument("--print",   dest="print",   action="store_true", help="print program again")
cli.add_argument("file",                                           help="input file")

args   = cli.parse_args()
parser = Parser(args.file)
prog   = parser.parse_prog()

if args.print: print(prog)

prog.check()
if err.num_errors != 0: sys.exit(f"aborting due to {err.num_errors} error(s)")

if args.eval: prog.eval()
