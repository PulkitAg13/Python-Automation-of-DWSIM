#!/usr/bin/env python3
"""
Test DWSIM with Python 3.10 - Simplified
"""

import sys
import os

print("="*60)
print("DWSIM Python 3.10 Test")
print("="*60)

# Python 3.10 specific setup
if sys.version_info >= (3, 10):
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'

# Initialize pythonnet
try:
    import pythonnet
    pythonnet.load()
    print("✅ Pythonnet initialized")
except Exception as e:
    print(f"❌ Pythonnet error: {e}")
    sys.exit(1)

# Test CLR
try:
    import clr
    print("✅ CLR imported")
    
    # Load System
    clr.AddReference("System")
    print("✅ System loaded")
    
    # Test System imports
    import System
    print(f"✅ System imported: {System}")
    
    # Test Guid
    guid = System.Guid.NewGuid()
    print(f"✅ System.Guid: {guid}")
    
except Exception as e:
    print(f"❌ CLR/System error: {e}")
    sys.exit(1)

# Test DWSIM
print("\n" + "="*60)
print("Testing DWSIM...")
print("="*60)

try:
    # Add DWSIM path
    dwsim_path = r"C:\Program Files\DWSIM"
    if os.path.exists(dwsim_path):
        sys.path.append(dwsim_path)
        print(f"✅ DWSIM path added: {dwsim_path}")
    else:
        print(f"❌ DWSIM not found at: {dwsim_path}")
        sys.exit(1)
    
    # Load DWSIM assemblies
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
            # Try by file path
            try:
                dll_path = os.path.join(dwsim_path, f"{assembly}.dll")
                clr.AddReferenceToFileAndPath(dll_path)
                print(f"✅ {assembly} loaded by path")
            except:
                print(f"❌ {assembly} completely failed")
                sys.exit(1)
    
    # Import DWSIM types
    try:
        from DWSIM.Interfaces import IFlowsheet
        from DWSIM.GlobalSettings import Settings
        from DWSIM.Thermodynamics import PropertyPackage
        print("✅ DWSIM types imported")
        
        # Create instance
        flowsheet = System.Activator.CreateInstance(IFlowsheet)
        flowsheet.CreateFlowsheet()
        print("✅ DWSIM flowsheet created")
        
        print("\n🎉 SUCCESS! DWSIM works with Python 3.10!")
        
    except Exception as e:
        print(f"❌ DWSIM import/creation failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)