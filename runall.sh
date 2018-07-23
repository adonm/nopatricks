#!/bin/bash

for P in {1..186}
do
    echo "Problem $P"
	python3.6 algorithm_cube.py $P
done
