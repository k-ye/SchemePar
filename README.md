# Scheme Subset Compiler

## Overview

- Python based compiler (requires `PLY`) that compiles Scheme source code to assembly code.
- Grammer version: R1 (See `grammar.md` for a full description)
- Target supported: Mac OS X X86-64

## Samples

To to compile a Scheme source code file, run

```bash
python integrated.py samples/r1/r1a_1.rkt
```

This will generate the assembly file, `r1a_1.s`, under `runtime/`. Then you can compile this file with `runtime.c` and run the binary to see the result.

```bash
cd runtime/
gcc -o main r1a_1.s runtime.c
./main
# 42
```

Currently all the sample cases are borrowed from [GitHub - IUCompilerCourse](https://github.com/IUCompilerCourse/support-code-for-students).
