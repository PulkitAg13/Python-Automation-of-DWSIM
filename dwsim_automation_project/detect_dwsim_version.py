#!/usr/bin/env python3
"""
Detect DWSIM version and available classes
"""

import sys
import os
import clr

# Python 3.10 fix
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    import pythonnet
    pythonnet.load()

# Add DWSIM path
dwsim_path = r"C:\Program Files\DWSIM"
sys.path.append(dwsim_path)

print("="*60)
print("DWSIM Version Detection")
print("="*60)

# Load assemblies
assemblies = [
    "DWSIM.Interfaces",
    "DWSIM.GlobalSettings",
    "DWSIM.Thermodynamics",
    "DWSIM.SharedClasses",
    "DWSIM.UnitOperations"
]

for assembly in assemblies:
    try:
        clr.AddReference(assembly)
        print(f"✅ {assembly} loaded")
    except Exception as e:
        print(f"❌ {assembly} failed: {e}")

print("\n" + "="*60)
print("Available classes in DWSIM.Thermodynamics:")
print("="*60)

# Inspect DWSIM.Thermodynamics module
try:
    import DWSIM.Thermodynamics as ThermoMod
    
    print("All attributes in DWSIM.Thermodynamics:")
    for attr in dir(ThermoMod):
        if not attr.startswith('_'):  # Skip private attributes
            print(f"  - {attr}")
    
    print("\nLooking for PropertyPackage or similar classes:")
    property_package_candidates = []
    for attr in dir(ThermoMod):
        if "Property" in attr or "Thermo" in attr or "Package" in attr:
            obj = getattr(ThermoMod, attr)
            print(f"  - {attr}: {type(obj)}")
            if "class" in str(type(obj)).lower():
                property_package_candidates.append(attr)
    
    print("\n" + "="*60)
    print("PropertyPackage Candidates:")
    print("="*60)
    for candidate in property_package_candidates:
        print(f"  - {candidate}")
        
        # Try to instantiate
        try:
            cls = getattr(ThermoMod, candidate)
            instance = cls()
            print(f"    ✅ Can instantiate: {instance}")
            print(f"    ✅ Class name: {cls.__name__}")
        except Exception as e:
            print(f"    ❌ Cannot instantiate: {e}")
    
except Exception as e:
    print(f"❌ Error inspecting thermodynamics: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Testing import methods:")
print("="*60)

# Try different import methods
import_methods = [
    ("from DWSIM.Thermodynamics import PropertyPackage", 
     lambda: exec("from DWSIM.Thermodynamics import PropertyPackage")),
    
    ("from DWSIM.Thermodynamics import Thermodynamics",
     lambda: exec("from DWSIM.Thermodynamics import Thermodynamics")),
    
    ("import DWSIM.Thermodynamics as Thermo",
     lambda: exec("import DWSIM.Thermodynamics as Thermo")),
]

for method_name, method_func in import_methods:
    try:
        method_func()
        print(f"✅ {method_name}")
    except Exception as e:
        print(f"❌ {method_name}: {e}")