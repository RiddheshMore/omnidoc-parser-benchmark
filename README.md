# OmniDoc Parser Benchmark

This repository contains the evaluation scripts and results for benchmarking **Marker**, **Docling**, and **LlamaParser** on the [OmniDocBench](https://github.com/opendatalab/OmniDocBench) dataset.

## Objective
Identify the most accurate and efficient PDF parser for complex documents (tables, formulas, multi-column layouts), specifically for extracting **soil analysis data**.

## Key Findings
| Parser | Text Accuracy (Edit Dist) | Table Structure (TEDS) | Speed (18 files) |
| :--- | :--- | :--- | :--- |
| **Marker** | **93.5%** | **80.0%** | ~21s/file |
| **Docling** | 88.3% | 69.7% | **~2s/file** |
| **Llama (Fast)** | 36.6% | 30.7% | ~26s/file |

**Recommendation**: Use **Marker** for high-precision extraction of soil data tables.

## Structure
*   `scripts/`: Python adapters for each parser.
*   `configs/`: OmniDocBench configuration files.
*   `run_benchmark.sh`: Main execution script (handles virtual environments).
*   `run_eval.sh`: Scoring script.

## Data Setup
The benchmark requires the **OmniDocBench** dataset.

1.  Clone the official repository (contains the data in `demo_data/`):
    ```bash
    git clone https://github.com/opendatalab/OmniDocBench.git
    ```
2.  **Auto-Conversion**: The benchmark script will automatically convert the demo images to PDFs if they are missing.

## Setup & Installation

### 1. Clone & Prepare
```bash
git clone https://github.com/your-username/omnidoc-parser-benchmark.git
cd omnidoc-parser-benchmark
```

### 2. Install Parsers (Isolated Environments)
To avoid dependency conflicts (PyTorch versions), we recommend using separate virtual environments.

#### **Marker**
```bash
python3 -m venv venv_marker
source venv_marker/bin/activate
pip install marker-pdf
pip install -r requirements_marker.txt # (Optional if you have specific versions)
deactivate
```

#### **Docling**
```bash
python3 -m venv venv_docling
source venv_docling/bin/activate
pip install docling
deactivate
```

#### **LlamaParser**
```bash
python3 -m venv venv_llama
source venv_llama/bin/activate
pip install llama-index-core llama-parse
deactivate
```

#### **Evaluation (Required for Scoring)**
```bash
python3 -m venv venv_eval
source venv_eval/bin/activate
# Install OmniDocBench requirements and plotting tools
pip install -r OmniDocBench/requirements.txt
pip install matplotlib pandas
deactivate
```

### 3. Configure
Create a `.env` file for LlamaParser:
```bash
LLAMA_CLOUD_API_KEY=llx-your-key-here
```

## System Requirements

| Component | Minimum | Recommended (for Marker) |
| :--- | :--- | :--- |
| **OS** | Linux / macOS | Linux (Ubuntu 22.04+) |
| **CPU** | 4 Cores | 8 Cores |
| **RAM** | 8 GB | 16 GB+ |
| **GPU** | Optional (Docling runs on CPU) | **NVIDIA GPU (8GB+ VRAM)** for Marker speedups |
| **Storage** | 10 GB (for Dataset) | 20 GB SSD |

## Run Benchmark
```bash
./run_benchmark_sequential.sh
```

### Running Evaluation
```bash
./run_eval.sh
```
