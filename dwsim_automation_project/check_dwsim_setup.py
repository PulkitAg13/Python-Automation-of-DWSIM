"""
Diagnostic script to check DWSIM setup
"""

import os
import sys
import clr
from pathlib import Path

def check_dwsim_installation():
    """Check if DWSIM is properly installed"""
    
    print("="*60)
    print("DWSIM Installation Diagnostic")
    print("="*60)
    
    # Get DWSIM path from environment
    dwsim_path = os.getenv('DWSIM_PATH', 'C:\\Program Files\\DWSIM')
    dwsim_path = os.path.normpath(dwsim_path)
    
    print(f"\n1. Checking DWSIM path: {dwsim_path}")
    
    # Check if path exists
    if not os.path.exists(dwsim_path):
        print("❌ ERROR: DWSIM path does not exist!")
        print(f"   Please check: {dwsim_path}")
        return False
    
    print("✅ DWSIM directory exists")
    
    # Check for required files
    print("\n2. Checking required files:")
    
    required_files = [
        "DWSIM.exe",
        "DWSIM.Interfaces.dll",
        "DWSIM.GlobalSettings.dll",
        "DWSIM.Thermodynamics.dll",
        "DWSIM.UnitOperations.dll",
        "DWSIM.SharedClasses.dll"
    ]
    
    all_files_exist = True
    for file in required_files:
        file_path = os.path.join(dwsim_path, file)
        if os.path.exists(file_path):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some required files are missing!")
        print("   Try reinstalling DWSIM with 'Complete' installation")
        return False
    
    # Try to load assemblies
    print("\n3. Trying to load DWSIM assemblies...")
    
    try:
        # Add path to sys.path
        if dwsim_path not in sys.path:
            sys.path.append(dwsim_path)
        
        # Try to load System assembly first
        clr.AddReference("System")
        print("   ✅ System assembly loaded")
        
        # Try to load DWSIM assemblies
        assemblies_to_try = [
            "DWSIM.Interfaces",
            "DWSIM.GlobalSettings", 
            "DWSIM.Thermodynamics",
            "DWSIM.UnitOperations",
            "DWSIM.SharedClasses"
        ]
        
        for assembly in assemblies_to_try:
            try:
                clr.AddReference(assembly)
                print(f"   ✅ {assembly} loaded")
            except Exception as e:
                print(f"   ❌ {assembly}: {str(e)}")
                # Try loading by file path
                try:
                    dll_path = os.path.join(dwsim_path, f"{assembly}.dll")
                    clr.AddReferenceToFileAndPath(dll_path)
                    print(f"   ✅ {assembly} loaded by path")
                except:
                    print(f"   ❌ {assembly} failed by path too")
                    return False
        
        print("\n✅ All assemblies loaded successfully!")
        
        # Try to import types
        print("\n4. Trying to import DWSIM types...")
        
        try:
            from DWSIM.Interfaces import IFlowsheet
            from DWSIM.GlobalSettings import Settings
            from DWSIM.Thermodynamics import PropertyPackage
            print("   ✅ DWSIM types imported successfully")
            
            print("\n" + "="*60)
            print("🎉 DWSIM IS PROPERLY INSTALLED AND CONFIGURED!")
            print("Your Python automation should work now.")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to import DWSIM types: {str(e)}")
            print("\n   Try running DWSIM GUI once to register assemblies")
            return False
        
    except Exception as e:
        print(f"❌ Error during assembly loading: {str(e)}")
        return False

def check_pythonnet():
    """Check if pythonnet is working"""
    print("\n" + "="*60)
    print("Checking Pythonnet Setup")
    print("="*60)
    
    try:
        import pythonnet
        print("✅ Pythonnet imported")
    except ImportError as e:
        print(f"❌ Pythonnet not installed: {e}")
        print("Run: pip install pythonnet==3.0.2")
        return False
    
    try:
        import clr
        print("✅ CLR imported")
        
        # Test CLR functionality
        clr.AddReference("System")
        from System import String
        print("✅ System.String imported via CLR")
        
        return True
        
    except Exception as e:
        print(f"❌ CLR error: {e}")
        return False

if __name__ == "__main__":
    # Check pythonnet first
    if not check_pythonnet():
        print("\n❌ Pythonnet setup failed")
        sys.exit(1)
    
    # Check DWSIM
    if not check_dwsim_installation():
        print("\n❌ DWSIM setup failed")
        sys.exit(1)