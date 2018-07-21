#!/bin/bash

for P in {2..186}
do
    echo "Problem $P"
	python3.6 algorithm.py $P
done
