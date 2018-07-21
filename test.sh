#!/bin/sh
for test in *_test.py; do
	echo -n "Running $test..."
	python3 "$test"
done
