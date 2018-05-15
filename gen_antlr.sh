#!/usr/bin/env bash
root=$(dirname $0)/query
cd ${root}
antlr4 -visitor -Dlanguage=Python3 Query.g4

