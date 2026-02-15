import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run Marker on a directory of PDFs")
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing PDFs")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for MD files")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Locate marker_single in the current python environment's bin dir
    python_bin = Path(sys.executable).parent
    marker_cmd = python_bin / "marker_single"
    
    if not marker_cmd.exists():
        # Try searching in PATH just in case
        marker_cmd = shutil.which("marker_single")
        if marker_cmd:
            marker_cmd = Path(marker_cmd)
        else:
            print(f"Error: marker_single not found in {python_bin} or PATH")
            return

    # Iterate over PDF files
    files = list(input_path.glob("*.pdf"))
    if not files:
        print(f"No PDF files found in {input_path}")
        return

    print(f"Processing {len(files)} files using {marker_cmd}...")

    for i, file_path in enumerate(files):
        try:
            print(f"[{i+1}/{len(files)}] Processing {file_path.name}...")
            
            # Correct usage based on user example: marker_single input_path --output_dir output_path
            cmd = [
                str(marker_cmd),
                str(file_path),
                "--output_dir", str(output_path)
            ]
            
            # Run marker
            # Set PYTORCH_ALLOC_CONF to reduce fragmentation
            env = os.environ.copy()
            env["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
            
            result = subprocess.run(cmd, check=True, capture_output=True, env=env)

            # Expected output location: output_dir / file_stem / file_stem.md
            # marker_single creates a subdirectory for the file.
            marker_output_folder = output_path / file_path.stem
            marker_md_file = marker_output_folder / f"{file_path.stem}.md"
            
            final_md_file = output_path / f"{file_path.stem}.md"
            
            if marker_md_file.exists():
                shutil.move(str(marker_md_file), str(final_md_file))
                # Cleanup the folder (it might contain other assets like images, but OmniDocBench only needs MD?)
                # OmniDocBench might need images if referenced? 
                # For now let's just move MD. If images are needed, we might need to keep folder structure or move images too.
                # Assuming just MD text for now as per `test_markitdown.py` printing content.
                shutil.rmtree(marker_output_folder)
                print(f"  Saved to {final_md_file}")
            else:
                 print(f"  Warning: Expected output not found at {marker_md_file}")
                 print(f"  STDOUT: {result.stdout.decode()}")
                 print(f"  STDERR: {result.stderr.decode()}")

        except subprocess.CalledProcessError as e:
            print(f"  Error running marker on {file_path.name}: {e.stderr.decode()}")
            if 'temp_pdf_path' in locals() and temp_pdf_path.exists(): temp_pdf_path.unlink()
        except Exception as e:
            print(f"  Error processing {file_path.name}: {e}")
            if 'temp_pdf_path' in locals() and temp_pdf_path.exists(): temp_pdf_path.unlink()

if __name__ == "__main__":
    main()
