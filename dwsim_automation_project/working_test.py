#!/usr/bin/env python3
"""
Simple working test for DWSIM v9
"""

import sys
import os

print("="*60)
print("Simple Working Test")
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

# Load minimal assemblies
clr.AddReference("System")
clr.AddReference("DWSIM.Interfaces")

import System

print("\n1. Trying to create DWSIM application instance...")

# In some DWSIM versions, there might be an Application class
try:
    # Try to find Application class
    for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
        if "DWSIM" in str(assembly):
            try:
                for type_obj in assembly.GetTypes():
                    if "Application" in type_obj.FullName:
                        print(f"Found Application class: {type_obj.FullName}")
                        
                        # Try to get static instance
                        if hasattr(type_obj, 'Instance') or hasattr(type_obj, 'Current'):
                            print("Has Instance/Current property")
                            
            except:
                pass
except Exception as e:
    print(f"Error: {e}")

print("\n2. Let's check what DWSIM.Interfaces actually contains...")

import DWSIM.Interfaces

print("\nAttributes in DWSIM.Interfaces module:")
count = 0
for attr in dir(DWSIM.Interfaces):
    if not attr.startswith('_'):
        count += 1
        if count <= 20:  # Show first 20
            print(f"  - {attr}")

print(f"\nTotal public attributes: {count}")

print("\n3. Looking for IFlowsheet...")

if hasattr(DWSIM.Interfaces, 'IFlowsheet'):
    print("✅ IFlowsheet found in DWSIM.Interfaces")
    
    # Get the type
    IFlowsheet_type = getattr(DWSIM.Interfaces, 'IFlowsheet')
    print(f"Type: {IFlowsheet_type}")
    
    # Try to find concrete implementation
    print("\n4. Searching for classes implementing IFlowsheet...")
    
    concrete_classes = []
    for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
        if "DWSIM" in str(assembly):
            try:
                for type_obj in assembly.GetTypes():
                    # Check if implements IFlowsheet
                    if IFlowsheet_type.IsAssignableFrom(type_obj):
                        if not type_obj.IsInterface and not type_obj.IsAbstract:
                            concrete_classes.append(type_obj)
                            print(f"✅ Concrete class: {type_obj.FullName}")
            except:
                pass
    
    print(f"\nFound {len(concrete_classes)} concrete classes")
    
    # Try to instantiate each
    for cls in concrete_classes:
        print(f"\nTrying to instantiate {cls.FullName}...")
        try:
            instance = System.Activator.CreateInstance(cls)
            print(f"✅ Instantiated successfully!")
            
            # Check for important methods
            if hasattr(instance, 'CreateFlowsheet'):
                print(f"✅ Has CreateFlowsheet method")
                instance.CreateFlowsheet()
                print(f"✅ Flowsheet created!")
                
                # Test adding object
                if hasattr(instance, 'AddObject'):
                    print(f"✅ Has AddObject method")
                    
                    # Add a material stream
                    stream_id = System.Guid.NewGuid()
                    stream = instance.AddObject(stream_id, "Material Stream", "Test", 0, 0)
                    print(f"✅ Material stream added: {stream}")
                    
                    print("\n🎉 SUCCESS! DWSIM is working!")
                    break
                    
        except Exception as e:
            print(f"❌ Failed: {e}")
    
else:
    print("❌ IFlowsheet not found in DWSIM.Interfaces")

print("\n" + "="*60)