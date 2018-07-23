#!/bin/bash

for P in {19..186}
do
    echo "Problem $P"
	python3.6 algorithm_cube.py $P
done

for P in {19..186}
do
    echo "Problem $P"
	python3.6 unprinter.py $P
done

for P in $(seq -f "%03g" 2 115)
do
    echo "Problem $P"
	python3.6 launcher.py --source problemsF/FR$P"_src.mdl" --target problemsF/FR$P"_tgt.mdl" submission/FR$P".nbt"
done
