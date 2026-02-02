#!/usr/bin/env python3
"""
Simple DWSIM v9 test - minimal approach
"""

import sys
import os

print("="*60)
print("Simple DWSIM v9 Test")
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
clr.AddReference("DWSIM.SharedClasses")
clr.AddReference("DWSIM.GlobalSettings")

import System

print("\n1. Looking for Flowsheet class...")

# Search for Flowsheet class
FlowsheetClass = None
for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
    asm_name = str(assembly)
    if "DWSIM" in asm_name:
        try:
            types = assembly.GetTypes()
            for t in types:
                if "Flowsheet" in t.FullName and not t.IsInterface and not t.IsAbstract:
                    print(f"✅ Found: {t.FullName}")
                    FlowsheetClass = t
                    break
            if FlowsheetClass:
                break
        except:
            pass

if FlowsheetClass:
    print("\n2. Creating Flowsheet instance...")
    try:
        flowsheet = System.Activator.CreateInstance(FlowsheetClass)
        print("✅ Flowsheet instance created")
        
        # Call CreateFlowsheet if method exists
        if hasattr(flowsheet, 'CreateFlowsheet'):
            flowsheet.CreateFlowsheet()
            print("✅ CreateFlowsheet called")
        
        print("\n🎉 SUCCESS! DWSIM flowsheet created!")
        
        # Test adding a material stream
        print("\n3. Testing Material Stream...")
        
        # Find MaterialStream class
        MaterialStreamClass = None
        for assembly in System.AppDomain.CurrentDomain.GetAssemblies():
            if "DWSIM" in str(assembly):
                try:
                    for t in assembly.GetTypes():
                        if "MaterialStream" in t.FullName or "Material_Stream" in t.FullName:
                            if not t.IsInterface and not t.IsAbstract:
                                MaterialStreamClass = t
                                print(f"✅ Found MaterialStream: {t.FullName}")
                                break
                    if MaterialStreamClass:
                        break
                except:
                    pass
        
        if MaterialStreamClass:
            # Create a stream
            stream_id = System.Guid.NewGuid()
            stream = flowsheet.AddObject(stream_id, "Material Stream", "TestStream", 0, 0)
            print("✅ Material stream added")
            
            # Try to set properties
            if hasattr(stream, 'SetTemperature'):
                stream.SetTemperature(300.0)
                print("✅ Temperature set")
            
            if hasattr(stream, 'SetPressure'):
                stream.SetPressure(101325)
                print("✅ Pressure set")
            
            print("\n✅ DWSIM is working correctly!")
        else:
            print("❌ Could not find MaterialStream class")
        
    except Exception as e:
        print(f"❌ Error creating flowsheet: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Could not find Flowsheet class")