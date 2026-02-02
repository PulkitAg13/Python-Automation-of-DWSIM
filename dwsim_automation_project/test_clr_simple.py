#!/usr/bin/env python3
"""
Simple test for CLR in Python 3.10
"""

import sys
print(f"Python: {sys.version}")

# Method 1: Direct import with load
print("\nMethod 1: Direct pythonnet.load()")
try:
    import pythonnet
    pythonnet.load()
    print("✅ pythonnet.load()")
    
    import clr
    print("✅ clr imported")
    
    # Check if AddReference exists
    if hasattr(clr, 'AddReference'):
        print("✅ clr.AddReference exists")
        clr.AddReference("System")
        print("✅ System assembly loaded")
    else:
        print("❌ clr.AddReference missing")
        
except Exception as e:
    print(f"❌ Method 1 failed: {e}")

# Method 2: Alternative import
print("\nMethod 2: Alternative import")
try:
    # Try importing from pythonnet directly
    from pythonnet import load
    load()
    print("✅ pythonnet.load() from module")
    
    from pythonnet import clr
    print("✅ clr from pythonnet")
    
    # Try to use it
    clr.AddReference("System")
    print("✅ System loaded via pythonnet.clr")
    
except Exception as e:
    print(f"❌ Method 2 failed: {e}")

# Method 3: Check installation
print("\nMethod 3: Check installation location")
import site
import os

# Find pythonnet
for path in site.getsitepackages():
    pythonnet_path = os.path.join(path, 'pythonnet')
    if os.path.exists(pythonnet_path):
        print(f"✅ pythonnet found at: {pythonnet_path}")
        # List files
        for file in os.listdir(pythonnet_path):
            if file.endswith('.pyd') or file.endswith('.dll'):
                print(f"  - {file}")
        break
else:
    print("❌ pythonnet not found in site-packages")