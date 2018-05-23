#!/bin/bash

for f in instance*.asp
do
	e=$(tail -n1 $f | cut -d' ' -f4-)
	a=$(clingo $f automaton.asp | grep merge)
	if [ "$e" == "$a" ]
	then
		echo "OK   $f"
	else
		echo "FAIL $f : $a : $e"
	fi
done
