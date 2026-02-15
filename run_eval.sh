#!/bin/bash
set -e

# Path to eval venv (relative or absolute check?)
# If venv_eval exists in cwd, use it.
if [ -d "venv_eval" ]; then
    EVAL_PYTHON="venv_eval/bin/python"
else
    # Fallback to absolute if user didn't install locally (e.g. dev environment)
    # But for repo user, they should have venv_eval.
    # We'll use a safer check.
    echo "Warning: venv_eval not found in $(pwd). Trying global python3..."
    EVAL_PYTHON="python3"
fi

# Store root dir
ROOT_DIR=$(pwd)

# OmniDocBench validation
if [ -d "OmniDocBench" ]; then
    cd OmniDocBench
    
    echo "Starting Evaluation..."
    date
    
    echo "---------------------------------------------------"
    echo "Evaluating Docling..."
    # configs are in ../configs usually?
    # No, we copied configs to OmniDocBench/configs or we symlinked?
    # The README says "Ensure [OmniDocBench] is located inside...".
    # And we need custom configs.
    # We should pass absolute path to configs if they are in repo root.
    CONFIG_DIR="$ROOT_DIR/configs"

    if [ -f "$CONFIG_DIR/custom_docling.yaml" ]; then
        $EVAL_PYTHON pdf_validation.py --config "$CONFIG_DIR/custom_docling.yaml"
        echo "Docling Evaluation Done."
    else
        echo "Config not found: $CONFIG_DIR/custom_docling.yaml"
    fi
    
    echo "---------------------------------------------------"
    echo "Evaluating LlamaParser..."
    if [ -f "$CONFIG_DIR/custom_llama.yaml" ]; then
        $EVAL_PYTHON pdf_validation.py --config "$CONFIG_DIR/custom_llama.yaml"
        echo "LlamaParser Evaluation Done."
    fi
    
    echo "---------------------------------------------------"
    echo "Evaluating Marker..."
    # Only evaluate if output exists
    # Marker output is in OmniDocBench/result/marker
    if [ -d "result/marker" ] && [ -f "$CONFIG_DIR/custom_marker.yaml" ]; then
        $EVAL_PYTHON pdf_validation.py --config "$CONFIG_DIR/custom_marker.yaml"
        echo "Marker Evaluation Done."
    else
        echo "Marker output or config not found, skipping..."
    fi
    
    # Return to root for reporting
    cd "$ROOT_DIR"
else
    echo "Error: OmniDocBench folder not found."
    exit 1
fi

echo "---------------------------------------------------"
echo "Generating Report..."
# generate_report.py expects to run from ROOT_DIR
$EVAL_PYTHON generate_report.py

if [ -f "benchmark_chart.png" ]; then
    echo "Chart generated: benchmark_chart.png"
fi

echo "All Evaluations Finished."
date
