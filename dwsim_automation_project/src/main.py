"""
Main module for DWSIM automation
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.validation import validate_environment
from src.dwsim_controller import DWSIMController
from src.pfr_simulator import PFRSimulator
from src.distillation_simulator import DistillationSimulator
from src.parametric_study import ParametricStudy
from src.results_manager import ResultsManager
from src.visualization import Visualization

class DWSimAutomation:
    """Main automation class for DWSIM simulations"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.results = {}
        self.start_time = None
        
    def initialize(self):
        """Initialize the simulation environment"""
        self.logger.info("Initializing DWSIM automation environment")
        self.start_time = datetime.now()
        
        # Validate environment
        if not validate_environment():
            self.logger.error("Environment validation failed")
            return False
            
        return True
    
    def run_pfr_simulation(self, config):
        """Run PFR simulation"""
        self.logger.info("Starting PFR simulation")
        
        try:
            # Initialize DWSIM
            controller = DWSIMController()
            if not controller.initialize():
                return None
            
            # Create PFR simulator
            pfr_simulator = PFRSimulator(controller)
            
            # Run base case
            base_result = pfr_simulator.run_base_case(config)
            
            # Run parametric sweep
            sweep_results = pfr_simulator.run_parametric_sweep(
                config.get('sweep', {}),
                variables=['temperature', 'volume']
            )
            
            results = {
                'base_case': base_result,
                'sweep_results': sweep_results
            }
            
            controller.cleanup()
            return results
            
        except Exception as e:
            self.logger.error(f"PFR simulation failed: {str(e)}")
            return None
    
    def run_distillation_simulation(self, config):
        """Run distillation column simulation"""
        self.logger.info("Starting distillation column simulation")
        
        try:
            # Initialize DWSIM
            controller = DWSIMController()
            if not controller.initialize():
                return None
            
            # Create distillation simulator
            dist_simulator = DistillationSimulator(controller)
            
            # Run base case
            base_result = dist_simulator.run_base_case(config)
            
            # Run parametric sweep
            sweep_results = dist_simulator.run_parametric_sweep(
                config.get('sweep', {}),
                variables=['reflux_ratio', 'stages']
            )
            
            results = {
                'base_case': base_result,
                'sweep_results': sweep_results
            }
            
            controller.cleanup()
            return results
            
        except Exception as e:
            self.logger.error(f"Distillation simulation failed: {str(e)}")
            return None
    
    def generate_reports(self, pfr_results, dist_results):
        """Generate comprehensive reports"""
        self.logger.info("Generating reports")
        
        # Create results manager
        results_manager = ResultsManager()
        
        # Save all results
        all_results = {
            'pfr': pfr_results,
            'distillation': dist_results,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'execution_time': str(datetime.now() - self.start_time)
            }
        }
        
        # Save to CSV
        results_manager.save_to_csv(all_results, 'results/results.csv')
        
        # Save detailed JSON
        results_manager.save_to_json(all_results, 'results/pfr_results.json', 'pfr')
        results_manager.save_to_json(all_results, 'results/distillation_results.json', 'distillation')
        
        # Generate HTML report
        results_manager.generate_html_report(all_results, 'results/results_summary.html')
        
        # Create visualizations
        if os.getenv('SAVE_PLOTS', 'true').lower() == 'true':
            visualizer = Visualization()
            visualizer.create_all_plots(all_results, 'results/plots/')
        
        self.logger.info("Reports generated successfully")
    
    def run_complete_study(self, pfr_config_path, dist_config_path):
        """Run complete simulation study"""
        self.logger.info("Starting complete simulation study")
        
        # Load configurations
        import yaml
        
        with open(pfr_config_path, 'r') as f:
            pfr_config = yaml.safe_load(f)
        
        with open(dist_config_path, 'r') as f:
            dist_config = yaml.safe_load(f)
        
        # Run PFR simulations
        pfr_results = self.run_pfr_simulation(pfr_config)
        
        # Run distillation simulations
        dist_results = self.run_distillation_simulation(dist_config)
        
        # Generate reports
        if pfr_results or dist_results:
            self.generate_reports(pfr_results, dist_results)
        
        self.logger.info(f"Study completed in {datetime.now() - self.start_time}")
        return True

def main():
    """Main entry point"""
    automation = DWSimAutomation()
    
    if automation.initialize():
        automation.run_complete_study(
            'config/pfr_config.yaml',
            'config/distillation_config.yaml'
        )

if __name__ == "__main__":
    main()