#!/bin/bash

# Configuration
INPUT_IMAGES="OmniDocBench/demo_data/omnidocbench_demo/images"
INPUT_PDFS="OmniDocBench/demo_data/omnidocbench_demo/pdfs"
OUTPUT_BASE="OmniDocBench/result"

echo "Starting Sequential Benchmark Run..."
date

# 0. Preparation: Generate PDFs if missing
if [ ! -d "$INPUT_PDFS" ] || [ -z "$(ls -A $INPUT_PDFS)" ]; then
    echo "PDFs not found in $INPUT_PDFS. Generating from images..."
    mkdir -p $INPUT_PDFS
    # Use system python or any venv with Pillow/img2pdf. 
    # venv_docling usually has these dependencies or we can use venv_marker.
    # We'll try venv_docling as it's lightweight.
    
    if [ -d "venv_docling" ]; then
        source venv_docling/bin/activate
        # Ensure dependencies for conversion exist (Pillow)
        pip install Pillow reportlab > /dev/null 2>&1 
        python scripts/images_to_pdfs.py --input_dir "$INPUT_IMAGES" --output_dir "$INPUT_PDFS"
        deactivate
    else
        echo "Error: venv_docling needed to convert images to PDFs."
        exit 1
    fi
fi

# 0.1 Cleanup Results
echo "Clearing previous results..."
rm -rf $OUTPUT_BASE/docling/*
rm -rf $OUTPUT_BASE/llama/*
rm -rf $OUTPUT_BASE/marker/*
mkdir -p $OUTPUT_BASE/docling
mkdir -p $OUTPUT_BASE/llama
mkdir -p $OUTPUT_BASE/marker
echo "---------------------------------------------------"

# 1. Docling
echo "Step 1: Running Docling..."
if [ -d "venv_docling" ]; then
    source venv_docling/bin/activate
    python scripts/run_docling.py --input_dir "$INPUT_PDFS" --output_dir "$OUTPUT_BASE/docling"
    deactivate
else
    echo "Warning: venv_docling not found. Skipping."
fi
echo "Docling finished. Cooling down..."
sleep 2
echo "---------------------------------------------------"

# 2. LlamaParser (Fast Mode)
echo "Step 2: Running LlamaParser (Fast)..."
if [ -d "venv_llama" ]; then
    source venv_llama/bin/activate
    ENV_ARG=""
    if [ -f ".env" ]; then
        ENV_ARG="--env_file .env"
    fi
    python scripts/run_llama.py --input_dir "$INPUT_PDFS" --output_dir "$OUTPUT_BASE/llama" --mode fast $ENV_ARG
    deactivate
else
    echo "Warning: venv_llama not found. Skipping."
fi
echo "LlamaParser finished. Cooling down..."
sleep 2
echo "---------------------------------------------------"

# 3. Marker
echo "Step 3: Running Marker..."
if [ -d "venv_marker" ]; then
    source venv_marker/bin/activate
    export PYTORCH_ALLOC_CONF=expandable_segments:True
    python scripts/run_marker.py --input_dir "$INPUT_PDFS" --output_dir "$OUTPUT_BASE/marker"
    deactivate
else
    echo "Warning: venv_marker not found. Skipping."
fi
echo "Marker finished."
echo "---------------------------------------------------"

echo "All Parsers Finished."
date
