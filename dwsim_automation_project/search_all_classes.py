#!/usr/bin/env python3
"""
Comprehensive search for all DWSIM v9 classes
"""

import sys
import os

print("="*60)
print("Comprehensive DWSIM v9 Class Search")
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

# Load ALL DWSIM assemblies
print("\n1. Loading all DWSIM assemblies...")

# List all DLLs in DWSIM directory
dll_files = []
for file in os.listdir(dwsim_path):
    if file.endswith('.dll') and 'DWSIM' in file:
        dll_files.append(file)

print(f"Found {len(dll_files)} DWSIM DLLs:")
for dll in dll_files:
    print(f"  - {dll}")

# Try to load each DLL
loaded_assemblies = []
for dll in dll_files:
    try:
        dll_path = os.path.join(dwsim_path, dll)
        assembly_name = dll.replace('.dll', '')
        clr.AddReferenceToFileAndPath(dll_path)
        loaded_assemblies.append(assembly_name)
        print(f"✅ Loaded: {assembly_name}")
    except Exception as e:
        print(f"❌ Failed to load {dll}: {e}")

print("\n2. Searching for Flowsheet and related classes...")

import System

# Search through ALL loaded assemblies
all_classes = []

for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    asm_name = str(assembly)
    if any(dll_name in asm_name for dll_name in loaded_assemblies):
        print(f"\n📦 Searching in: {assembly.GetName().Name}")
        
        try:
            types = assembly.GetTypes()
            print(f"  Total types: {len(types)}")
            
            # Filter concrete classes
            concrete = [t for t in types if not t.IsInterface and not t.IsAbstract]
            print(f"  Concrete classes: {len(concrete)}")
            
            # Look for important classes
            important_keywords = [
                'Flowsheet', 'Stream', 'Reactor', 'Column', 
                'Property', 'Thermo', 'Material', 'Distillation',
                'UnitOp', 'UnitOperation'
            ]
            
            important_classes = []
            for t in concrete:
                name = t.FullName
                if any(keyword in name for keyword in important_keywords):
                    important_classes.append(t)
                    print(f"    🔍 {name}")
            
            all_classes.extend(important_classes)
            
        except Exception as e:
            print(f"  Cannot enumerate types: {e}")

print("\n3. Trying to find and instantiate key classes...")

# Look for Flowsheet class
print("\n🔍 Looking for Flowsheet class...")
flowsheet_class = None
for cls in all_classes:
    if 'Flowsheet' in cls.FullName and 'FlowsheetUtility' not in cls.FullName:
        print(f"\nTrying class: {cls.FullName}")
        try:
            instance = System.Activator.CreateInstance(cls)
            print(f"  ✅ Can instantiate")
            
            # Check for important methods
            methods_to_check = ['CreateFlowsheet', 'AddObject', 'SolveFlowsheet']
            for method in methods_to_check:
                if hasattr(instance, method):
                    print(f"  ✅ Has {method} method")
            
            flowsheet_class = cls
            flowsheet_instance = instance
            break
            
        except Exception as e:
            print(f"  ❌ Cannot instantiate: {e}")

if flowsheet_class:
    print(f"\n🎉 Found working Flowsheet class: {flowsheet_class.FullName}")
    
    # Try to create flowsheet
    if hasattr(flowsheet_instance, 'CreateFlowsheet'):
        flowsheet_instance.CreateFlowsheet()
        print("✅ Flowsheet created")
    
    # Test adding an object
    print("\n🔧 Testing AddObject method...")
    try:
        import System
        obj_id = System.Guid.NewGuid()
        
        # Try to add a material stream
        added_obj = flowsheet_instance.AddObject(obj_id, "Material Stream", "TestStream", 0, 0)
        print(f"✅ Object added: {added_obj}")
        
        # Check object type
        print(f"  Object type: {type(added_obj)}")
        print(f"  Object class: {added_obj.GetType().FullName}")
        
    except Exception as e:
        print(f"❌ AddObject failed: {e}")
else:
    print("\n❌ Could not find working Flowsheet class")

print("\n4. Looking for unit operation classes...")

# Search for specific unit operations
unit_ops = ['Material Stream', 'Reactor - PFR', 'Distillation Column']

for unit_op in unit_ops:
    print(f"\n🔍 Looking for: {unit_op}")
    
    # This would be registered in DWSIM, not a .NET class
    # We'll check what AddObject returns

print("\n5. Checking DWSIM.GlobalSettings assembly...")

# Load GlobalSettings if not already loaded
try:
    clr.AddReference("DWSIM.GlobalSettings")
    import DWSIM.GlobalSettings as GS
    
    print("✅ DWSIM.GlobalSettings loaded")
    
    # List available attributes
    print("\nAttributes in DWSIM.GlobalSettings:")
    for attr in dir(GS):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
except Exception as e:
    print(f"❌ DWSIM.GlobalSettings: {e}")

print("\n" + "="*60)
print("Search complete!")
print("="*60)