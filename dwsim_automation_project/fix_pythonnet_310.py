#!/usr/bin/env python3
"""
Fix Pythonnet for Python 3.10.11
"""

import sys
import os
import subprocess

print("="*60)
print(f"Python version: {sys.version}")
print("="*60)

# Step 1: Check current installation
print("\n1. Checking pythonnet installation...")
try:
    import pip
    # Get installed packages
    installed_packages = pip.get_installed_distributions()
    pythonnet_installed = any(pkg.key == 'pythonnet' for pkg in installed_packages)
    
    if pythonnet_installed:
        print("✅ pythonnet is installed")
    else:
        print("❌ pythonnet NOT installed")
except:
    # Try pip list
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    if 'pythonnet' in result.stdout:
        print("✅ pythonnet found in pip list")
    else:
        print("❌ pythonnet NOT found in pip list")

# Step 2: Test pythonnet import
print("\n2. Testing pythonnet import...")
try:
    import pythonnet
    print(f"✅ pythonnet imported: version = {pythonnet.__version__}")
except Exception as e:
    print(f"❌ pythonnet import failed: {e}")

# Step 3: Test CLR
print("\n3. Testing CLR...")
try:
    # Python 3.10 requires pythonnet.load() BEFORE importing clr
    import pythonnet
    pythonnet.load()
    print("✅ pythonnet.load() successful")
    
    import clr
    print("✅ clr imported")
    
    # Check clr attributes
    print(f"CLR attributes: {[a for a in dir(clr) if not a.startswith('_')]}")
    
    # Try AddReference
    try:
        clr.AddReference("System")
        print("✅ clr.AddReference works")
    except AttributeError:
        print("❌ clr.AddReference missing")
        
except Exception as e:
    print(f"❌ CLR test failed: {e}")
    import traceback
    traceback.print_exc()

# Step 4: Fix if needed
print("\n4. Applying fixes if needed...")

# Check if we need to reinstall
needs_reinstall = False
try:
    import clr
    if not hasattr(clr, 'AddReference'):
        needs_reinstall = True
        print("❌ clr.AddReference missing - needs reinstall")
except:
    needs_reinstall = True
    print("❌ clr import failed - needs reinstall")

if needs_reinstall:
    print("\n5. Reinstalling pythonnet...")
    commands = [
        [sys.executable, "-m", "pip", "uninstall", "pythonnet", "clr-loader", "-y"],
        [sys.executable, "-m", "pip", "install", "pythonnet==3.0.1"],
        [sys.executable, "-m", "pip", "install", "clr-loader==0.2.4"],
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success")
        else:
            print(f"❌ Failed: {result.stderr}")
    
    print("\nPlease restart this script after installation.")
else:
    print("\n✅ pythonnet appears to be working!")

print("\n" + "="*60)