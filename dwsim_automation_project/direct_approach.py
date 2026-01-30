#!/usr/bin/env python3
"""
Direct approach - try known DWSIM patterns
"""

import sys
import os

print("="*60)
print("Direct DWSIM v9 Approach")
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
clr.AddReference("DWSIM.GlobalSettings")
clr.AddReference("DWSIM.SharedClasses")

import System
import DWSIM.Interfaces
import DWSIM.GlobalSettings
import DWSIM.SharedClasses

print("\n1. Trying to import specific classes...")

# Try to import Flowsheet from different namespaces
try:
    from DWSIM import Flowsheet
    print("✅ from DWSIM import Flowsheet")
except Exception as e:
    print(f"❌ from DWSIM import Flowsheet: {e}")

try:
    from DWSIM.Interfaces import Flowsheet
    print("✅ from DWSIM.Interfaces import Flowsheet")
except Exception as e:
    print(f"❌ from DWSIM.Interfaces import Flowsheet: {e}")

try:
    from DWSIM.GlobalSettings import Flowsheet
    print("✅ from DWSIM.GlobalSettings import Flowsheet")
except Exception as e:
    print(f"❌ from DWSIM.GlobalSettings import Flowsheet: {e}")

try:
    from DWSIM.SharedClasses import Flowsheet
    print("✅ from DWSIM.SharedClasses import Flowsheet")
except Exception as e:
    print(f"❌ from DWSIM.SharedClasses import Flowsheet: {e}")

print("\n2. Looking for Flowsheet in all namespaces...")

# Get all loaded modules with DWSIM in name
for module_name in sys.modules:
    if 'DWSIM' in module_name:
        module = sys.modules[module_name]
        print(f"\nModule: {module_name}")
        
        # Check if it has Flowsheet attribute
        if hasattr(module, 'Flowsheet'):
            print(f"  ✅ Has 'Flowsheet' attribute")
            
            # Try to see what it is
            flowsheet_attr = getattr(module, 'Flowsheet')
            print(f"  Type: {type(flowsheet_attr)}")

print("\n3. Trying to use IFlowsheet interface...")

from DWSIM.Interfaces import IFlowsheet

print(f"✅ IFlowsheet type: {type(IFlowsheet)}")

# Try to find concrete implementation
print("\n4. Searching for concrete implementation of IFlowsheet...")

import System

# Get all types that implement IFlowsheet
concrete_implementations = []

# Get IFlowsheet type
iflow_type = clr.GetClrType(IFlowsheet)

for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    if "DWSIM" in str(assembly):
        try:
            for type_obj in assembly.GetTypes():
                # Check if type implements IFlowsheet
                if iflow_type.IsAssignableFrom(type_obj):
                    if not type_obj.IsInterface and not type_obj.IsAbstract:
                        concrete_implementations.append(type_obj)
                        print(f"✅ Found: {type_obj.FullName}")
        except:
            pass

print(f"\nFound {len(concrete_implementations)} concrete implementations")

# Try to instantiate each one
for i, cls in enumerate(concrete_implementations):
    print(f"\nTrying to instantiate {cls.FullName}...")
    try:
        instance = System.Activator.CreateInstance(cls)
        print(f"  ✅ Instantiated successfully")
        
        # Check for methods
        if hasattr(instance, 'CreateFlowsheet'):
            print(f"  ✅ Has CreateFlowsheet method")
            instance.CreateFlowsheet()
            print(f"  ✅ Flowsheet created")
            
            # Store for testing
            flowsheet = instance
            break
            
    except Exception as e:
        print(f"  ❌ Failed to instantiate: {e}")

print("\n5. Alternative approach: Check DWSIM documentation/patterns")

# In many DWSIM versions, you might need to use a factory or specific method
print("\nChecking DWSIM.GlobalSettings for factory methods...")

# List all methods in GlobalSettings
for attr in dir(DWSIM.GlobalSettings):
    if not attr.startswith('_'):
        attr_obj = getattr(DWSIM.GlobalSettings, attr)
        if callable(attr_obj):
            print(f"  Method: {attr}")

print("\n" + "="*60)
print("Trying last resort: Check all public methods in loaded assemblies")
print("="*60)

# Search for methods that might create a flowsheet
for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    if "DWSIM" in str(assembly):
        print(f"\nAssembly: {assembly.GetName().Name}")
        try:
            for type_obj in assembly.GetTypes():
                # Look for static methods that might create flowsheet
                methods = type_obj.GetMethods(System.Reflection.BindingFlags.Static | 
                                            System.Reflection.BindingFlags.Public)
                
                for method in methods:
                    method_name = method.Name
                    if 'Create' in method_name or 'New' in method_name or 'Flowsheet' in method_name:
                        print(f"  Found method: {type_obj.FullName}.{method_name}()")
                        
        except:
            pass