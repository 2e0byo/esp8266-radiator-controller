#!/bin/bash

cd src/

FILES=$(find . -mindepth 1 -type f -name '*.py' |  awk '{printf "putc " $1 "; "}')
mpfshell -o ser:$1 -n -c $FILES
