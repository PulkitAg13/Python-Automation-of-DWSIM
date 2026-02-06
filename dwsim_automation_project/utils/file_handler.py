"""
File handling utilities
"""

import os
import json
import yaml
import pickle
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

def ensure_directory(directory: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Failed to create directory {directory}: {str(e)}")
        return False

def save_results(data: Any, filename: str, format: str = 'json') -> bool:
    """Save data to file in specified format"""
    try:
        ensure_directory(os.path.dirname(filename))
        
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == 'yaml':
            with open(filename, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        elif format == 'csv' and isinstance(data, pd.DataFrame):
            data.to_csv(filename, index=False)
        elif format == 'pkl':
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
        else:
            print(f"❌ Unsupported format: {format}")
            return False
        
        print(f"✅ Saved results to {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save results: {str(e)}")
        return False

def load_config(filename: str, format: str = 'yaml') -> Optional[Dict]:
    """Load configuration from file"""
    try:
        if not os.path.exists(filename):
            print(f"❌ Config file not found: {filename}")
            return None
        
        with open(filename, 'r') as f:
            if format == 'yaml':
                return yaml.safe_load(f)
            elif format == 'json':
                return json.load(f)
            else:
                print(f"❌ Unsupported config format: {format}")
                return None
                
    except Exception as e:
        print(f"❌ Failed to load config: {str(e)}")
        return None

def read_csv(filename: str) -> Optional[pd.DataFrame]:
    """Read CSV file into DataFrame"""
    try:
        if os.path.exists(filename):
            return pd.read_csv(filename)
        else:
            print(f"❌ CSV file not found: {filename}")
            return None
    except Exception as e:
        print(f"❌ Failed to read CSV: {str(e)}")
        return None

def get_file_size(filename: str) -> Optional[int]:
    """Get file size in bytes"""
    try:
        if os.path.exists(filename):
            return os.path.getsize(filename)
        else:
            return None
    except Exception:
        return None

def list_files(directory: str, pattern: str = "*") -> list:
    """List files in directory matching pattern"""
    try:
        path = Path(directory)
        if path.exists():
            return [str(f) for f in path.glob(pattern)]
        else:
            return []
    except Exception:
        return []

def backup_file(filename: str, backup_dir: str = "backups") -> bool:
    """Create backup of file"""
    try:
        if not os.path.exists(filename):
            return False
        
        ensure_directory(backup_dir)
        
        import shutil
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        basename = os.path.basename(filename)
        backup_name = f"{basename}.{timestamp}.bak"
        backup_path = os.path.join(backup_dir, backup_name)
        
        shutil.copy2(filename, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create backup: {str(e)}")
        return False