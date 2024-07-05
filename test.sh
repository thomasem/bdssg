#!/usr/bin/env bash

python -m coverage run -m unittest discover -s src
python -m coverage report
