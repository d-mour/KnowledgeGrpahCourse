import argparse
import yaml
import os
import glob
from .core import Parser

def load_all_configs(config_path):
    """Загружает все YAML-конфиги из указанной папки и объединяет их"""
    all_configs = []
    
    
    if os.path.isfile(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = yaml.safe_load(f)
            
            if configs is None:
                configs = []
            elif not isinstance(configs, list):
                configs = [configs]
            all_configs.extend(configs)
        return all_configs
    
    
    if os.path.isdir(config_path):
        yaml_files = glob.glob(os.path.join(config_path, "*.yaml")) + \
                    glob.glob(os.path.join(config_path, "*.yml"))
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    configs = yaml.safe_load(f)
                    
                    if configs is None:
                        configs = []
                    elif not isinstance(configs, list):
                        configs = [configs]
                    all_configs.extend(configs)
                print(f"Loaded config from: {yaml_file}")
            except Exception as e:
                print(f"Error loading config from {yaml_file}: {e}")
        
        return all_configs
    
    raise ValueError(f"Config path not found: {config_path}")

def run(args_list=None):
    
    if args_list is None:
        args_list = sys.argv[1:]
    
    parser = argparse.ArgumentParser(description='Web Parser')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to YAML config file or directory')
    
    args = parser.parse_args(args_list)

    
    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join('conf', config_path)

    
    all_configs = load_all_configs(config_path)
    
    
    parser = Parser(all_configs)
    parser.run()


if __name__ == '__main__':
    run()