#!/usr/bin/env python3
"""
Explore DWSIM v9.0.5 classes
"""

import sys
import os

print("="*60)
print(f"DWSIM Version: 9.0.5")
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

# Load assemblies
clr.AddReference("System")
clr.AddReference("DWSIM.Interfaces")
clr.AddReference("DWSIM.Thermodynamics")
clr.AddReference("DWSIM.SharedClasses")

import System
import DWSIM.Interfaces
import DWSIM.Thermodynamics
import DWSIM.SharedClasses

print("\n1. Exploring DWSIM.Thermodynamics module:")

# Get ALL public members
thermo_members = []
for attr_name in dir(DWSIM.Thermodynamics):
    if not attr_name.startswith('_'):
        attr = getattr(DWSIM.Thermodynamics, attr_name)
        thermo_members.append((attr_name, attr))

print(f"\nFound {len(thermo_members)} public members:")
for attr_name, attr in thermo_members:
    attr_type = type(attr).__name__
    print(f"  {attr_name:30} -> {attr_type}")

# Look for classes (not modules or other types)
print("\n2. Looking for CLASSES in DWSIM.Thermodynamics:")

for attr_name, attr in thermo_members:
    # Check if it's a class
    is_class = False
    try:
        # For CLR types in Pythonnet
        if hasattr(attr, '__class__'):
            class_str = str(attr.__class__)
            if 'RuntimeType' in class_str or 'Type' in class_str:
                is_class = True
    except:
        pass
    
    if is_class:
        print(f"\n🔍 Class found: {attr_name}")
        print(f"   Type: {type(attr)}")
        
        # Try to instantiate
        try:
            instance = attr()
            print(f"   ✅ Can instantiate")
            
            # Check for properties
            props = [p for p in dir(instance) if not p.startswith('_')]
            print(f"   Properties ({len(props)} total):")
            
            # Show important properties
            important_props = ['ComponentName', 'Name', 'PackageName', 'PropertyPackage']
            for prop in important_props:
                if prop in props:
                    print(f"     ✅ {prop}")
                    
            # Try to set ComponentName
            if 'ComponentName' in props:
                instance.ComponentName = "Raoult's Law"
                print(f"     ✅ ComponentName set to: {instance.ComponentName}")
                
        except Exception as e:
            print(f"   ❌ Cannot instantiate: {e}")

print("\n3. Checking what 'import *' gives us:")
print("="*60)

# Try to see what's available with wildcard import
try:
    # Create local namespace for import *
    exec("from DWSIM.Thermodynamics import *")
    local_vars = locals()
    
    print("Names imported with 'from DWSIM.Thermodynamics import *':")
    for var_name, var_value in local_vars.items():
        if not var_name.startswith('_') and var_name not in ['sys', 'os', 'clr', 'System']:
            print(f"  {var_name}")
            
except Exception as e:
    print(f"❌ Wildcard import failed: {e}")

print("\n4. Creating DWSIM instance:")
print("="*60)

# Create a DWSIM instance
from DWSIM.Interfaces import IFlowsheet

flowsheet = System.Activator.CreateInstance(IFlowsheet)
flowsheet.CreateFlowsheet()

print("✅ Flowsheet created")

# Now let's explore the Options property
print("\n5. Exploring flowsheet.Options:")
if hasattr(flowsheet, 'Options'):
    options = flowsheet.Options
    print("Options properties:")
    for prop in dir(options):
        if not prop.startswith('_'):
            print(f"  - {prop}")
            
    # Look for PropertyPackage related properties
    print("\nPropertyPackage related properties:")
    for prop in dir(options):
        if 'Property' in prop or 'Package' in prop or 'Thermo' in prop:
            print(f"  - {prop}")
            
            # Try to get/set
            try:
                prop_value = getattr(options, prop)
                print(f"    Current value: {type(prop_value).__name__}")
            except:
                print(f"    Cannot access")