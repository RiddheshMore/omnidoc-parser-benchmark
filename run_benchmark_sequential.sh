#!/bin/bash

# Configuration
# Adapts to local venvs if they exist
# Usage: ./run_benchmark_sequential.sh

echo "Starting Sequential Benchmark Run..."
date

# 0. Cleanup
echo "Clearing previous results..."
rm -rf OmniDocBench/result/docling/*
rm -rf OmniDocBench/result/llama/*
rm -rf OmniDocBench/result/marker/*
mkdir -p OmniDocBench/result/docling
mkdir -p OmniDocBench/result/llama
mkdir -p OmniDocBench/result/marker
echo "---------------------------------------------------"

# 1. Docling
original_dir=$(pwd)
echo "Step 1: Running Docling..."
if [ -d "venv_docling" ]; then
    source venv_docling/bin/activate
    python scripts/run_docling.py
    deactivate
else
    echo "Warning: venv_docling not found in $(pwd). Skipping."
fi
echo "Docling finished. Cooling down..."
sleep 2
echo "---------------------------------------------------"

# 2. LlamaParser (Fast Mode)
echo "Step 2: Running LlamaParser (Fast)..."
if [ -d "venv_llama" ]; then
    source venv_llama/bin/activate
    python scripts/run_llama.py --mode fast
    deactivate
else
    echo "Warning: venv_llama not found in $(pwd). Skipping."
fi
echo "LlamaParser finished. Cooling down..."
sleep 2
echo "---------------------------------------------------"

# 3. Marker
echo "Step 3: Running Marker..."
if [ -d "venv_marker" ]; then
    source venv_marker/bin/activate
    export PYTORCH_ALLOC_CONF=expandable_segments:True
    python scripts/run_marker.py
    deactivate
else
    echo "Warning: venv_marker not found in $(pwd). Skipping."
fi
echo "Marker finished."
echo "---------------------------------------------------"

echo "All Parsers Finished."
date
