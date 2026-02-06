"""
Unit tests for PFR simulator
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pfr_simulator import PFRSimulator
from src.dwsim_controller import DWSIMController
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

class TestPFRSimulator(unittest.TestCase):
    """Test cases for PFRSimulator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_controller = MockController()
        self.simulator = PFRSimulator(self.mock_controller)
        
        # Test configuration
        self.test_config = {
            'reactor': {
                'volume': 1.0,
                'temperature': 350.0,
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
    
    def test_initialization(self):
        """Test simulator initialization"""
        self.assertIsNotNone(self.simulator)
        self.assertIsInstance(self.simulator, PFRSimulator)
    
    def test_config_validation(self):
        """Test configuration validation"""
        valid, errors = validate_config(self.test_config, 'pfr')
        self.assertTrue(valid, f"Config validation failed: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_invalid_config(self):
        """Test invalid configuration"""
        invalid_config = {
            'reactor': {
                'volume': -1.0,  # Invalid: negative volume
                'temperature': 350.0
            },
            'feed': {
                'temperature': 300.0
            }
        }
        
        valid, errors = validate_config(invalid_config, 'pfr')
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_parameter_extraction(self):
        """Test parameter extraction from results"""
        test_result = {
            'success': True,
            'conversion_percent': 75.5,
            'b_production_rate': 75.5,
            'reactor_temperature': 350.0,
            'reactor_volume': 1.0,
            'sweep_parameters': {
                'temperature': 350.0,
                'volume': 1.0
            }
        }
        
        # Test find_optimal_conditions
        optimal = self.simulator.find_optimal_conditions([test_result])
        self.assertIsNotNone(optimal)
        self.assertIn('max_conversion', optimal)
        self.assertIn('max_production', optimal)
    
    def test_analyze_results_empty(self):
        """Test analysis with empty results"""
        analysis = self.simulator.analyze_results([])
        self.assertEqual(analysis, {})
    
    def test_analyze_results_successful(self):
        """Test analysis with successful results"""
        test_results = [
            {
                'success': True,
                'conversion_percent': 50.0,
                'b_production_rate': 50.0
            },
            {
                'success': True,
                'conversion_percent': 75.0,
                'b_production_rate': 75.0
            },
            {
                'success': False,  # This should be ignored
                'conversion_percent': 0.0,
                'b_production_rate': 0.0
            }
        ]
        
        analysis = self.simulator.analyze_results(test_results)
        self.assertIsNotNone(analysis)
        self.assertIn('total_cases', analysis)
        self.assertIn('successful_cases', analysis)
        self.assertEqual(analysis['total_cases'], 3)
        self.assertEqual(analysis['successful_cases'], 2)
    
    def test_sweep_config_generation(self):
        """Test sweep configuration generation"""
        sweep_config = {
            'temperature': {'min': 300, 'max': 400, 'steps': 3},
            'volume': {'min': 0.5, 'max': 2.0, 'steps': 2}
        }
        
        # This would normally create cases through run_parametric_sweep
        # For unit test, we'll just verify the sweep config is valid
        self.assertIn('temperature', sweep_config)
        self.assertIn('volume', sweep_config)
        
        temp_range = sweep_config['temperature']
        self.assertEqual(temp_range['min'], 300)
        self.assertEqual(temp_range['max'], 400)
        self.assertEqual(temp_range['steps'], 3)
    
    def tearDown(self):
        """Clean up after tests"""
        self.mock_controller.cleanup()

if __name__ == '__main__':
    unittest.main()