#!/bin/bash
set -e

# Path to eval venv
EVAL_PYTHON="/home/ritz/docling/venv_eval/bin/python"

# OmniDocBench root
cd /home/ritz/docling/OmniDocBench

echo "Starting Evaluation..."
date

echo "---------------------------------------------------"
echo "Evaluating Docling..."
$EVAL_PYTHON pdf_validation.py --config configs/custom_docling.yaml
echo "Docling Evaluation Done."

echo "---------------------------------------------------"
echo "Evaluating LlamaParser..."
$EVAL_PYTHON pdf_validation.py --config configs/custom_llama.yaml
echo "LlamaParser Evaluation Done."

echo "---------------------------------------------------"
echo "Evaluating Marker..."
# Only evaluate if output exists
if [ -d "result/marker" ]; then
    $EVAL_PYTHON pdf_validation.py --config configs/custom_marker.yaml
    echo "Marker Evaluation Done."
else
    echo "Marker output directory not found, skipping..."
fi

echo "---------------------------------------------------"
echo "---------------------------------------------------"
echo "Generating Report..."
$EVAL_PYTHON generate_report.py
if [ -f "benchmark_chart.png" ]; then
    echo "Chart generated: benchmark_chart.png"
fi

echo "All Evaluations Finished."
date
