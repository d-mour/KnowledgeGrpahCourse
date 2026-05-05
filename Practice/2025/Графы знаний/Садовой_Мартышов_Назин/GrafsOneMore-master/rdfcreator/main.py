import argparse
from pathlib import Path
import sys
import traceback
from .core.config import load_config
from .core.csv_processor import process_csv_files
from .core.rdf_builder import build_rdf

def run(args):
    parser = argparse.ArgumentParser(description='RDF Creator')
    parser.add_argument('--config', type=str, 
                       default='conf/rdfconf.yaml',
                       help='Path to configuration file')
    parser.add_argument('--output', type=str,
                       default='output.rdf',
                       help='Output RDF file path')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    parsed_args = parser.parse_args(args)
    
    try:
        
        config_path = Path(parsed_args.config)
        if not config_path.exists():
            print(f"Error: Configuration file {config_path} not found.")
            sys.exit(1)
        
        print(f"Loading config from {config_path}")
        
        
        config = load_config(parsed_args.config)
        if parsed_args.debug:
            print("DEBUG: Configuration loaded:")
            print(config)
        
        
        data = process_csv_files(config, parsed_args.debug)
        if not data or not data['rows']:
            print("Error: No data processed from CSV files.")
            sys.exit(1)
        
        print(f"Processed {len(data['rows'])} rows from {len(data['files_processed'])} files: {', '.join(data['files_processed'])}")
        
        
        build_rdf(data, parsed_args.output, parsed_args.debug)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run(sys.argv[1:])