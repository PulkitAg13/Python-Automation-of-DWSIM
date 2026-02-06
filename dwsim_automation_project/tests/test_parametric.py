"""
Unit tests for Parametric study
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parametric_study import ParametricStudy
from utils.validation import validate_config

class MockControllerFactory:
    """Mock controller factory for testing"""
    
    def __init__(self):
        self.call_count = 0
    
    def __call__(self):
        self.call_count += 1
        return MockController()

class MockController:
    """Mock controller for testing"""
    
    def __init__(self):
        self.initialized = False
    
    def initialize(self):
        self.initialized = True
        return True
    
    def is_initialized(self):
        return self.initialized
    
    def cleanup(self):
        self.initialized = False

class TestParametricStudy(unittest.TestCase):
    """Test cases for ParametricStudy"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.controller_factory = MockControllerFactory()
        self.study = ParametricStudy(self.controller_factory)
        
        # Test configuration
        self.test_config = {
            'pfr': {
                'ranges': {
                    'temperature': {'min': 300, 'max': 400, 'steps': 3},
                    'volume': {'min': 0.5, 'max': 2.0, 'steps': 2}
                },
                'method': 'linear'
            },
            'distillation': {
                'ranges': {
                    'reflux_ratio': {'min': 1.0, 'max': 5.0, 'steps': 3},
                    'stages': {'min': 5, 'max': 15, 'steps': 3}
                },
                'method': 'linear'
            }
        }
    
    def test_initialization(self):
        """Test study initialization"""
        self.assertIsNotNone(self.study)
        self.assertIsInstance(self.study, ParametricStudy)
    
    def test_config_validation(self):
        """Test configuration validation"""
        valid, errors = validate_config(self.test_config, 'sweep')
        self.assertTrue(valid, f"Config validation failed: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_invalid_sweep_config(self):
        """Test invalid sweep configuration"""
        invalid_config = {
            'pfr': {
                'ranges': {
                    'temperature': {'min': 400, 'max': 300, 'steps': 3},  # min > max
                    'volume': {'min': 0.5, 'max': 2.0, 'steps': 2}
                }
            }
        }
        
        valid, errors = validate_config(invalid_config, 'sweep')
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_parameter_grid_creation(self):
        """Test parameter grid creation"""
        ranges = {
            'temperature': {'min': 300, 'max': 400, 'steps': 3},
            'volume': {'min': 0.5, 'max': 2.0, 'steps': 2}
        }
        
        grid = self.study.create_parameter_grid(ranges, method='linear')
        self.assertIsNotNone(grid)
        self.assertIsInstance(grid, list)
        
        # Calculate expected number of combinations
        expected_combinations = 3 * 2  # 3 temperature steps × 2 volume steps
        self.assertEqual(len(grid), expected_combinations)
        
        # Check first grid point
        if grid:
            first_point = grid[0]
            self.assertIn('temperature', first_point)
            self.assertIn('volume', first_point)
    
    def test_single_parameter_grid(self):
        """Test grid creation with single parameter"""
        ranges = {
            'temperature': {'min': 300, 'max': 400, 'steps': 5}
        }
        
        grid = self.study.create_parameter_grid(ranges, method='linear')
        self.assertEqual(len(grid), 5)
        
        for point in grid:
            self.assertIn('temperature', point)
            self.assertIsInstance(point['temperature'], float)
    
    def test_export_to_dataframe(self):
        """Test export to DataFrame"""
        test_results = {
            'pfr': [
                {
                    'success': True,
                    'conversion_percent': 50.0,
                    'b_production_rate': 50.0,
                    'parameters': {
                        'reactor': {'temperature': 350.0, 'volume': 1.0},
                        'feed': {'temperature': 300.0}
                    }
                }
            ],
            'distillation': [
                {
                    'success': True,
                    'converged': True,
                    'distillate_purity_A': 95.0,
                    'parameters': {
                        'column': {'reflux_ratio': 2.0, 'stages': 10},
                        'feed': {'temperature': 350.0}
                    }
                }
            ]
        }
        
        dfs = self.study.export_to_dataframe(test_results)
        self.assertIsInstance(dfs, dict)
        
        if 'pfr' in dfs:
            self.assertIsNotNone(dfs['pfr'])
            self.assertGreater(len(dfs['pfr']), 0)
        
        if 'distillation' in dfs:
            self.assertIsNotNone(dfs['distillation'])
            self.assertGreater(len(dfs['distillation']), 0)
    
    def test_analyze_all_results(self):
        """Test analysis of all results"""
        test_results = {
            'pfr': [
                {'success': True, 'conversion_percent': 50.0},
                {'success': True, 'conversion_percent': 75.0},
                {'success': False}
            ],
            'distillation': [
                {'success': True, 'converged': True, 'distillate_purity_A': 80.0},
                {'success': True, 'converged': False, 'distillate_purity_A': 0.0},
                {'success': False, 'converged': False}
            ]
        }
        
        analysis = self.study.analyze_all_results(test_results)
        self.assertIsNotNone(analysis)
        self.assertIn('pfr', analysis)
        self.assertIn('distillation', analysis)
        self.assertIn('overall', analysis)
        
        overall = analysis['overall']
        self.assertEqual(overall['total_cases'], 6)
        # Only successful PFR and successful+converged distillation count
        self.assertEqual(overall['successful_cases'], 3)
    
    def test_surface_data_creation(self):
        """Test response surface data creation"""
        test_results = [
            {
                'success': True,
                'conversion_percent': 50.0,
                'reactor_temperature': 350.0,
                'reactor_volume': 1.0,
                'parameters': {
                    'reactor': {'temperature': 350.0, 'volume': 1.0}
                }
            },
            {
                'success': True,
                'conversion_percent': 60.0,
                'reactor_temperature': 375.0,
                'reactor_volume': 1.5,
                'parameters': {
                    'reactor': {'temperature': 375.0, 'volume': 1.5}
                }
            }
        ]
        
        surface_data = self.study._create_surface_data(
            test_results,
            x_param='temperature',
            y_param='volume',
            z_param='conversion_percent'
        )
        
        # With only 2 points, surface data might be empty
        # But the method should not crash
        self.assertIsInstance(surface_data, dict)
    
    def tearDown(self):
        """Clean up after tests"""
        pass

if __name__ == '__main__':
    unittest.main()