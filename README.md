# While

An interpreter/compiler for a toy language called *While*.
The implementation is in Python

## Usage

```
usage: while.py [-h] [--eval] [-o output] [--output-c output] [--output-py output] file

Compiler and interpreter for the while languge.

positional arguments:
  file                  input file

options:
  -h, --help            show this help message and exit
  --eval                interpret input program
  -o output, --output output
                        print program again
  --output-c output     compile program to C
  --output-py output    compile program to Python

Use '-' to output to stdout.
```

## Examples

### Interpreter

Invoke the interpreter like so:
```sh
./while.py test/fib.while --eval
```

### Compile to C

Compile a *While* program to C, then to an executable, and execute:
```sh
./while.py test/fib.while --output-c fib.c
cc fib.c -o fib
./fib
```

### Compile to Python

Compile a *While* program to Pyhon and then execute:
```sh
./while.py test/fib.while --output-py fib.py
pyhton fib.py
```

### Compile to While

Output the source program again:
```sh
./while.py test/fib.while -o -
```

## Grammar

```enbf
p -> s 'return' e ';'
s -> ';'
   | t ID '=' e;
   |   ID '=' e;
   | 'while' e '{' s '}'
   | s ... s
e -> LIT
   | 'true'
   | 'false'
   | ID
   | '(' e ')'
   | e OP e
```
where
* `LIT` = [`0`-`9`]+
* `ID` = [`a`-`zA`-`Z`][`a`-`zA`-`Z0`-`9`]*
* `OP` is one of: `- * and or == != < <= > >=`
```
