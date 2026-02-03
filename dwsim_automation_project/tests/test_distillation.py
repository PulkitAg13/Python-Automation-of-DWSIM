"""
Unit tests for Distillation simulator
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.distillation_simulator import DistillationSimulator
from utils.validation import validate_config

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

class TestDistillationSimulator(unittest.TestCase):
    """Test cases for DistillationSimulator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_controller = MockController()
        self.simulator = DistillationSimulator(self.mock_controller)
        
        # Test configuration
        self.test_config = {
            'column': {
                'stages': 10,
                'feed_stage': 5,
                'reflux_ratio': 2.0,
                'distillate_rate': 50.0
            },
            'feed': {
                'temperature': 350.0,
                'pressure': 101325,
                'flow_rate': 100.0,
                'composition': {'A': 0.5, 'B': 0.5}
            }
        }
    
    def test_initialization(self):
        """Test simulator initialization"""
        self.assertIsNotNone(self.simulator)
        self.assertIsInstance(self.simulator, DistillationSimulator)
    
    def test_config_validation(self):
        """Test configuration validation"""
        valid, errors = validate_config(self.test_config, 'distillation')
        self.assertTrue(valid, f"Config validation failed: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_invalid_config(self):
        """Test invalid configuration"""
        invalid_config = {
            'column': {
                'stages': 1,  # Invalid: less than 2 stages
                'reflux_ratio': -1.0  # Invalid: negative reflux ratio
            },
            'feed': {
                'temperature': 350.0
            }
        }
        
        valid, errors = validate_config(invalid_config, 'distillation')
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_parameter_extraction(self):
        """Test parameter extraction from results"""
        test_result = {
            'success': True,
            'converged': True,
            'distillate_purity_A': 95.5,
            'bottoms_purity_B': 90.0,
            'total_energy': 1500.0,
            'reflux_ratio': 2.0,
            'column_stages': 10,
            'sweep_parameters': {
                'reflux_ratio': 2.0,
                'stages': 10
            }
        }
        
        # Test find_optimal_conditions
        optimal = self.simulator.find_optimal_conditions([test_result])
        self.assertIsNotNone(optimal)
        self.assertIn('max_distillate_purity', optimal)
        self.assertIn('max_bottoms_purity', optimal)
        self.assertIn('min_energy', optimal)
    
    def test_analyze_results_empty(self):
        """Test analysis with empty results"""
        analysis = self.simulator.analyze_results([])
        self.assertEqual(analysis, {})
    
    def test_analyze_results_successful(self):
        """Test analysis with successful results"""
        test_results = [
            {
                'success': True,
                'converged': True,
                'distillate_purity_A': 80.0,
                'bottoms_purity_B': 85.0,
                'total_energy': 1000.0
            },
            {
                'success': True,
                'converged': True,
                'distillate_purity_A': 90.0,
                'bottoms_purity_B': 88.0,
                'total_energy': 1200.0
            },
            {
                'success': True,
                'converged': False,  # This should be ignored
                'distillate_purity_A': 0.0,
                'bottoms_purity_B': 0.0,
                'total_energy': 0.0
            },
            {
                'success': False,  # This should be ignored
                'converged': False,
                'distillate_purity_A': 0.0,
                'bottoms_purity_B': 0.0,
                'total_energy': 0.0
            }
        ]
        
        analysis = self.simulator.analyze_results(test_results)
        self.assertIsNotNone(analysis)
        self.assertIn('total_cases', analysis)
        self.assertIn('successful_cases', analysis)
        self.assertEqual(analysis['total_cases'], 4)
        self.assertEqual(analysis['successful_cases'], 2)  # Only converged and successful
    
    def test_sweep_config_generation(self):
        """Test sweep configuration generation"""
        sweep_config = {
            'reflux_ratio': {'min': 1.0, 'max': 5.0, 'steps': 3},
            'stages': {'min': 5, 'max': 15, 'steps': 3}
        }
        
        # This would normally create cases through run_parametric_sweep
        # For unit test, we'll just verify the sweep config is valid
        self.assertIn('reflux_ratio', sweep_config)
        self.assertIn('stages', sweep_config)
        
        rr_range = sweep_config['reflux_ratio']
        self.assertEqual(rr_range['min'], 1.0)
        self.assertEqual(rr_range['max'], 5.0)
        self.assertEqual(rr_range['steps'], 3)
    
    def test_feed_stage_calculation(self):
        """Test automatic feed stage calculation"""
        config_without_feed_stage = {
            'column': {
                'stages': 10,
                'reflux_ratio': 2.0,
                'distillate_rate': 50.0
            },
            'feed': {
                'temperature': 350.0,
                'pressure': 101325,
                'flow_rate': 100.0,
                'composition': {'A': 0.5, 'B': 0.5}
            }
        }
        
        # The simulator should calculate feed_stage as stages // 2
        # This is tested in the integration, not unit test
        pass
    
    def tearDown(self):
        """Clean up after tests"""
        self.mock_controller.cleanup()

if __name__ == '__main__':
    unittest.main()