#!/bin/bash
# Script to start the AI Sahayak Agents API

# Set PYTHONPATH to include the src directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

echo "🚀 Starting AI Sahayak Agents API..."
python3 src/ai_sahayak/main.py
