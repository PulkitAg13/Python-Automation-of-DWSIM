#!/usr/bin/env python3
"""
Simple DWSIM test - finds correct class names
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

print("Testing DWSIM import...")

# Load required assemblies
assemblies = [
    "System",
    "DWSIM.Interfaces",
    "DWSIM.Thermodynamics",
    "DWSIM.SharedClasses"
]

for assembly in assemblies:
    try:
        clr.AddReference(assembly)
        print(f"✅ {assembly} loaded")
    except Exception as e:
        print(f"❌ {assembly}: {e}")

# Try to find the correct thermodynamics class
print("\nFinding thermodynamics class...")

import DWSIM.Thermodynamics as ThermoMod

# List all public classes in Thermodynamics
thermo_classes = []
for attr_name in dir(ThermoMod):
    attr = getattr(ThermoMod, attr_name)
    # Check if it's a class (not a function or module)
    if isinstance(attr, type) or "class" in str(type(attr)).lower():
        if not attr_name.startswith('_'):  # Skip private
            thermo_classes.append(attr_name)

print(f"Found {len(thermo_classes)} classes:")
for cls_name in thermo_classes:
    print(f"  - {cls_name}")

# Try to find PropertyPackage
print("\nLooking for PropertyPackage...")
property_package_class = None

for cls_name in thermo_classes:
    if "PropertyPackage" in cls_name or "Thermo" in cls_name:
        print(f"\nTrying {cls_name}...")
        try:
            cls = getattr(ThermoMod, cls_name)
            # Try to create instance
            instance = cls()
            print(f"✅ {cls_name} can be instantiated")
            print(f"   Instance: {instance}")
            print(f"   Methods: {[m for m in dir(instance) if not m.startswith('_')][:10]}...")
            
            # Check if it has ComponentName property
            if hasattr(instance, 'ComponentName'):
                instance.ComponentName = "Raoult's Law"
                print(f"   ✅ Has ComponentName: {instance.ComponentName}")
                property_package_class = cls_name
                break
                
        except Exception as e:
            print(f"❌ {cls_name} failed: {e}")

if property_package_class:
    print(f"\n🎉 Found PropertyPackage class: {property_package_class}")
    print(f"\nUse this in your code:")
    print(f"from DWSIM.Thermodynamics import {property_package_class}")
    print(f"thermo = {property_package_class}()")
    print(f'thermo.ComponentName = "Raoult\'s Law"')
else:
    print("\n❌ Could not find PropertyPackage class")
    print("\nTry these alternatives in your code:")
    print("1. from DWSIM.Thermodynamics import *  # Then see what's available")
    print("2. import DWSIM.Thermodynamics as Thermo")
    print("3. Check DWSIM documentation for correct class name")