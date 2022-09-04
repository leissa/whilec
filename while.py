#!/usr/bin/env python3

import argparse
from parser import Parser

cli = argparse.ArgumentParser(description='Compiler and interpreter for the while languge.')


cli.add_argument('--eval',    dest='eval',    action='store_true', help='interpret input program')
cli.add_argument('--emit-c',  dest='emit_c',  action='store_true', help='compile input program to C')
cli.add_argument('--emit-py', dest='emit_py', action='store_true', help='compile input program to Python')
cli.add_argument('file',                                           help='input file')

args   = cli.parse_args()
parser = Parser(args.file)
stmnt  = parser.parse_prog()
