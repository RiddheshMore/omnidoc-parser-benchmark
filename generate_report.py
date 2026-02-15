import json
import os
import glob
import pandas as pd
from pathlib import Path

def load_metric(filepath):
    """Load metric result from JSON file."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    result_dir = Path("OmniDocBench/result")
    
    # Identify parsers based on available files
    # pattern: <parser>_quick_match_metric_result.json
    files = list(result_dir.glob("*_quick_match_metric_result.json"))
    
    data = []
    
    for file_path in files:
        # parser name is prefix before _quick_match
        parser_name = file_path.name.replace("_quick_match_metric_result.json", "")
        # skip end2end if it appears (matches pattern but is typically a task name, though here we used it as generic?)
        # Wait, configs used 'docling', 'llama', 'marker' as dataset prediction paths,
        # but the config file structure:
        # end2end_eval:
        #   dataset: 
        #     prediction: ...
        # The script pdf_validation.py uses:
        # save_name = os.path.basename(cfg[task]['dataset']['prediction']['data_path']) + '_' + match_method
        # config paths were: ./result/docling, ./result/llama, ./result/marker
        # so save_names should be: docling_quick_match, llama_quick_match, marker_quick_match.
        
        metrics = load_metric(file_path)
        if not metrics:
            continue
            
        # Extract key metrics
        # Structure of metrics depends on OmniDocBench output
        # Usually: { 'text_block': {'Edit_dist': 0.1, ...}, 'table': {'TEDS': 0.8...}, ... }
        
        row = {'Parser': parser_name}
        
        try:
            # Text Block
            if 'text_block' in metrics and 'all' in metrics['text_block']:
                tb_all = metrics['text_block']['all']
                row['Text Edit Dist (Lower=Better)'] = tb_all.get('Edit_dist', {}).get('ALL_page_avg', 'N/A')
                row['Text BLEU'] = tb_all.get('BLEU', {}).get('all', 'N/A')
                row['Text METEOR'] = tb_all.get('METEOR', {}).get('all', 'N/A')
            
            # Table
            if 'table' in metrics and 'all' in metrics['table']:
                tbl_all = metrics['table']['all']
                row['Table TEDS (Higher=Better)'] = tbl_all.get('TEDS', {}).get('all', 'N/A')
                row['Table TEDS-Struct'] = tbl_all.get('TEDS_structure_only', {}).get('all', 'N/A')
                row['Table Edit Dist'] = tbl_all.get('Edit_dist', {}).get('ALL_page_avg', 'N/A')
                
            # Reading Order
            if 'reading_order' in metrics and 'all' in metrics['reading_order']:
                ro_all = metrics['reading_order']['all']
                row['Reading Order Edit Dist'] = ro_all.get('Edit_dist', {}).get('ALL_page_avg', 'N/A')
                
        except Exception as e:
             print(f"Error parsing metrics for {parser_name}: {e}")
             continue
            
        # Overall Score (formula from README)
        # Overall = ((1 - Text Edit Dist) * 100 + Table TEDS + Formula CDM) / 3
        # We might not have Formula CDM
        
        data.append(row)

    if not data:
        print("No result data found.")
        return

    df = pd.DataFrame(data)
    print("\n" + "="*50)
    print("OMNIDOCBENCH EVALUATION REPORT")
    print("="*50 + "\n")
    print(df.to_markdown(index=False))
    
    # Save to CSV
    df.to_csv("benchmark_report.csv", index=False)
    print("\nSaved to benchmark_report.csv")

if __name__ == "__main__":
    main()
