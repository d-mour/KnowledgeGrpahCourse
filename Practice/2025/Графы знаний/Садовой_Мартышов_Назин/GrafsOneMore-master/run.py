import argparse
import importlib
import sys

def main():
    parser = argparse.ArgumentParser(description='Application Runner')
    parser.add_argument('--app', type=str, required=True,
                       help='Application to run (e.g., enemies_processor)')
    
    args, unknown_args = parser.parse_known_args()
    
    try:
        app_module = importlib.import_module(f'{args.app}.main')
        app_module.run(unknown_args)
        
    except ImportError as e:
        print(f"Error: Application '{args.app}' not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application '{args.app}': {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()