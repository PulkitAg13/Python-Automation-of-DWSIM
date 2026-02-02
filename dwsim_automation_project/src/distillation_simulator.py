"""
Distillation Column Simulator
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import time
from datetime import datetime

class DistillationSimulator:
    """Simulator for Distillation Column"""
    
    def __init__(self, controller):
        self.controller = controller
        self.results = []
    
    def create_base_flowsheet(self, config: Dict) -> Tuple[Any, Any, Any, Any]:
        """Create base distillation flowsheet"""
        # Extract configuration
        column_config = config.get('column', {})
        feed_config = config.get('feed', {})
        
        # Create feed stream (binary mixture A:B = 50:50)
        feed_composition = feed_config.get('composition', {'A': 0.5, 'B': 0.5})
        feed_stream = self.controller.create_material_stream(
            name="Feed",
            temperature=feed_config.get('temperature', 350.0),
            pressure=feed_config.get('pressure', 101325),
            flow_rate=feed_config.get('flow_rate', 100.0),
            composition=feed_composition
        )
        
        # Create distillation column
        column = self.controller.create_distillation_column(
            name="Distillation_Column",
            stages=column_config.get('stages', 10),
            feed_stage=column_config.get('feed_stage', 5),
            reflux_ratio=column_config.get('reflux_ratio', 2.0),
            distillate_rate=column_config.get('distillate_rate', 50.0)
        )
        
        # Create distillate stream
        distillate_stream = self.controller.create_material_stream(
            name="Distillate",
            temperature=350.0,
            pressure=101325
        )
        
        # Create bottoms stream
        bottoms_stream = self.controller.create_material_stream(
            name="Bottoms",
            temperature=350.0,
            pressure=101325
        )
        
        # Connect streams
        self.controller.connect_streams(feed_stream, column, 0)  # Feed
        self.controller.connect_streams(column, distillate_stream, 0)  # Distillate
        self.controller.connect_streams(column, bottoms_stream, 1)  # Bottoms
        
        return feed_stream, column, distillate_stream, bottoms_stream
    
    def run_base_case(self, config: Dict) -> Dict[str, Any]:
        """Run base case distillation simulation"""
        print("Running distillation base case simulation...")
        
        try:
            # Create flowsheet
            feed_stream, column, distillate_stream, bottoms_stream = self.create_base_flowsheet(config)
            
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
            distillate_results = self.controller.get_stream_results(distillate_stream)
            bottoms_results = self.controller.get_stream_results(bottoms_stream)
            column_results = self.controller.get_column_results(column)
            
            # Calculate purities
            if 'A' in distillate_results['composition']:
                distillate_purity_A = distillate_results['composition']['A'] * 100
            else:
                distillate_purity_A = 0
            
            if 'B' in bottoms_results['composition']:
                bottoms_purity_B = bottoms_results['composition']['B'] * 100
            else:
                bottoms_purity_B = 0
            
            # Calculate energy consumption
            condenser_duty = column_results.get('condenser_duty', 0)
            reboiler_duty = column_results.get('reboiler_duty', 0)
            total_energy = abs(condenser_duty) + abs(reboiler_duty)
            
            results = {
                'success': True,
                'case_type': 'base_case',
                'timestamp': datetime.now().isoformat(),
                'solve_time': solve_time,
                'distillate_purity_A': distillate_purity_A,
                'bottoms_purity_B': bottoms_purity_B,
                'condenser_duty': condenser_duty,
                'reboiler_duty': reboiler_duty,
                'total_energy': total_energy,
                'converged': column_results.get('converged', False),
                'column_stages': config.get('column', {}).get('stages', 10),
                'feed_stage': config.get('column', {}).get('feed_stage', 5),
                'reflux_ratio': config.get('column', {}).get('reflux_ratio', 2.0),
                'distillate_rate': config.get('column', {}).get('distillate_rate', 50.0),
                'feed_composition': config.get('feed', {}).get('composition', {'A': 0.5, 'B': 0.5}),
                'feed_results': feed_results,
                'distillate_results': distillate_results,
                'bottoms_results': bottoms_results,
                'column_results': column_results
            }
            
            print(f"✅ Distillation base case completed: "
                  f"Distillate A={distillate_purity_A:.2f}%, "
                  f"Bottoms B={bottoms_purity_B:.2f}%")
            return results
            
        except Exception as e:
            print(f"❌ Distillation base case failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'case_type': 'base_case',
                'timestamp': datetime.now().isoformat()
            }
    
    def run_parametric_sweep(self, sweep_config: Dict,
                            variables: List[str] = None) -> List[Dict[str, Any]]:
        """Run parametric sweep for distillation column"""
        if variables is None:
            variables = ['reflux_ratio', 'stages']
        
        all_results = []
        
        # Define sweep ranges
        if 'reflux_ratio' in variables:
            rr_range = sweep_config.get('reflux_ratio', {'min': 1.0, 'max': 5.0, 'steps': 5})
            reflux_ratios = np.linspace(rr_range['min'], rr_range['max'], rr_range['steps'])
        else:
            reflux_ratios = [2.0]
        
        if 'stages' in variables:
            stages_range = sweep_config.get('stages', {'min': 5, 'max': 20, 'steps': 4})
            stages_list = np.linspace(stages_range['min'], stages_range['max'], 
                                     stages_range['steps'], dtype=int)
        else:
            stages_list = [10]
        
        # Run sweep
        total_cases = len(reflux_ratios) * len(stages_list)
        case_count = 0
        
        print(f"Running distillation parametric sweep: {total_cases} cases")
        
        for rr in reflux_ratios:
            for stages in stages_list:
                case_count += 1
                print(f"Case {case_count}/{total_cases}: RR={rr:.2f}, Stages={stages}")
                
                # Modify configuration
                config = {
                    'column': {
                        'stages': int(stages),
                        'feed_stage': max(2, int(stages // 2)),  # Middle stage
                        'reflux_ratio': float(rr),
                        'distillate_rate': 50.0
                    },
                    'feed': {
                        'temperature': 350.0,
                        'pressure': 101325,
                        'flow_rate': 100.0,
                        'composition': {'A': 0.5, 'B': 0.5}
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
                        'reflux_ratio': float(rr),
                        'stages': int(stages)
                    }
                    
                    all_results.append(result)
                    
                except Exception as e:
                    print(f"❌ Case failed: {str(e)}")
                    all_results.append({
                        'success': False,
                        'error': str(e),
                        'sweep_parameters': {
                            'reflux_ratio': float(rr),
                            'stages': int(stages)
                        },
                        'timestamp': datetime.now().isoformat()
                    })
        
        print(f"✅ Distillation parametric sweep completed: {len(all_results)} cases")
        return all_results
    
    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze distillation simulation results"""
        if not results:
            return {}
        
        # Filter successful results
        successful_results = [r for r in results if r.get('success', False) and r.get('converged', False)]
        
        if not successful_results:
            return {'error': 'No successful converged simulations'}
        
        # Calculate statistics
        distillate_purities = [r.get('distillate_purity_A', 0) for r in successful_results]
        bottoms_purities = [r.get('bottoms_purity_B', 0) for r in successful_results]
        total_energies = [r.get('total_energy', 0) for r in successful_results]
        
        analysis = {
            'total_cases': len(results),
            'successful_cases': len(successful_results),
            'success_rate': len(successful_results) / len(results) * 100,
            'distillate_purity_stats': {
                'min': min(distillate_purities) if distillate_purities else 0,
                'max': max(distillate_purities) if distillate_purities else 0,
                'mean': np.mean(distillate_purities) if distillate_purities else 0,
                'std': np.std(distillate_purities) if distillate_purities else 0
            },
            'bottoms_purity_stats': {
                'min': min(bottoms_purities) if bottoms_purities else 0,
                'max': max(bottoms_purities) if bottoms_purities else 0,
                'mean': np.mean(bottoms_purities) if bottoms_purities else 0
            },
            'energy_stats': {
                'min': min(total_energies) if total_energies else 0,
                'max': max(total_energies) if total_energies else 0,
                'mean': np.mean(total_energies) if total_energies else 0
            },
            'optimal_conditions': self.find_optimal_conditions(successful_results)
        }
        
        return analysis
    
    def find_optimal_conditions(self, results: List[Dict]) -> Dict[str, Any]:
        """Find optimal conditions from results"""
        if not results:
            return {}
        
        # Find maximum distillate purity
        max_dist_purity_result = max(results, key=lambda x: x.get('distillate_purity_A', 0))
        
        # Find maximum bottoms purity
        max_bot_purity_result = max(results, key=lambda x: x.get('bottoms_purity_B', 0))
        
        # Find minimum energy consumption
        min_energy_result = min(results, key=lambda x: x.get('total_energy', float('inf')))
        
        return {
            'max_distillate_purity': {
                'purity': max_dist_purity_result.get('distillate_purity_A', 0),
                'reflux_ratio': max_dist_purity_result.get('reflux_ratio', 0),
                'stages': max_dist_purity_result.get('column_stages', 0),
                'energy': max_dist_purity_result.get('total_energy', 0)
            },
            'max_bottoms_purity': {
                'purity': max_bot_purity_result.get('bottoms_purity_B', 0),
                'reflux_ratio': max_bot_purity_result.get('reflux_ratio', 0),
                'stages': max_bot_purity_result.get('column_stages', 0),
                'energy': max_bot_purity_result.get('total_energy', 0)
            },
            'min_energy': {
                'energy': min_energy_result.get('total_energy', 0),
                'distillate_purity': min_energy_result.get('distillate_purity_A', 0),
                'bottoms_purity': min_energy_result.get('bottoms_purity_B', 0),
                'reflux_ratio': min_energy_result.get('reflux_ratio', 0),
                'stages': min_energy_result.get('column_stages', 0)
            }
        }