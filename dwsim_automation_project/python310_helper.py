"""
Helper functions for Python 3.10 imports
"""

import sys
import clr

class Python310Importer:
    """Helper class for Python 3.10 imports"""
    
    @staticmethod
    def load_system_assembly():
        """Load System assembly for Python 3.10"""
        try:
            clr.AddReference("System")
            return True
        except Exception as e:
            print(f"❌ Failed to load System: {e}")
            return False
    
    @staticmethod
    def get_system_type(type_name):
        """Get a System type dynamically"""
        try:
            import System
            return getattr(System, type_name)
        except Exception as e:
            print(f"❌ Failed to get System.{type_name}: {e}")
            raise
    
    @staticmethod
    def test_imports():
        """Test all imports work"""
        print("Testing Python 3.10 imports...")
        
        # Load System
        if not Python310Importer.load_system_assembly():
            return False
        
        # Test common types
        types_to_test = ["Guid", "String", "Activator", "Console"]
        
        for type_name in types_to_test:
            try:
                type_obj = Python310Importer.get_system_type(type_name)
                print(f"✅ System.{type_name} loaded")
                
                # Test Guid creation
                if type_name == "Guid":
                    guid = type_obj.NewGuid()
                    print(f"   Created Guid: {guid}")
                
            except Exception as e:
                print(f"❌ System.{type_name} failed: {e}")
        
        return True

# Usage example:
if __name__ == "__main__":
    if Python310Importer.test_imports():
        print("\n✅ Python 3.10 imports work!")
    else:
        print("\n❌ Python 3.10 imports failed")