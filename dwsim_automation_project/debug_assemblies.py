#!/usr/bin/env python3
"""
Debug DWSIM assembly loading
"""

import sys
import os

print("="*60)
print("Debugging DWSIM Assembly Loading")
print("="*60)

# Python 3.10 setup
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    import pythonnet
    pythonnet.load()

import clr

# Add DWSIM path
dwsim_path = r"C:\Program Files\DWSIM"
sys.path.append(dwsim_path)
print(f"DWSIM path: {dwsim_path}")

# Check if DLLs exist
print("\n1. Checking DWSIM DLL files:")
dlls = [
    "DWSIM.Interfaces.dll",
    "DWSIM.Thermodynamics.dll", 
    "DWSIM.SharedClasses.dll",
    "DWSIM.UnitOperations.dll",
    "DWSIM.GlobalSettings.dll"
]

for dll in dlls:
    dll_path = os.path.join(dwsim_path, dll)
    if os.path.exists(dll_path):
        print(f"✅ {dll} exists")
    else:
        print(f"❌ {dll} MISSING")

# Try to load assemblies
print("\n2. Trying to load assemblies:")

# First load System
try:
    clr.AddReference("System")
    print("✅ System loaded")
except Exception as e:
    print(f"❌ System failed: {e}")

# Try different methods for each DWSIM assembly
assemblies = [
    "DWSIM.Interfaces",
    "DWSIM.Thermodynamics",
    "DWSIM.SharedClasses",
    "DWSIM.UnitOperations",
    "DWSIM.GlobalSettings"
]

for assembly in assemblies:
    print(f"\nTrying {assembly}:")
    
    # Method 1: By name
    try:
        clr.AddReference(assembly)
        print(f"  ✅ Loaded by name")
        continue
    except Exception as e:
        print(f"  ❌ By name failed: {e}")
    
    # Method 2: By file path
    try:
        dll_path = os.path.join(dwsim_path, f"{assembly}.dll")
        clr.AddReferenceToFileAndPath(dll_path)
        print(f"  ✅ Loaded by path")
        continue
    except Exception as e:
        print(f"  ❌ By path failed: {e}")
    
    # Method 3: Try loading just the base name
    try:
        simple_name = assembly.replace("DWSIM.", "")
        clr.AddReference(simple_name)
        print(f"  ✅ Loaded as {simple_name}")
        continue
    except Exception as e:
        print(f"  ❌ Simple name failed: {e}")

print("\n" + "="*60)
print("3. Checking loaded assemblies:")
print("="*60)

# List all loaded assemblies
import System
loaded_assemblies = list(System.AppDomain.CurrentDomain.GetAssemblies())
print(f"Total assemblies loaded: {len(loaded_assemblies)}")

# Filter for DWSIM assemblies
dwsim_assemblies = []
for asm in loaded_assemblies:
    asm_name = str(asm)
    if "DWSIM" in asm_name:
        dwsim_assemblies.append(asm_name)

print(f"\nDWSIM assemblies loaded ({len(dwsim_assemblies)}):")
for asm in dwsim_assemblies:
    print(f"  - {asm}")

if not dwsim_assemblies:
    print("\n❌ No DWSIM assemblies loaded!")
    print("\nPossible solutions:")
    print("1. Run DWSIM GUI once to register assemblies")
    print("2. Check DWSIM installation")
    print("3. Try loading from different path")
else:
    print("\n✅ DWSIM assemblies are loaded!")
    
    # Try to import
    print("\n4. Trying to import from loaded assemblies:")
    try:
        # This should work if assemblies are loaded
        from DWSIM.Interfaces import IFlowsheet
        print("✅ IFlowsheet imported")
    except Exception as e:
        print(f"❌ IFlowsheet import failed: {e}")