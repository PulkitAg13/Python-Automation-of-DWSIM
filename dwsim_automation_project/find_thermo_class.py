#!/usr/bin/env python3
"""
Find the correct thermodynamics class name
"""

import sys
import os

# Python 3.10 setup
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    import pythonnet
    pythonnet.load()

import clr

# Add DWSIM path
dwsim_path = r"C:\Program Files\DWSIM"
sys.path.append(dwsim_path)

# Load assemblies
clr.AddReference("System")
clr.AddReference("DWSIM.Interfaces")
clr.AddReference("DWSIM.Thermodynamics")

import System
import DWSIM.Thermodynamics as ThermoMod

print("="*60)
print("Finding DWSIM Thermodynamics Classes")
print("="*60)

# List ALL classes in Thermodynamics module
print("\nAll public attributes in DWSIM.Thermodynamics:")
all_attrs = []

for attr_name in dir(ThermoMod):
    if not attr_name.startswith('_'):
        attr = getattr(ThermoMod, attr_name)
        all_attrs.append((attr_name, type(attr).__name__))
        print(f"  {attr_name:30} -> {type(attr).__name__}")

# Filter for likely PropertyPackage candidates
print("\n\nLikely PropertyPackage candidates:")
candidates = []

for attr_name, attr_type in all_attrs:
    attr = getattr(ThermoMod, attr_name)
    
    # Check if it's a class (not a module, function, etc.)
    is_class = False
    try:
        # Try to check if it's a CLR type
        if hasattr(attr, '__class__'):
            class_str = str(attr.__class__)
            if 'RuntimeType' in class_str or 'Type' in class_str:
                is_class = True
    except:
        pass
    
    # Also check by naming patterns
    if ('Property' in attr_name or 'Thermo' in attr_name or 
        'Package' in attr_name or 'PP' in attr_name):
        candidates.append((attr_name, attr, is_class))

for attr_name, attr, is_class in candidates:
    print(f"\n{attr_name}:")
    print(f"  Is class: {is_class}")
    
    # Try to instantiate
    if is_class:
        try:
            instance = attr()
            print(f"  ✅ Can instantiate")
            
            # Check for ComponentName property
            if hasattr(instance, 'ComponentName'):
                print(f"  ✅ Has ComponentName property")
                instance.ComponentName = "Raoult's Law"
                print(f"  ✅ ComponentName set to: {instance.ComponentName}")
                
            # List some properties
            props = [p for p in dir(instance) if not p.startswith('_')]
            print(f"  Properties (first 10): {props[:10]}")
            
        except Exception as e:
            print(f"  ❌ Cannot instantiate: {e}")
    else:
        print(f"  Not a class (type: {type(attr)})")

print("\n" + "="*60)
print("Suggested imports:")
print("="*60)

# Based on findings, suggest import statements
for attr_name, attr, is_class in candidates:
    if is_class:
        print(f"from DWSIM.Thermodynamics import {attr_name}")
        print(f"# Usage: thermo = {attr_name}()")
        print(f"#        thermo.ComponentName = \"Raoult's Law\"")
        print()