"""
Advanced Parametric Study Module
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from joblib import Parallel, delayed
import os

class ParametricStudy:
    """Advanced parametric study with parallel processing"""
    
    def __init__(self, controller_factory):
        self.controller_factory = controller_factory
        self.results = []
        
    def create_parameter_grid(self, ranges: Dict[str, Dict], method: str = 'linear') -> List[Dict]:
        """Create parameter grid for sweep"""
        param_grid = []
        
        if method == 'linear':
            # Create linear grid
            param_names = list(ranges.keys())
            
            # Generate all combinations
            if len(param_names) == 1:
                param = param_names[0]
                rng = ranges[param]
                values = np.linspace(rng['min'], rng['max'], rng['steps'])
                for val in values:
                    param_grid.append({param: float(val)})
                    
            elif len(param_names) == 2:
                param1, param2 = param_names[0], param_names[1]
                rng1, rng2 = ranges[param1], ranges[param2]
                values1 = np.linspace(rng1['min'], rng1['max'], rng1['steps'])
                values2 = np.linspace(rng2['min'], rng2['max'], rng2['steps'])
                
                for val1 in values1:
                    for val2 in values2:
                        param_grid.append({
                            param1: float(val1),
                            param2: float(val2)
                        })
        
        return param_grid
    
    def run_single_case(self, case_config: Dict, case_type: str = 'pfr') -> Dict[str, Any]:
        """Run a single simulation case"""
        try:
            # Create controller
            controller = self.controller_factory()
            if not controller.initialize():
                return {
                    'success': False,
                    'error': 'Controller initialization failed',
                    'parameters': case_config,
                    'case_type': case_type,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Run simulation based on type
            if case_type == 'pfr':
                from src.pfr_simulator import PFRSimulator
                simulator = PFRSimulator(controller)
                result = simulator.run_base_case(case_config)
            elif case_type == 'distillation':
                from src.distillation_simulator import DistillationSimulator
                simulator = DistillationSimulator(controller)
                result = simulator.run_base_case(case_config)
            else:
                return {
                    'success': False,
                    'error': f'Unknown case type: {case_type}',
                    'parameters': case_config
                }
            
            # Add parameters to result
            result['parameters'] = case_config
            result['case_type'] = case_type
            
            # Cleanup
            controller.cleanup()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'parameters': case_config,
                'case_type': case_type,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_comprehensive_sweep(self, config: Dict, parallel: bool = False, 
                               max_workers: int = None) -> Dict[str, Any]:
        """Run comprehensive parametric sweep"""
        print("Starting comprehensive parametric sweep...")
        
        all_results = {
            'pfr': [],
            'distillation': []
        }
        
        # Get configurations
        pfr_config = config.get('pfr', {})
        dist_config = config.get('distillation', {})
        
        # Generate parameter grids
        pfr_params = self.create_parameter_grid(
            pfr_config.get('ranges', {}),
            method=pfr_config.get('method', 'linear')
        )
        
        dist_params = self.create_parameter_grid(
            dist_config.get('ranges', {}),
            method=dist_config.get('method', 'linear')
        )
        
        # Prepare cases
        pfr_cases = []
        for params in pfr_params:
            case_config = {
                'reactor': {
                    'temperature': params.get('temperature', 350.0),
                    'volume': params.get('volume', 1.0),
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
            pfr_cases.append(case_config)
        
        dist_cases = []
        for params in dist_params:
            stages = params.get('stages', 10)
            case_config = {
                'column': {
                    'stages': int(stages),
                    'feed_stage': max(2, int(stages // 2)),
                    'reflux_ratio': params.get('reflux_ratio', 2.0),
                    'distillate_rate': 50.0
                },
                'feed': {
                    'temperature': 350.0,
                    'pressure': 101325,
                    'flow_rate': 100.0,
                    'composition': {'A': 0.5, 'B': 0.5}
                }
            }
            dist_cases.append(case_config)
        
        # Run simulations
        if parallel:
            # Determine number of workers
            if max_workers is None:
                max_workers = min(os.cpu_count(), 4)
            
            print(f"Running in parallel with {max_workers} workers")
            
            # Run PFR cases in parallel
            pfr_results = Parallel(n_jobs=max_workers)(
                delayed(self.run_single_case)(case, 'pfr')
                for case in pfr_cases
            )
            
            # Run distillation cases in parallel
            dist_results = Parallel(n_jobs=max_workers)(
                delayed(self.run_single_case)(case, 'distillation')
                for case in dist_cases
            )
            
            all_results['pfr'] = pfr_results
            all_results['distillation'] = dist_results
            
        else:
            # Run sequentially
            print("Running sequentially...")
            
            # Run PFR cases
            for i, case in enumerate(pfr_cases):
                print(f"PFR Case {i+1}/{len(pfr_cases)}")
                result = self.run_single_case(case, 'pfr')
                all_results['pfr'].append(result)
            
            # Run distillation cases
            for i, case in enumerate(dist_cases):
                print(f"Distillation Case {i+1}/{len(dist_cases)}")
                result = self.run_single_case(case, 'distillation')
                all_results['distillation'].append(result)
        
        # Analyze results
        analysis = self.analyze_all_results(all_results)
        all_results['analysis'] = analysis
        
        print(f"✅ Comprehensive sweep completed")
        print(f"   PFR cases: {len(all_results['pfr'])}")
        print(f"   Distillation cases: {len(all_results['distillation'])}")
        
        return all_results
    
    def analyze_all_results(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Analyze all simulation results"""
        analysis = {}
        
        # Analyze PFR results
        if results['pfr']:
            from src.pfr_simulator import PFRSimulator
            pfr_simulator = PFRSimulator(None)
            pfr_successful = [r for r in results['pfr'] if r.get('success', False)]
            analysis['pfr'] = pfr_simulator.analyze_results(pfr_successful)
        
        # Analyze distillation results
        if results['distillation']:
            from src.distillation_simulator import DistillationSimulator
            dist_simulator = DistillationSimulator(None)
            dist_successful = [r for r in results['distillation'] if r.get('success', False) and r.get('converged', False)]
            analysis['distillation'] = dist_simulator.analyze_results(dist_successful)
        
        # Overall statistics
        total_cases = len(results['pfr']) + len(results['distillation'])
        successful_cases = len([r for r in results['pfr'] if r.get('success', False)]) + \
                          len([r for r in results['distillation'] if r.get('success', False) and r.get('converged', False)])
        
        analysis['overall'] = {
            'total_cases': total_cases,
            'successful_cases': successful_cases,
            'success_rate': (successful_cases / total_cases * 100) if total_cases > 0 else 0
        }
        
        return analysis
    
    def generate_response_surfaces(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Generate response surfaces from parametric study"""
        surfaces = {}
        
        # Generate PFR response surface
        if results['pfr']:
            pfr_successful = [r for r in results['pfr'] if r.get('success', False)]
            if len(pfr_successful) >= 4:
                surfaces['pfr_conversion'] = self._create_surface_data(
                    pfr_successful,
                    x_param='temperature',
                    y_param='volume',
                    z_param='conversion_percent'
                )
                surfaces['pfr_production'] = self._create_surface_data(
                    pfr_successful,
                    x_param='temperature',
                    y_param='volume',
                    z_param='b_production_rate'
                )
        
        # Generate distillation response surface
        if results['distillation']:
            dist_successful = [r for r in results['distillation'] if r.get('success', False) and r.get('converged', False)]
            if len(dist_successful) >= 4:
                surfaces['dist_purity'] = self._create_surface_data(
                    dist_successful,
                    x_param='reflux_ratio',
                    y_param='stages',
                    z_param='distillate_purity_A'
                )
                surfaces['dist_energy'] = self._create_surface_data(
                    dist_successful,
                    x_param='reflux_ratio',
                    y_param='stages',
                    z_param='total_energy'
                )
        
        return surfaces
    
    def _create_surface_data(self, results: List[Dict], x_param: str, 
                            y_param: str, z_param: str) -> Dict[str, Any]:
        """Create surface data for 3D plotting"""
        try:
            # Extract data
            x_data = []
            y_data = []
            z_data = []
            
            for result in results:
                if z_param in result:
                    # Get x parameter
                    if 'parameters' in result and x_param in result['parameters'].get('reactor', {}):
                        x_val = result['parameters']['reactor'][x_param]
                    elif 'parameters' in result and x_param in result['parameters'].get('column', {}):
                        x_val = result['parameters']['column'][x_param]
                    else:
                        x_val = result.get(x_param, 0)
                    
                    # Get y parameter
                    if 'parameters' in result and y_param in result['parameters'].get('reactor', {}):
                        y_val = result['parameters']['reactor'][y_param]
                    elif 'parameters' in result and y_param in result['parameters'].get('column', {}):
                        y_val = result['parameters']['column'][y_param]
                    else:
                        y_val = result.get(y_param, 0)
                    
                    # Get z value
                    z_val = result[z_param]
                    
                    x_data.append(x_val)
                    y_data.append(y_val)
                    z_data.append(z_val)
            
            if len(x_data) < 4:
                return {}
            
            return {
                'x': x_data,
                'y': y_data,
                'z': z_data,
                'x_label': x_param,
                'y_label': y_param,
                'z_label': z_param
            }
            
        except Exception as e:
            print(f"Error creating surface data: {str(e)}")
            return {}
    
    def export_to_dataframe(self, results: Dict[str, List]) -> Dict[str, pd.DataFrame]:
        """Export results to pandas DataFrames"""
        dfs = {}
        
        # Create PFR DataFrame
        pfr_data = []
        for result in results['pfr']:
            row = {
                'case_type': 'pfr',
                'success': result.get('success', False),
                'conversion_percent': result.get('conversion_percent', 0),
                'b_production_rate': result.get('b_production_rate', 0),
                'outlet_temperature': result.get('outlet_temperature', 0),
                'heat_duty': result.get('heat_duty', 0),
                'solve_time': result.get('solve_time', 0)
            }
            
            # Add parameters
            if 'parameters' in result:
                if 'reactor' in result['parameters']:
                    row.update({f'reactor_{k}': v for k, v in result['parameters']['reactor'].items()})
                if 'feed' in result['parameters']:
                    row.update({f'feed_{k}': v for k, v in result['parameters']['feed'].items()})
            
            pfr_data.append(row)
        
        if pfr_data:
            dfs['pfr'] = pd.DataFrame(pfr_data)
        
        # Create distillation DataFrame
        dist_data = []
        for result in results['distillation']:
            row = {
                'case_type': 'distillation',
                'success': result.get('success', False),
                'converged': result.get('converged', False),
                'distillate_purity_A': result.get('distillate_purity_A', 0),
                'bottoms_purity_B': result.get('bottoms_purity_B', 0),
                'condenser_duty': result.get('condenser_duty', 0),
                'reboiler_duty': result.get('reboiler_duty', 0),
                'total_energy': result.get('total_energy', 0),
                'solve_time': result.get('solve_time', 0)
            }
            
            # Add parameters
            if 'parameters' in result:
                if 'column' in result['parameters']:
                    row.update({f'column_{k}': v for k, v in result['parameters']['column'].items()})
                if 'feed' in result['parameters']:
                    row.update({f'feed_{k}': v for k, v in result['parameters']['feed'].items()})
            
            dist_data.append(row)
        
        if dist_data:
            dfs['distillation'] = pd.DataFrame(dist_data)
        
        return dfs