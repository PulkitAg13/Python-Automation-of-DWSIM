#!/usr/bin/env python3
"""
Load DWSIM assemblies using reflection
"""

import sys
import os

print("="*60)
print("Loading DWSIM with Reflection")
print("="*60)

# Python 3.10 setup
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    import pythonnet
    pythonnet.load()

import clr

dwsim_path = r"C:\Program Files\DWSIM"
sys.path.append(dwsim_path)

# Load System.Reflection
clr.AddReference("System.Reflection")

import System
import System.Reflection

print("\n1. Loading DWSIM assemblies using Reflection:")

# Try to load DWSIM.Interfaces.dll
interfaces_dll = os.path.join(dwsim_path, "DWSIM.Interfaces.dll")
if os.path.exists(interfaces_dll):
    print(f"Loading: {interfaces_dll}")
    try:
        # Load assembly from file
        assembly = System.Reflection.Assembly.LoadFrom(interfaces_dll)
        print(f"✅ Assembly loaded: {assembly.FullName}")
        
        # Get types
        types = assembly.GetTypes()
        print(f"✅ Found {len(types)} types in assembly")
        
        # List first 10 types
        print("\nFirst 10 types:")
        for i, t in enumerate(types[:10]):
            print(f"  {i+1}. {t.FullName}")
        
    except Exception as e:
        print(f"❌ Failed to load: {e}")
else:
    print(f"❌ File not found: {interfaces_dll}")

print("\n" + "="*60)
print("2. Alternative: Use clr.AddReference with full path")
print("="*60)

# Try loading all DWSIM DLLs
dwsim_dlls = [
    "DWSIM.SharedClasses.dll",
    "DWSIM.GlobalSettings.dll", 
    "DWSIM.Thermodynamics.dll",
    "DWSIM.Interfaces.dll",
    "DWSIM.UnitOperations.dll"
]

for dll in dwsim_dlls:
    dll_path = os.path.join(dwsim_path, dll)
    if os.path.exists(dll_path):
        print(f"\nTrying {dll}:")
        try:
            # Try clr.AddReference with full type name
            clr.AddReferenceToFileAndPath(dll_path)
            print(f"✅ Loaded successfully")
        except Exception as e:
            print(f"❌ Failed: {e}")
    else:
        print(f"\n❌ {dll} not found")

print("\n" + "="*60)
print("3. Check if we can access DWSIM namespace")
print("="*60)

# Try to import DWSIM namespace
try:
    import DWSIM
    print("✅ DWSIM namespace imported")
    
    # List submodules
    print("\nSubmodules in DWSIM:")
    for attr in dir(DWSIM):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
except Exception as e:
    print(f"❌ DWSIM import failed: {e}")
    
    # Try direct import of Interfaces
    try:
        import DWSIM.Interfaces
        print("✅ DWSIM.Interfaces imported")
    except Exception as e2:
        print(f"❌ DWSIM.Interfaces failed: {e2}")