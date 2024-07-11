#!/usr/bin/env bash

python src/main.py
cd public && python -m http.server 8888
