"""
Validation utilities
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml

def validate_environment() -> bool:
    """Validate the execution environment"""
    print("Validating environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Check DWSIM path
    dwsim_path = os.getenv('DWSIM_PATH', 'C:/Program Files/DWSIM')
    if not os.path.exists(dwsim_path):
        print(f"⚠️ DWSIM path not found: {dwsim_path}")
        print("   Please set DWSIM_PATH environment variable")
        # Continue anyway, might be in different location
    
    # Check required directories
    required_dirs = ['config', 'logs', 'results']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"⚠️ Directory not found: {dir_name}")
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ Created directory: {dir_name}")
            except:
                print(f"❌ Failed to create directory: {dir_name}")
                return False
    
    # Check required config files
    required_configs = [
        'config/pfr_config.yaml',
        'config/distillation_config.yaml',
        'config/sweep_config.yaml'
    ]
    
    for config_file in required_configs:
        if not os.path.exists(config_file):
            print(f"❌ Config file not found: {config_file}")
            return False
        else:
            print(f"✅ Config file found: {config_file}")
    
    # Validate config files
    for config_file in required_configs:
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            if config_file.endswith('pfr_config.yaml'):
                if 'reactor' not in config:
                    print(f"❌ Invalid PFR config: missing 'reactor' section")
                    return False
            elif config_file.endswith('distillation_config.yaml'):
                if 'column' not in config:
                    print(f"❌ Invalid distillation config: missing 'column' section")
                    return False
            
        except Exception as e:
            print(f"❌ Failed to parse config file {config_file}: {str(e)}")
            return False
    
    print("✅ Environment validation passed")
    return True

def validate_config(config: Dict, config_type: str) -> Tuple[bool, List[str]]:
    """Validate configuration dictionary"""
    errors = []
    
    if config_type == 'pfr':
        required_sections = ['reactor', 'feed']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing section: {section}")
        
        if 'reactor' in config:
            reactor = config['reactor']
            required_params = ['volume', 'temperature']
            for param in required_params:
                if param not in reactor:
                    errors.append(f"Missing reactor parameter: {param}")
                else:
                    # Validate ranges
                    if param == 'volume' and reactor[param] <= 0:
                        errors.append(f"Reactor volume must be positive")
                    elif param == 'temperature' and reactor[param] <= 0:
                        errors.append(f"Temperature must be positive")
    
    elif config_type == 'distillation':
        required_sections = ['column', 'feed']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing section: {section}")
        
        if 'column' in config:
            column = config['column']
            required_params = ['stages', 'reflux_ratio']
            for param in required_params:
                if param not in column:
                    errors.append(f"Missing column parameter: {param}")
                else:
                    # Validate ranges
                    if param == 'stages' and column[param] < 2:
                        errors.append(f"Number of stages must be at least 2")
                    elif param == 'reflux_ratio' and column[param] < 0:
                        errors.append(f"Reflux ratio cannot be negative")
    
    elif config_type == 'sweep':
        if 'pfr' in config:
            pfr_sweep = config['pfr']
            if 'ranges' in pfr_sweep:
                ranges = pfr_sweep['ranges']
                for param, range_config in ranges.items():
                    if 'min' not in range_config or 'max' not in range_config:
                        errors.append(f"PFR sweep range for {param} missing min/max")
                    elif range_config['min'] >= range_config['max']:
                        errors.append(f"PFR sweep {param}: min must be less than max")
        
        if 'distillation' in config:
            dist_sweep = config['distillation']
            if 'ranges' in dist_sweep:
                ranges = dist_sweep['ranges']
                for param, range_config in ranges.items():
                    if 'min' not in range_config or 'max' not in range_config:
                        errors.append(f"Distillation sweep range for {param} missing min/max")
                    elif range_config['min'] >= range_config['max']:
                        errors.append(f"Distillation sweep {param}: min must be less than max")
    
    return len(errors) == 0, errors

def validate_simulation_result(result: Dict, simulation_type: str) -> Tuple[bool, List[str]]:
    """Validate simulation result"""
    errors = []
    
    if not result.get('success', False):
        errors.append("Simulation was not successful")
        return False, errors
    
    if simulation_type == 'pfr':
        required_fields = ['conversion_percent', 'b_production_rate', 'outlet_temperature']
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing field: {field}")
            else:
                value = result[field]
                if field == 'conversion_percent' and (value < 0 or value > 100):
                    errors.append(f"Conversion percentage out of range: {value}")
                elif field == 'b_production_rate' and value < 0:
                    errors.append(f"Negative B production rate: {value}")
    
    elif simulation_type == 'distillation':
        required_fields = ['distillate_purity_A', 'bottoms_purity_B', 'condenser_duty']
        for field in required_fields:
            if field not in result:
                errors.append(f"Missing field: {field}")
            else:
                value = result[field]
                if 'purity' in field and (value < 0 or value > 100):
                    errors.append(f"Purity out of range: {value}")
        
        if not result.get('converged', False):
            errors.append("Distillation column did not converge")
    
    return len(errors) == 0, errors

def check_dependencies() -> Dict[str, bool]:
    """Check Python dependencies"""
    dependencies = {
        'pythonnet': False,
        'numpy': False,
        'pandas': False,
        'matplotlib': False,
        'pyyaml': False,
    }
    
    for dep in dependencies.keys():
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies