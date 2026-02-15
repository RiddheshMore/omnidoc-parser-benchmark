import argparse
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Use custom loading because `pip install python-dotenv` might not be in the marker venv
# But wait, `list_dir` showed `dotenv` in that venv too? (python-dotenv or dotenv?)
# Let's hope it's there. If not, we parse .env manually.

def load_env_manual(env_path):
    if not os.path.exists(env_path):
        return
    with open(env_path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

try:
    from llama_parse import LlamaParse
except ImportError:
    print("Error: llama_parse module not found. Is it installed?")
    # Try importing just to check
    exit(1)

import nest_asyncio
nest_asyncio.apply()

def main():
    parser = argparse.ArgumentParser(description="Run LlamaParse on a directory of PDFs")
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing PDFs")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for MD files")
    parser.add_argument("--env_file", type=str, default="/home/ritz/docling/.env_llama", help="Path to .env file")
    parser.add_argument("--mode", type=str, default="balanced", choices=["fast", "balanced", "agentic", "agentic_plus"], help="Parsing mode")
    args = parser.parse_args()

    # Load API Key
    load_env_manual(args.env_file)
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        print("Error: LLAMA_CLOUD_API_KEY not found in env")
        return

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Configure Parser based on mode
    parse_options = {
        "api_key": api_key,
        "result_type": "markdown",
        "verbose": True,
        "invalidate_cache": True  # Force fresh run for new modes
    }

    if args.mode == "fast":
        print("Using FAST mode (Standard)...")
        # Standard mode, minimal extra processing
        parse_options.update({
            "parse_mode": "parse_page_with_llm", # Use LLM only, no agent
             # disable high_res_ocr for speed if possible, but user wants 'correct' result?
             # Standard "balanced" usually has high_res_ocr=True default? No.
             "high_res_ocr": False, 
             "adaptive_long_table": False,
             "outlined_table_extraction": False
        })
    elif args.mode == "agentic":
        print("Using AGENTIC mode (Gemini-2.5-flash)...")
        parse_options.update({
            "parse_mode": "parse_page_with_agent",
            "model": "gemini-2.5-flash",
            "high_res_ocr": True,
            "adaptive_long_table": True,
            "outlined_table_extraction": True,
            "output_tables_as_HTML": True
        })
    elif args.mode == "agentic_plus":
        print("Using AGENTIC PLUS mode (Anthropic Sonnet 4.0)...")
        # Note: model name might need to be exact as per docs "anthropic-sonnet-4.0"
        parse_options.update({
            "parse_mode": "parse_page_with_agent",
            "model": "anthropic-sonnet-4.0",
            "high_res_ocr": True,
            "adaptive_long_table": True,
            "outlined_table_extraction": True,
            "output_tables_as_HTML": True
        })
    
    # Initialize Parser
    parser = LlamaParse(**parse_options)

    # Iterate over PDF files
    files = list(input_path.glob("*.pdf"))
    if not files:
        print(f"No PDF files found in {input_path}")
        return

    print(f"Processing {len(files)} files...")

    for i, file_path in enumerate(files):
        try:
            start_time = time.time()
            print(f"[{i+1}/{len(files)}] Processing {file_path.name}...")
            
            # LlamaParse execution
            documents = parser.load_data(str(file_path))
            
            if documents:
                md_content = documents[0].text
                
                # Output filename: replace extension with .md
                output_file = output_path / f"{file_path.stem}.md"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(md_content)
                    
                print(f"  Saved to {output_file} ({time.time() - start_time:.2f}s)")
            else:
                 print(f"  Warning: No content returned for {file_path.name}")

        except Exception as e:
            print(f"  Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    main()
