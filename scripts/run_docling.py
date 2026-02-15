import argparse
import os
import time
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
from docling.datamodel.base_models import InputFormat

def main():
    parser = argparse.ArgumentParser(description="Run Docling on a directory of PDFs")
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing PDFs")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for MD files")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Configure GPU
    pipeline_options = PdfPipelineOptions()
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.CUDA
    )
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

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
            
            result = converter.convert(file_path)
            md_content = result.document.export_to_markdown()

            # Output filename: replace extension with .md
            output_file = output_path / f"{file_path.stem}.md"
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            print(f"  Saved to {output_file} ({time.time() - start_time:.2f}s)")
            
        except Exception as e:
            print(f"  Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    main()
