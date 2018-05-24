#!/bin/bash

clingo --quiet=1 optimisation.asp opt-instance00.asp | \
grep assign | \
sed 's/) /)\n/g' | \
cut -d'(' -f 2- | \
cut -d')' -f1 | \
tr ',' '\t' | \
sort -n
