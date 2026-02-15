import argparse
import os
from pathlib import Path
from PIL import Image

def main():
    parser = argparse.ArgumentParser(description="Convert images to PDFs")
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing images")
    parser.add_argument("--output_dir", type=str, required=True, help="Output directory for PDFs")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Supported image extensions
    image_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    
    files = [f for f in input_path.iterdir() if f.suffix.lower() in image_exts]
    
    if not files:
        print(f"No image files found in {input_path}")
        return

    print(f"Converting {len(files)} images to PDF...")

    for i, file_path in enumerate(files):
        try:
            print(f"[{i+1}/{len(files)}] Converting {file_path.name}...")
            
            image = Image.open(file_path)
            # Convert to RGB to ensure PDF compatibility (e.g. for PNG with alpha)
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            output_file = output_path / f"{file_path.stem}.pdf"
            image.save(output_file, "PDF", resolution=100.0)
                
            print(f"  Saved to {output_file}")
            
        except Exception as e:
            print(f"  Error converting {file_path.name}: {e}")

if __name__ == "__main__":
    main()
