"""
PFR (Plug Flow Reactor) Simulator
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import time
from datetime import datetime

class PFRSimulator:
    """Simulator for Plug Flow Reactor"""
    
    def __init__(self, controller):
        self.controller = controller
        self.results = []
        
    def create_base_flowsheet(self, config: Dict) -> Tuple[Any, Any, Any]:
        """Create base PFR flowsheet"""
        # Extract configuration
        reactor_config = config.get('reactor', {})
        feed_config = config.get('feed', {})
        reaction_config = config.get('reaction', {})
        
        # Create feed stream
        feed_stream = self.controller.create_material_stream(
            name="Feed",
            temperature=feed_config.get('temperature', 300.0),
            pressure=feed_config.get('pressure', 101325),
            flow_rate=feed_config.get('flow_rate', 100.0),
            composition=feed_config.get('composition', {'A': 1.0, 'B': 0.0})
        )
        
        # Create PFR reactor
        reactor = self.controller.create_reactor_pfr(
            name="PFR_Reactor",
            volume=reactor_config.get('volume', 1.0),
            temperature=reactor_config.get('temperature', 350.0),
            pressure=reactor_config.get('pressure', 101325)
        )
        
        # Create product stream
        product_stream = self.controller.create_material_stream(
            name="Product",
            temperature=reactor_config.get('temperature', 350.0),
            pressure=reactor_config.get('pressure', 101325)
        )
        
        # Connect streams
        self.controller.connect_streams(feed_stream, reactor, 0)
        self.controller.connect_streams(reactor, product_stream, 0)
        
        # Add reaction if specified
        if reaction_config:
            self.controller.add_reaction(
                reactor=reactor,
                reaction_name="A_to_B",
                reactants={'A': 1.0},
                products={'B': 1.0},
                rate_constant=reaction_config.get('rate_constant', 0.1),
                activation_energy=reaction_config.get('activation_energy', 50000.0)
            )
        
        return feed_stream, reactor, product_stream
    
    def run_base_case(self, config: Dict) -> Dict[str, Any]:
        """Run base case PFR simulation"""
        print("Running PFR base case simulation...")
        
        try:
            # Create flowsheet
            feed_stream, reactor, product_stream = self.create_base_flowsheet(config)
            
            # Solve flowsheet
            start_time = time.time()
            success = self.controller.solve_flowsheet()
            solve_time = time.time() - start_time
            
            if not success:
                return {
                    'success': False,
                    'error': 'Flowsheet solution failed',
                    'solve_time': solve_time
                }
            
            # Get results
            feed_results = self.controller.get_stream_results(feed_stream)
            product_results = self.controller.get_stream_results(product_stream)
            reactor_results = self.controller.get_reactor_results(reactor)
            
            # Calculate conversion
            if 'A' in feed_results['composition'] and 'A' in product_results['composition']:
                feed_A = feed_results['composition']['A'] * feed_results['molar_flow']
                product_A = product_results['composition']['A'] * product_results['molar_flow']
                conversion = ((feed_A - product_A) / feed_A * 100) if feed_A > 0 else 0
            else:
                conversion = reactor_results.get('conversion', 0) * 100
            
            # Calculate B production rate
            if 'B' in product_results['composition']:
                b_production = product_results['composition']['B'] * product_results['molar_flow']
            else:
                b_production = 0
            
            results = {
                'success': True,
                'case_type': 'base_case',
                'timestamp': datetime.now().isoformat(),
                'solve_time': solve_time,
                'conversion_percent': conversion,
                'b_production_rate': b_production,
                'outlet_temperature': reactor_results.get('outlet_temperature', 0),
                'heat_duty': reactor_results.get('heat_duty', 0),
                'reactor_volume': config.get('reactor', {}).get('volume', 1.0),
                'reactor_temperature': config.get('reactor', {}).get('temperature', 350.0),
                'feed_flow_rate': config.get('feed', {}).get('flow_rate', 100.0),
                'feed_composition': config.get('feed', {}).get('composition', {}),
                'feed_results': feed_results,
                'product_results': product_results,
                'reactor_results': reactor_results
            }
            
            print(f"✅ PFR base case completed: {conversion:.2f}% conversion")
            return results
            
        except Exception as e:
            print(f"❌ PFR base case failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'case_type': 'base_case',
                'timestamp': datetime.now().isoformat()
            }
    
    def run_parametric_sweep(self, sweep_config: Dict, 
                            variables: List[str] = None) -> List[Dict[str, Any]]:
        """Run parametric sweep for PFR"""
        if variables is None:
            variables = ['temperature', 'volume']
        
        all_results = []
        
        # Define sweep ranges
        if 'temperature' in variables:
            temp_range = sweep_config.get('temperature', {'min': 300, 'max': 400, 'steps': 5})
            temperatures = np.linspace(temp_range['min'], temp_range['max'], temp_range['steps'])
        else:
            temperatures = [350.0]
        
        if 'volume' in variables:
            vol_range = sweep_config.get('volume', {'min': 0.5, 'max': 5.0, 'steps': 5})
            volumes = np.linspace(vol_range['min'], vol_range['max'], vol_range['steps'])
        else:
            volumes = [1.0]
        
        # Run sweep
        total_cases = len(temperatures) * len(volumes)
        case_count = 0
        
        print(f"Running PFR parametric sweep: {total_cases} cases")
        
        for temp in temperatures:
            for vol in volumes:
                case_count += 1
                print(f"Case {case_count}/{total_cases}: T={temp:.1f}K, V={vol:.2f}m³")
                
                # Modify configuration
                config = {
                    'reactor': {
                        'temperature': float(temp),
                        'volume': float(vol),
                        'pressure': 101325
                    },
                    'feed': {
                        'temperature': 300.0,
                        'pressure': 101325,
                        'flow_rate': 100.0,
                        'composition': {'A': 1.0, 'B': 0.0}
                    },
                    'reaction': {
                        'rate_constant': 0.1,
                        'activation_energy': 50000.0
                    }
                }
                
                # Run simulation
                try:
                    # Reinitialize controller for each case
                    if not self.controller.is_initialized():
                        self.controller.initialize()
                    
                    result = self.run_base_case(config)
                    
                    # Add sweep parameters
                    result['sweep_parameters'] = {
                        'temperature': float(temp),
                        'volume': float(vol)
                    }
                    
                    all_results.append(result)
                    
                except Exception as e:
                    print(f"❌ Case failed: {str(e)}")
                    all_results.append({
                        'success': False,
                        'error': str(e),
                        'sweep_parameters': {
                            'temperature': float(temp),
                            'volume': float(vol)
                        },
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"✅ PFR parametric sweep completed: {len(all_results)} cases")
        return all_results
    
    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze PFR simulation results"""
        if not results:
            return {}
        
        # Filter successful results
        successful_results = [r for r in results if r.get('success', False)]
        
        if not successful_results:
            return {'error': 'No successful simulations'}
        
        # Calculate statistics
        conversions = [r.get('conversion_percent', 0) for r in successful_results]
        b_productions = [r.get('b_production_rate', 0) for r in successful_results]
        
        analysis = {
            'total_cases': len(results),
            'successful_cases': len(successful_results),
            'success_rate': len(successful_results) / len(results) * 100,
            'conversion_stats': {
                'min': min(conversions) if conversions else 0,
                'max': max(conversions) if conversions else 0,
                'mean': np.mean(conversions) if conversions else 0,
                'std': np.std(conversions) if conversions else 0
            },
            'production_stats': {
                'min': min(b_productions) if b_productions else 0,
                'max': max(b_productions) if b_productions else 0,
                'mean': np.mean(b_productions) if b_productions else 0
            },
            'optimal_conditions': self.find_optimal_conditions(successful_results)
        }
        
        return analysis
    
    def find_optimal_conditions(self, results: List[Dict]) -> Dict[str, Any]:
        """Find optimal conditions from results"""
        if not results:
            return {}
        
        # Find maximum conversion
        max_conv_result = max(results, key=lambda x: x.get('conversion_percent', 0))
        
        # Find maximum B production
        max_prod_result = max(results, key=lambda x: x.get('b_production_rate', 0))
        
        return {
            'max_conversion': {
                'conversion': max_conv_result.get('conversion_percent', 0),
                'temperature': max_conv_result.get('reactor_temperature', 0),
                'volume': max_conv_result.get('reactor_volume', 0),
                'b_production': max_conv_result.get('b_production_rate', 0)
            },
            'max_production': {
                'b_production': max_prod_result.get('b_production_rate', 0),
                'conversion': max_prod_result.get('conversion_percent', 0),
                'temperature': max_prod_result.get('reactor_temperature', 0),
                'volume': max_prod_result.get('reactor_volume', 0)
            }
        }