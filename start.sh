#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Discord bot..."
python3 florrcalc.py

