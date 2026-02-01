import sys
import os
from pathlib import Path
import argparse
from datetime import datetime

if sys.version_info >= (3, 10):
    # Set environment variable for pythonnet
    os.environ['PYTHONNET_PYDLL'] = 'python310.dll'
    
    # Early pythonnet initialization
    try:
        import pythonnet
        pythonnet.load()
    except:
        pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.logger import setup_logger
from src.main import DWSimAutomation

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='DWSIM Automation: PFR and Distillation Simulations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                       # Run complete study
  %(prog)s --pfr-only            # Run only PFR simulations
  %(prog)s --distillation-only   # Run only distillation simulations
  %(prog)s --quick               # Run quick study with reduced parameters
  %(prog)s --config custom_config/ # Use custom config directory
        """
    )
    
    parser.add_argument('--pfr-only', action='store_true',
                       help='Run only PFR simulations')
    parser.add_argument('--distillation-only', action='store_true',
                       help='Run only distillation simulations')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick study with reduced parameter space')
    parser.add_argument('--config', default='config',
                       help='Configuration directory (default: config)')
    parser.add_argument('--output', default='results',
                       help='Output directory (default: results)')
    parser.add_argument('--no-plots', action='store_true',
                       help='Disable plot generation')
    parser.add_argument('--parallel', action='store_true',
                       help='Enable parallel processing')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers (default: 4)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    return parser.parse_args()

def setup_environment(args):
    """Setup execution environment"""
    # Set environment variables based on arguments
    if args.no_plots:
        os.environ['SAVE_PLOTS'] = 'false'
    
    if args.parallel:
        os.environ['USE_PARALLEL_PROCESSING'] = 'true'
        os.environ['MAX_WORKERS'] = str(args.workers)
    
    if args.verbose:
        os.environ['LOG_LEVEL'] = 'INFO'
    
    if args.debug:
        os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    # Setup logger
    log_level = 'DEBUG' if args.debug else ('INFO' if args.verbose else 'INFO')
    logger = setup_logger('run_screening', log_level, 
                         f'{args.output}/simulation.log')
    
    return logger

def modify_config_for_quick_mode(config_dir):
    """Modify configuration files for quick mode"""
    import yaml
    
    # Quick mode reduces parameter space for faster execution
    pfr_config_path = Path(config_dir) / 'pfr_config.yaml'
    dist_config_path = Path(config_dir) / 'distillation_config.yaml'
    sweep_config_path = Path(config_dir) / 'sweep_config.yaml'
    
    if pfr_config_path.exists():
        with open(pfr_config_path, 'r') as f:
            pfr_config = yaml.safe_load(f)
        
        # Reduce sweep steps
        if 'sweep' in pfr_config:
            for param in ['temperature', 'volume']:
                if param in pfr_config['sweep']:
                    pfr_config['sweep'][param]['steps'] = 3
        
        with open(pfr_config_path, 'w') as f:
            yaml.dump(pfr_config, f, default_flow_style=False)
    
    if dist_config_path.exists():
        with open(dist_config_path, 'r') as f:
            dist_config = yaml.safe_load(f)
        
        # Reduce sweep steps
        if 'sweep' in dist_config:
            for param in ['reflux_ratio', 'stages']:
                if param in dist_config['sweep']:
                    if param == 'stages':
                        dist_config['sweep'][param]['steps'] = 3
                    else:
                        dist_config['sweep'][param]['steps'] = 3
        
        with open(dist_config_path, 'w') as f:
            yaml.dump(dist_config, f, default_flow_style=False)
    
    if sweep_config_path.exists():
        with open(sweep_config_path, 'r') as f:
            sweep_config = yaml.safe_load(f)
        
        # Reduce steps in sweep config
        if 'pfr' in sweep_config and 'ranges' in sweep_config['pfr']:
            for param in sweep_config['pfr']['ranges']:
                sweep_config['pfr']['ranges'][param]['steps'] = 3
        
        if 'distillation' in sweep_config and 'ranges' in sweep_config['distillation']:
            for param in sweep_config['distillation']['ranges']:
                sweep_config['distillation']['ranges'][param]['steps'] = 3
        
        with open(sweep_config_path, 'w') as f:
            yaml.dump(sweep_config, f, default_flow_style=False)
    
    print("✅ Configurations modified for quick mode")

def main():
    """Main function"""
    args = parse_arguments()
    logger = setup_environment(args)
    
    print("\n" + "="*60)
    print("DWSIM Automation Project")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {args.config}")
    print(f"Output directory: {args.output}")
    print(f"Mode: {'Quick' if args.quick else 'Normal'}")
    print(f"Parallel: {args.parallel} ({args.workers} workers)")
    print("="*60 + "\n")
    
    # Modify config for quick mode if requested
    if args.quick:
        modify_config_for_quick_mode(args.config)
    
    try:
        # Create automation instance
        automation = DWSimAutomation()
        
        # Initialize
        if not automation.initialize():
            logger.error("Initialization failed")
            return 1
        
        # Load configurations
        import yaml
        
        pfr_config_path = Path(args.config) / 'pfr_config.yaml'
        dist_config_path = Path(args.config) / 'distillation_config.yaml'
        
        if not pfr_config_path.exists():
            logger.error(f"PFR config not found: {pfr_config_path}")
            return 1
        
        if not dist_config_path.exists():
            logger.error(f"Distillation config not found: {dist_config_path}")
            return 1
        
        # Run simulations based on arguments
        if args.pfr_only:
            logger.info("Running PFR simulations only")
            with open(pfr_config_path, 'r') as f:
                pfr_config = yaml.safe_load(f)
            pfr_results = automation.run_pfr_simulation(pfr_config)
            
            if pfr_results:
                automation.generate_reports(pfr_results, None)
        
        elif args.distillation_only:
            logger.info("Running distillation simulations only")
            with open(dist_config_path, 'r') as f:
                dist_config = yaml.safe_load(f)
            dist_results = automation.run_distillation_simulation(dist_config)
            
            if dist_results:
                automation.generate_reports(None, dist_results)
        
        else:
            # Run complete study
            logger.info("Running complete simulation study")
            success = automation.run_complete_study(
                str(pfr_config_path),
                str(dist_config_path)
            )
            
            if not success:
                logger.error("Complete study failed")
                return 1
        
        # Summary
        elapsed = datetime.now() - automation.start_time
        print("\n" + "="*60)
        print("SIMULATION COMPLETE")
        print("="*60)
        print(f"Total execution time: {elapsed}")
        print(f"Results saved to: {args.output}/")
        print(f"Main output file: {args.output}/results.csv")
        print("="*60)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Simulation interrupted by user")
        return 130  # Standard exit code for Ctrl+C
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\n❌ Simulation failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())