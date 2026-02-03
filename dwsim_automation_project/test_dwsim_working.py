#!/usr/bin/env python3
"""
Test DWSIM with working CLR
"""

import sys
import os

print("="*60)
print("DWSIM Test with Working CLR")
print("="*60)

# Python 3.10 setup - USE METHOD 1 FROM YOUR SUCCESSFUL TEST
if sys.version_info >= (3, 10):
    print("Python 3.10+ detected")
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    
    # Method 1 that worked for you
    import pythonnet
    pythonnet.load()
    print("✅ pythonnet.load() successful")

# Import clr
import clr
print("✅ clr imported")
print(f"clr.AddReference exists: {hasattr(clr, 'AddReference')}")

# Add DWSIM path
dwsim_path = r"C:\Program Files\DWSIM"
sys.path.append(dwsim_path)
print(f"✅ DWSIM path added: {dwsim_path}")

# Load System first
clr.AddReference("System")
print("✅ System assembly loaded")

import System
print(f"✅ System module imported")

# Load DWSIM assemblies
print("\nLoading DWSIM assemblies...")

assemblies = [
    "DWSIM.Interfaces",
    "DWSIM.Thermodynamics", 
    "DWSIM.SharedClasses",
    "DWSIM.UnitOperations",
    "DWSIM.GlobalSettings"
]

for assembly in assemblies:
    try:
        clr.AddReference(assembly)
        print(f"✅ {assembly} loaded")
    except Exception as e:
        print(f"❌ {assembly} failed: {e}")

print("\n" + "="*60)
print("Testing DWSIM imports...")
print("="*60)

# Try to import DWSIM types
try:
    from DWSIM.Interfaces import IFlowsheet
    print("✅ IFlowsheet imported")
except Exception as e:
    print(f"❌ IFlowsheet import failed: {e}")

# Try to import Thermodynamics
print("\nTesting Thermodynamics imports...")
try:
    import DWSIM.Thermodynamics as ThermoMod
    print("✅ DWSIM.Thermodynamics module imported")
    
    # List available classes
    print("\nAvailable classes in DWSIM.Thermodynamics:")
    for attr in dir(ThermoMod):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
except Exception as e:
    print(f"❌ DWSIM.Thermodynamics import failed: {e}")

print("\n" + "="*60)
print("Creating DWSIM instance...")
print("="*60)

try:
    # Get IFlowsheet type
    IFlowsheet_type = clr.GetClrType(IFlowsheet)
    
    # Create instance
    flowsheet = System.Activator.CreateInstance(IFlowsheet_type)
    print("✅ DWSIM instance created")
    
    # Call CreateFlowsheet if method exists
    if hasattr(flowsheet, 'CreateFlowsheet'):
        flowsheet.CreateFlowsheet()
        print("✅ Flowsheet created")
    
    print("\n🎉 SUCCESS! DWSIM is working!")
    
except Exception as e:
    print(f"❌ Failed to create DWSIM instance: {e}")
    import traceback
    traceback.print_exc()