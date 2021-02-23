#!/bin/bash
kill $(ps aux | grep 'joblib' | awk '{print $2}')
kill $(ps aux | grep 'pytest' | awk '{print $2}')
kill $(ps aux | grep 'python' | awk '{print $2}')
python3 main.py
