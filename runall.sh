#!/bin/bash

for P in {63..186}
do
    echo "Problem $P"
	python3.6 algorithm_shortest.py $P
done
