#!/bin/bash

AGENTS=(perfect)

echo -ne 'instance\toptimum\t'

for agent in ${AGENTS[*]}
do
	echo -ne "$agent\t"
done

echo -ne '\n'

for f in suite/$1
do
	b=$(basename $f .txt)
	# Extract optimum
	o=$(grep optimum $f | cut -c9-)
	echo -ne "$b\t$o\t"
	for agent in ${AGENTS[*]}
	do
		result=$(python3 ./game.py -agent $agent -world $f -porcelain)
		echo -ne "$result\t"
	done
	echo
done
