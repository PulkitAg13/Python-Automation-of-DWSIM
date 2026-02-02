"""
DWSIM Controller - Python 3.10+ Working Version
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================
# PYTHON 3.10+ FIX - THIS IS CRITICAL
# ============================================
if sys.version_info >= (3, 10):
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    
    # Initialize pythonnet BEFORE importing clr
    import pythonnet
    pythonnet.load()

import clr
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

class DWSIMController:
    """Controller for DWSIM Automation API"""
    
    def __init__(self):
        self.dwsim = None
        self.flowsheet = None
        self.thermo = None
        self._initialized = False
        self._dwsim_path = None
        
    def _find_thermo_class(self):
        """Find the correct thermodynamics class dynamically"""
        try:
            import DWSIM.Thermodynamics as ThermoMod
            
            # Common class names in different DWSIM versions
            possible_names = [
                'PropertyPackage',
                'Thermodynamics',
                'Thermo',
                'ThermoPropertyPackage',
                'PropertyPackages',
                'PP'
            ]
            
            for attr_name in dir(ThermoMod):
                if not attr_name.startswith('_'):
                    attr = getattr(ThermoMod, attr_name)
                    
                    # Check if it looks like a class
                    is_class = False
                    try:
                        if hasattr(attr, '__class__'):
                            class_str = str(attr.__class__)
                            if 'RuntimeType' in class_str or 'Type' in class_str:
                                is_class = True
                    except:
                        pass
                    
                    # Check naming patterns
                    if is_class and any(name in attr_name for name in possible_names):
                        print(f"🔍 Found candidate: {attr_name}")
                        
                        # Try to instantiate and test
                        try:
                            instance = attr()
                            if hasattr(instance, 'ComponentName'):
                                instance.ComponentName = "Test"
                                print(f"✅ Valid thermo class: {attr_name}")
                                return attr
                        except:
                            continue
            
            # If no class found with patterns, try all classes
            print("⚠️ No class found with patterns, trying all classes...")
            for attr_name in dir(ThermoMod):
                if not attr_name.startswith('_'):
                    attr = getattr(ThermoMod, attr_name)
                    try:
                        if 'class' in str(type(attr)).lower():
                            instance = attr()
                            if hasattr(instance, 'ComponentName'):
                                print(f"✅ Found thermo class: {attr_name}")
                                return attr
                    except:
                        continue
            
            raise ImportError("Could not find PropertyPackage class in DWSIM.Thermodynamics")
            
        except Exception as e:
            print(f"❌ Error finding thermo class: {e}")
            raise
    
    def initialize(self, dwsim_path: Optional[str] = None) -> bool:
        """Initialize DWSIM Automation API"""
        try:
            print("=" * 60)
            print("DWSIM Initialization")
            print("=" * 60)
            
            # Get DWSIM path
            if dwsim_path is None:
                dwsim_path = os.getenv('DWSIM_PATH', 'C:\\Program Files\\DWSIM')
            
            dwsim_path = os.path.normpath(dwsim_path)
            self._dwsim_path = dwsim_path
            
            print(f"Python version: {sys.version}")
            print(f"DWSIM path: {dwsim_path}")
            
            # Verify DWSIM installation
            if not os.path.exists(dwsim_path):
                print(f"❌ DWSIM path does not exist: {dwsim_path}")
                return False
            
            # Add DWSIM path to sys.path
            if dwsim_path not in sys.path:
                sys.path.append(dwsim_path)
            
            # Load required assemblies
            print("\n📦 Loading assemblies...")
            
            # Load System first
            clr.AddReference("System")
            print("✅ System assembly loaded")
            
            # Load DWSIM assemblies
            assemblies = [
                "DWSIM.Interfaces",
                "DWSIM.Thermodynamics",
                "DWSIM.SharedClasses",
                "DWSIM.GlobalSettings",
                "DWSIM.UnitOperations"
            ]
            
            for assembly in assemblies:
                try:
                    clr.AddReference(assembly)
                    print(f"✅ {assembly} loaded")
                except Exception as e:
                    print(f"❌ {assembly} failed: {e}")
                    return False
            
            # Import DWSIM types
            print("\n📥 Importing DWSIM types...")
            
            # Import basic types
            from DWSIM.Interfaces import IFlowsheet
            from DWSIM.GlobalSettings import Settings
            from DWSIM.SharedClasses import SystemsOfUnits
            
            print("✅ Basic DWSIM types imported")
            
            # Find and create thermodynamics package
            print("\n🔍 Creating thermodynamics package...")
            ThermoClass = self._find_thermo_class()
            self.thermo = ThermoClass()
            self.thermo.ComponentName = "Raoult's Law"
            print("✅ Thermodynamics package created")
            
            # Create DWSIM instance
            print("\n🚀 Creating DWSIM instance...")
            import System
            
            # Create flowsheet
            self.dwsim = System.Activator.CreateInstance(IFlowsheet)
            
            # Call CreateFlowsheet if method exists
            if hasattr(self.dwsim, 'CreateFlowsheet'):
                self.dwsim.CreateFlowsheet()
                print("✅ Flowsheet created")
            
            # Set thermodynamic package
            if hasattr(self.dwsim.Options, 'PropertyPackage'):
                self.dwsim.Options.PropertyPackage = self.thermo
                print("✅ PropertyPackage set")
            else:
                # Try alternative property names
                for prop_name in ['ThermoPackage', 'ThermodynamicPackage', 'Package']:
                    if hasattr(self.dwsim.Options, prop_name):
                        setattr(self.dwsim.Options, prop_name, self.thermo)
                        print(f"✅ Thermodynamic package set via {prop_name}")
                        break
            
            # Set units
            if hasattr(self.dwsim.Options, 'SelectedUnitSystem'):
                self.dwsim.Options.SelectedUnitSystem = SystemsOfUnits.SI
                print("✅ Unit system set to SI")
            
            self._initialized = True
            print("\n✅ DWSIM initialized successfully!")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    # ============================================
    # REST OF THE METHODS (same as before)
    # ============================================
    
    def create_material_stream(self, name: str, temperature: float = 298.15,
                              pressure: float = 101325, 
                              flow_rate: float = 100.0,
                              composition: Dict[str, float] = None) -> Any:
        """Create a material stream"""
        if not self._initialized:
            raise RuntimeError("DWSIM not initialized")
        
        try:
            import System
            
            # Create stream
            stream_id = System.Guid.NewGuid()
            stream = self.dwsim.AddObject(stream_id, "Material Stream", name, 0, 0)
            
            # Set properties
            stream.SetTemperature(temperature)
            stream.SetPressure(pressure)
            
            # Set composition if provided
            if composition:
                for comp, fraction in composition.items():
                    stream.SetOverallCompoundMoleFraction(comp, fraction)
            
            # Set flow rate
            stream.SetMassFlow(flow_rate)
            
            return stream
            
        except Exception as e:
            print(f"❌ Failed to create stream {name}: {str(e)}")
            raise
    
    def create_reactor_pfr(self, name: str, volume: float = 1.0,
                          temperature: float = 298.15,
                          pressure: float = 101325) -> Any:
        """Create a PFR reactor"""
        if not self._initialized:
            raise RuntimeError("DWSIM not initialized")
        
        try:
            import System
            
            # Create reactor
            reactor_id = System.Guid.NewGuid()
            reactor = self.dwsim.AddObject(reactor_id, "Reactor - PFR", name, 0, 0)
            
            # Set reactor properties
            reactor.Volume = volume
            reactor.Temperature = temperature
            reactor.Pressure = pressure
            
            # Set as isothermal if property exists
            if hasattr(reactor, 'CalcMode'):
                reactor.CalcMode = 0  # Isothermal operation
            
            return reactor
            
        except Exception as e:
            print(f"❌ Failed to create PFR reactor {name}: {str(e)}")
            raise
    
    def create_distillation_column(self, name: str, stages: int = 10,
                                  feed_stage: int = 5,
                                  reflux_ratio: float = 2.0,
                                  distillate_rate: float = 50.0) -> Any:
        """Create a distillation column"""
        if not self._initialized:
            raise RuntimeError("DWSIM not initialized")
        
        try:
            import System
            
            # Create column
            column_id = System.Guid.NewGuid()
            column = self.dwsim.AddObject(column_id, "Distillation Column", name, 0, 0)
            
            # Set column properties
            column.NumberOfStages = stages
            column.FeedStage = feed_stage
            column.RefluxRatio = reflux_ratio
            column.DistillateRate = distillate_rate
            
            # Set convergence parameters if they exist
            if hasattr(column, 'MaxIterations'):
                column.MaxIterations = 100
            if hasattr(column, 'Tolerance'):
                column.Tolerance = 1e-6
            
            return column
            
        except Exception as e:
            print(f"❌ Failed to create distillation column {name}: {str(e)}")
            raise
    
    def connect_streams(self, from_stream: Any, to_unit: Any, port: int = 0):
        """Connect a stream to a unit operation"""
        try:
            self.dwsim.ConnectObjects(from_stream.GraphicObject, to_unit.GraphicObject, port, 0)
            return True
        except Exception as e:
            print(f"❌ Failed to connect streams: {str(e)}")
            return False
    
    def add_reaction(self, reactor: Any, reaction_name: str, 
                    reactants: Dict[str, float],
                    products: Dict[str, float],
                    rate_constant: float = 1.0,
                    activation_energy: float = 50000.0,
                    temperature_dependence: bool = True):
        """Add a reaction to a reactor"""
        try:
            # Check if reactor has ReactionSetID property
            if hasattr(reactor, 'ReactionSetID'):
                if reactor.ReactionSetID is None or reactor.ReactionSetID == "":
                    import System
                    reaction_set_id = System.Guid.NewGuid()
                    reaction_set = self.dwsim.AddObject(reaction_set_id, "Reaction Set", "ReactionSet", 0, 0)
                    reactor.ReactionSetID = reaction_set.Name
            else:
                print("⚠️ Reactor doesn't have ReactionSetID property")
                return False
            
            # Create reaction
            import System
            reaction_id = System.Guid.NewGuid()
            reaction = self.dwsim.AddObject(reaction_id, "Reaction", reaction_name, 0, 0)
            
            # Set reaction properties
            if hasattr(reaction, 'ReactionType'):
                reaction.ReactionType = 0  # Conversion
            
            # Set reactants and products
            if hasattr(reaction, 'Components'):
                for comp, coeff in reactants.items():
                    reaction.Components[comp] = -coeff
                for comp, coeff in products.items():
                    reaction.Components[comp] = coeff
            
            # Set kinetics if properties exist
            if hasattr(reaction, 'BaseReactionRate'):
                reaction.BaseReactionRate = rate_constant
            if hasattr(reaction, 'ActivationEnergy'):
                reaction.ActivationEnergy = activation_energy
            if hasattr(reaction, 'TemperatureDependence'):
                reaction.TemperatureDependence = temperature_dependence
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to add reaction: {str(e)}")
            return False
    
    def solve_flowsheet(self, max_iterations: int = 100, tolerance: float = 1e-6) -> bool:
        """Solve the entire flowsheet"""
        try:
            # Set solver parameters if they exist
            if hasattr(self.dwsim.Options, 'SolverMaxIterations'):
                self.dwsim.Options.SolverMaxIterations = max_iterations
            if hasattr(self.dwsim.Options, 'SolverTolerance'):
                self.dwsim.Options.SolverTolerance = tolerance
            
            # Solve flowsheet
            start_time = time.time()
            success = self.dwsim.SolveFlowsheet()
            solve_time = time.time() - start_time
            
            if success:
                print(f"✅ Flowsheet solved in {solve_time:.2f} seconds")
            else:
                print(f"❌ Flowsheet solution failed")
                
            return success
            
        except Exception as e:
            print(f"❌ Failed to solve flowsheet: {str(e)}")
            return False
    
    def get_stream_results(self, stream: Any) -> Dict[str, Any]:
        """Get results from a material stream"""
        try:
            results = {
                'temperature': 0,
                'pressure': 0,
                'mass_flow': 0,
                'molar_flow': 0,
                'composition': {}
            }
            
            # Try to get properties
            if hasattr(stream, 'GetTemperature'):
                results['temperature'] = stream.GetTemperature()
            if hasattr(stream, 'GetPressure'):
                results['pressure'] = stream.GetPressure()
            if hasattr(stream, 'GetMassFlow'):
                results['mass_flow'] = stream.GetMassFlow()
            if hasattr(stream, 'GetMolarFlow'):
                results['molar_flow'] = stream.GetMolarFlow()
            
            # Get composition
            try:
                if hasattr(stream, 'Phases') and len(stream.Phases) > 0:
                    if hasattr(stream.Phases[0], 'Compounds'):
                        for comp in stream.Phases[0].Compounds.Keys:
                            results['composition'][comp] = stream.GetOverallCompoundMoleFraction(comp)
            except:
                pass
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to get stream results: {str(e)}")
            return {}
    
    def get_reactor_results(self, reactor: Any) -> Dict[str, Any]:
        """Get results from a reactor"""
        try:
            results = {
                'conversion': 0,
                'outlet_temperature': 0,
                'heat_duty': 0,
                'outlet_pressure': 0
            }
            
            # Try to get properties if they exist
            if hasattr(reactor, 'Conversion'):
                results['conversion'] = reactor.Conversion
            if hasattr(reactor, 'OutletTemperature'):
                results['outlet_temperature'] = reactor.OutletTemperature
            if hasattr(reactor, 'DeltaQ'):
                results['heat_duty'] = reactor.DeltaQ
            if hasattr(reactor, 'OutletPressure'):
                results['outlet_pressure'] = reactor.OutletPressure
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to get reactor results: {str(e)}")
            return {}
    
    def get_column_results(self, column: Any) -> Dict[str, Any]:
        """Get results from a distillation column"""
        try:
            results = {
                'condenser_duty': 0,
                'reboiler_duty': 0,
                'distillate_purity': 0,
                'bottoms_purity': 0,
                'reflux_ratio': 0,
                'converged': False
            }
            
            # Try to get properties if they exist
            if hasattr(column, 'CondenserDuty'):
                results['condenser_duty'] = column.CondenserDuty
            if hasattr(column, 'ReboilerDuty'):
                results['reboiler_duty'] = column.ReboilerDuty
            if hasattr(column, 'DistillatePurity'):
                results['distillate_purity'] = column.DistillatePurity
            if hasattr(column, 'BottomsPurity'):
                results['bottoms_purity'] = column.BottomsPurity
            if hasattr(column, 'RefluxRatio'):
                results['reflux_ratio'] = column.RefluxRatio
            if hasattr(column, 'Converged'):
                results['converged'] = column.Converged
            
            return results
            
        except Exception as e:
            print(f"❌ Failed to get column results: {str(e)}")
            return {}
    
    def cleanup(self):
        """Cleanup resources"""
        if self.dwsim:
            try:
                self.dwsim.Close()
                print("✅ DWSIM cleaned up successfully")
            except:
                pass
        
        self._initialized = False
    
    def is_initialized(self) -> bool:
        """Check if DWSIM is initialized"""
        return self._initialized
    
    def get_dwsim_path(self) -> str:
        """Get the DWSIM installation path"""
        return self._dwsim_path