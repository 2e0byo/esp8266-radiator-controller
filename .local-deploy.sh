#!/bin/bash

cd src/

FILES=$(find . -mindepth 1 -name '*.py' |  awk '{printf "putc " $1 "; "}')
mpfshell -o ser:$1 -n -c $FILES
