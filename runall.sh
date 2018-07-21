#!/bin/bash

for P in {130..186}
do
    echo "Problem $P"
	python3.6 algorithm_shortest.py $P
done
