#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Discord bot..."
python bot.py
