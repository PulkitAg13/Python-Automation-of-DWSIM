#!/usr/bin/env python3
"""
Find concrete DWSIM v9 classes
"""

import sys
import os

print("="*60)
print("Finding Concrete DWSIM v9 Classes")
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

import System

print("\n1. Looking for classes that implement IFlowsheet...")

# Get IFlowsheet type
IFlowsheet_type = clr.GetClrType(type(clr.AddReference("DWSIM.Interfaces")))

# Search through all loaded assemblies
concrete_classes = []
for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    try:
        for type_obj in assembly.GetTypes():
            # Check if it implements IFlowsheet
            if IFlowsheet_type.IsAssignableFrom(type_obj) and not type_obj.IsInterface and not type_obj.IsAbstract:
                concrete_classes.append(type_obj.FullName)
    except:
        pass

print(f"\nFound {len(concrete_classes)} concrete classes implementing IFlowsheet:")
for cls in concrete_classes:
    print(f"  - {cls}")

print("\n2. Searching for Flowsheet class...")

# Look for Flowsheet in all assemblies
for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    if "DWSIM" in str(assembly):
        print(f"\nSearching in assembly: {assembly.GetName().Name}")
        try:
            for type_obj in assembly.GetTypes():
                type_name = type_obj.FullName
                if "Flowsheet" in type_name and not type_obj.IsInterface and not type_obj.IsAbstract:
                    print(f"  ✅ Found: {type_name}")
                    
                    # Try to create instance
                    try:
                        instance = System.Activator.CreateInstance(type_obj)
                        print(f"     ✅ Can instantiate")
                        
                        # Check for CreateFlowsheet method
                        if hasattr(instance, 'CreateFlowsheet'):
                            print(f"     ✅ Has CreateFlowsheet method")
                            instance.CreateFlowsheet()
                            print(f"     ✅ Flowsheet created successfully!")
                            
                            # Store for later use
                            flowsheet_instance = instance
                            flowsheet_type = type_obj
                            break
                            
                    except Exception as e:
                        print(f"     ❌ Cannot instantiate: {e}")
        except:
            pass

print("\n3. Looking for PropertyPackage or similar...")

# Search for thermodynamics classes
for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    if "DWSIM" in str(assembly):
        print(f"\nAssembly: {assembly.GetName().Name}")
        try:
            for type_obj in assembly.GetTypes():
                type_name = type_obj.FullName
                if ("Property" in type_name or "Thermo" in type_name) and "Package" in type_name:
                    if not type_obj.IsInterface and not type_obj.IsAbstract:
                        print(f"  🔍 Found: {type_name}")
                        
                        # Try to instantiate
                        try:
                            instance = System.Activator.CreateInstance(type_obj)
                            print(f"     ✅ Can instantiate")
                            
                            # Check for ComponentName
                            if hasattr(instance, 'ComponentName'):
                                instance.ComponentName = "Raoult's Law"
                                print(f"     ✅ Has ComponentName: {instance.ComponentName}")
                                
                                # Store thermo class
                                thermo_class = type_obj
                                thermo_instance = instance
                                
                        except Exception as e:
                            print(f"     ❌ Cannot instantiate: {e}")
        except:
            pass

print("\n4. Testing DWSIM unit operations...")

# Try to find MaterialStream class
for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    if "DWSIM" in str(assembly):
        try:
            for type_obj in assembly.GetTypes():
                type_name = type_obj.FullName
                if "MaterialStream" in type_name or "Material_Stream" in type_name:
                    if not type_obj.IsInterface and not type_obj.IsAbstract:
                        print(f"✅ Found MaterialStream: {type_name}")
                        material_stream_class = type_obj
                        break
        except:
            pass

print("\n" + "="*60)
print("Summary of Found Classes:")
print("="*60)

# List all DWSIM classes
for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    if "DWSIM" in str(assembly):
        print(f"\n{assembly.GetName().Name}:")
        try:
            types = assembly.GetTypes()
            print(f"  Total types: {len(types)}")
            
            # List concrete classes (non-interface, non-abstract)
            concrete = [t for t in types if not t.IsInterface and not t.IsAbstract]
            print(f"  Concrete classes: {len(concrete)}")
            
            # Show important ones
            important_classes = []
            for t in concrete:
                name = t.FullName
                if any(keyword in name for keyword in ['Flowsheet', 'Stream', 'Reactor', 'Column', 'Property', 'Thermo']):
                    important_classes.append(name)
            
            if important_classes:
                print(f"\n  Important classes:")
                for cls in important_classes[:10]:  # Show first 10
                    print(f"    - {cls}")
                    
        except:
            print("  Cannot enumerate types")