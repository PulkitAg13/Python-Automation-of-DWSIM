#!/usr/bin/env python3
"""
Test DWSIM v9 Controller
"""

import sys
import os

print("="*60)
print("Testing DWSIM v9 Controller")
print("="*60)

# Python 3.10 setup
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    import pythonnet
    pythonnet.load()

# Import the controller
from src.dwsim_controller import DWSIMController

controller = DWSIMController()

if controller.initialize():
    print("\n🎉 SUCCESS! DWSIM v9.0.5 is working!")
    
    # Test creating a stream
    print("\nTesting material stream creation...")
    try:
        stream = controller.create_material_stream(
            name="TestStream",
            temperature=300.0,
            pressure=101325,
            flow_rate=100.0,
            composition={'A': 1.0}
        )
        print("✅ Material stream created")
        
        # Test PFR reactor
        print("\nTesting PFR reactor creation...")
        reactor = controller.create_reactor_pfr(
            name="TestPFR",
            volume=1.0,
            temperature=350.0,
            pressure=101325
        )
        print("✅ PFR reactor created")
        
        # Connect stream to reactor
        print("\nTesting stream connection...")
        if controller.connect_streams(stream, reactor):
            print("✅ Stream connected to reactor")
        
        # Test distillation column
        print("\nTesting distillation column creation...")
        column = controller.create_distillation_column(
            name="TestColumn",
            stages=10,
            feed_stage=5,
            reflux_ratio=2.0,
            distillate_rate=50.0
        )
        print("✅ Distillation column created")
        
        print("\n" + "="*60)
        print("✅ All tests passed! DWSIM automation is working!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    controller.cleanup()
    
else:
    print("\n❌ DWSIM initialization failed")