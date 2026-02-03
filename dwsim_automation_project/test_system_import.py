#!/usr/bin/env python3
"""
Test System imports in Python 3.10
"""

import sys
import os

print(f"Python version: {sys.version}")

# Python 3.10 fix
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'

# Test 1: Import pythonnet
try:
    import pythonnet
    pythonnet.load()
    print("✅ Pythonnet loaded")
except Exception as e:
    print(f"❌ Pythonnet error: {e}")

# Test 2: Import clr
try:
    import clr
    print("✅ CLR imported")
    
    # Load System assembly
    clr.AddReference("System")
    print("✅ System assembly loaded")
    
except Exception as e:
    print(f"❌ CLR error: {e}")

# Test 3: Different ways to import System in Python 3.10
print("\nTesting System imports in Python 3.10:")

# Method A: Import entire System module
try:
    import clr
    clr.AddReference("System")
    import System
    print("✅ Method A: import System")
    
    # Test Guid
    guid = System.Guid.NewGuid()
    print(f"✅ System.Guid: {guid}")
    
    # Test String
    test_str = System.String("Hello")
    print(f"✅ System.String: {test_str}")
    
    # Test Activator
    print(f"✅ System.Activator available")
    
except Exception as e:
    print(f"❌ Method A failed: {e}")

# Method B: Direct attribute access
try:
    # This works in Python 3.10
    Guid = getattr(__import__("System"), "Guid")
    guid2 = Guid.NewGuid()
    print(f"✅ Method B (getattr): Guid = {guid2}")
except Exception as e:
    print(f"❌ Method B failed: {e}")

print("\n" + "="*60)
print("System import test complete!")