#!/bin/bash
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Starting Discord bot..."
python3 florrcalc.py


