#!/bin/bash
set -e

# Define paths
DOCLING_PYTHON="/home/ritz/docling/venv_docling/bin/python"
MARKER_PYTHON="/home/ritz/CinSoil/document-parsing-rag/venv/bin/python"
LLAMA_PYTHON="/home/ritz/CinSoil/document-parsing-rag/venv/bin/python"

INPUT_DIR="OmniDocBench/demo_data/omnidocbench_demo/pdfs"
OUTPUT_BASE="OmniDocBench/result"
LOG_FILE="benchmark_run.log"

echo "Starting Sequential Benchmark Run..." | tee -a $LOG_FILE
date | tee -a $LOG_FILE

# Clear previous results
echo "Clearing previous results..." | tee -a $LOG_FILE
rm -rf $OUTPUT_BASE/docling/*
rm -rf $OUTPUT_BASE/llama/*
rm -rf $OUTPUT_BASE/marker/*

# 1. Run Docling
echo "---------------------------------------------------" | tee -a $LOG_FILE
echo "Step 1: Running Docling..." | tee -a $LOG_FILE
START_TIME=$SECONDS
$DOCLING_PYTHON OmniDocBench/tools_custom/run_docling.py \
   --input_dir $INPUT_DIR \
   --output_dir $OUTPUT_BASE/docling 2>&1 | tee -a $LOG_FILE
ELAPSED=$(($SECONDS - $START_TIME))
echo "Docling finished in ${ELAPSED}s. Cooling down..." | tee -a $LOG_FILE
sleep 2

# 2. Run LlamaParser (Fast Mode)
echo "---------------------------------------------------" | tee -a $LOG_FILE
echo "Step 2: Running LlamaParser (Fast)..." | tee -a $LOG_FILE
START_TIME=$SECONDS
$LLAMA_PYTHON OmniDocBench/tools_custom/run_llama.py \
   --input_dir $INPUT_DIR \
   --output_dir $OUTPUT_BASE/llama \
   --env_file /home/ritz/docling/.env_llama \
   --mode fast 2>&1 | tee -a $LOG_FILE
ELAPSED=$(($SECONDS - $START_TIME))
echo "LlamaParser finished in ${ELAPSED}s. Cooling down..." | tee -a $LOG_FILE
sleep 2

# 3. Run Marker
# Set PyTorch alloc conf to avoid fragmentation as suggested by error
export PYTORCH_ALLOC_CONF=expandable_segments:True

echo "---------------------------------------------------" | tee -a $LOG_FILE
echo "Step 3: Running Marker..." | tee -a $LOG_FILE
START_TIME=$SECONDS
$MARKER_PYTHON OmniDocBench/tools_custom/run_marker.py \
    --input_dir $INPUT_DIR \
    --output_dir $OUTPUT_BASE/marker 2>&1 | tee -a $LOG_FILE
ELAPSED=$(($SECONDS - $START_TIME))
echo "Marker finished in ${ELAPSED}s." | tee -a $LOG_FILE

echo "---------------------------------------------------" | tee -a $LOG_FILE
echo "All Parsers Finished." | tee -a $LOG_FILE
date | tee -a $LOG_FILE
