#!/usr/bin/env python3
"""
Simple test - just try to import DWSIM
"""

import sys
import os

print("Python version:", sys.version)

# Python 3.10 setup
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    import pythonnet
    pythonnet.load()

import clr

# Try the simplest possible import
print("\n1. Loading System assembly...")
try:
    clr.AddReference("System")
    print("✅ System loaded")
    
    import System
    print(f"✅ System imported: {System}")
    
except Exception as e:
    print(f"❌ System failed: {e}")

print("\n2. Adding DWSIM path...")
dwsim_path = r"C:\Program Files\DWSIM"
if os.path.exists(dwsim_path):
    sys.path.append(dwsim_path)
    print(f"✅ DWSIM path added: {dwsim_path}")
else:
    print(f"❌ DWSIM path doesn't exist: {dwsim_path}")
    print("\nPlease check DWSIM installation at: C:\\Program Files\\DWSIM")
    sys.exit(1)

print("\n3. Listing files in DWSIM directory...")
try:
    files = os.listdir(dwsim_path)
    dll_files = [f for f in files if f.endswith('.dll')]
    print(f"Found {len(dll_files)} DLL files:")
    for dll in dll_files[:10]:  # Show first 10
        print(f"  - {dll}")
    
    # Check for specific DWSIM DLLs
    required = ["DWSIM.Interfaces.dll", "DWSIM.Thermodynamics.dll"]
    for req in required:
        if req in files:
            print(f"✅ {req} found")
        else:
            print(f"❌ {req} NOT found")
            
except Exception as e:
    print(f"❌ Error listing files: {e}")

print("\n4. Trying to load DWSIM.Interfaces...")
try:
    clr.AddReference("DWSIM.Interfaces")
    print("✅ DWSIM.Interfaces loaded")
    
    # Try to import
    import DWSIM.Interfaces
    print("✅ DWSIM.Interfaces module imported")
    
    # List contents
    print("\nContents of DWSIM.Interfaces:")
    for attr in dir(DWSIM.Interfaces):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
except Exception as e:
    print(f"❌ DWSIM.Interfaces failed: {e}")
    
    # Try loading from file
    try:
        dll_path = os.path.join(dwsim_path, "DWSIM.Interfaces.dll")
        if os.path.exists(dll_path):
            print(f"\nTrying to load from file: {dll_path}")
            clr.AddReferenceToFileAndPath(dll_path)
            print("✅ Loaded from file")
    except Exception as e2:
        print(f"❌ File load also failed: {e2}")