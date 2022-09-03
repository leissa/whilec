#!/usr/bin/env python3

import argparse
from parser import Parser

cli = argparse.ArgumentParser(description='Compiler and interpreter for the while languge.')

cli.add_argument('input', metavar='file', type=str, help='input file')
cli.add_argument('--eval', dest='eval', help='evaluate (interpret) while program')

args = cli.parse_args()

parser = Parser(args.input)
