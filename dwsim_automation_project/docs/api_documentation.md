# DWSIM Automation API Documentation

## Overview

This API provides Python automation for DWSIM process simulations. The main components are:

1. **DWSIMController** - Interface with DWSIM Automation API
2. **PFRSimulator** - Plug Flow Reactor simulations
3. **DistillationSimulator** - Distillation column simulations
4. **ParametricStudy** - Advanced parametric studies
5. **ResultsManager** - Results handling and reporting
6. **Visualization** - Plotting and visualization

## Installation

```bash
pip install -r requirements.txt
Quick Start
python
from src.dwsim_controller import DWSIMController
from src.pfr_simulator import PFRSimulator

# Initialize controller
controller = DWSIMController()
controller.initialize()

# Create PFR simulator
pfr_simulator = PFRSimulator(controller)

# Run simulation
config = {
    'reactor': {'volume': 1.0, 'temperature': 350.0},
    'feed': {'flow_rate': 100.0, 'composition': {'A': 1.0}}
}
results = pfr_simulator.run_base_case(config)

# Cleanup
controller.cleanup()
DWSIMController API
Initialization
python
controller = DWSIMController()
success = controller.initialize(dwsim_path="C:/Program Files/DWSIM")
Creating Unit Operations
python
# Create material stream
stream = controller.create_material_stream(
    name="Feed",
    temperature=300.0,
    pressure=101325,
    flow_rate=100.0,
    composition={'A': 1.0, 'B': 0.0}
)

# Create PFR reactor
reactor = controller.create_reactor_pfr(
    name="PFR",
    volume=1.0,
    temperature=350.0,
    pressure=101325
)

# Create distillation column
column = controller.create_distillation_column(
    name="Column",
    stages=10,
    feed_stage=5,
    reflux_ratio=2.0,
    distillate_rate=50.0
)
Connecting Streams
python
controller.connect_streams(feed_stream, reactor, port=0)
controller.connect_streams(reactor, product_stream, port=0)
Adding Reactions
python
controller.add_reaction(
    reactor=reactor,
    reaction_name="A_to_B",
    reactants={'A': 1.0},
    products={'B': 1.0},
    rate_constant=0.1,
    activation_energy=50000.0
)
Solving Flowsheet
python
success = controller.solve_flowsheet(max_iterations=100, tolerance=1e-6)
Getting Results
python
stream_results = controller.get_stream_results(stream)
reactor_results = controller.get_reactor_results(reactor)
column_results = controller.get_column_results(column)
Cleanup
python
controller.cleanup()
PFRSimulator API
Basic Simulation
python
pfr_simulator = PFRSimulator(controller)

config = {
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

results = pfr_simulator.run_base_case(config)
Parametric Sweep
python
sweep_config = {
    'temperature': {'min': 300, 'max': 400, 'steps': 5},
    'volume': {'min': 0.5, 'max': 5.0, 'steps': 5}
}

sweep_results = pfr_simulator.run_parametric_sweep(
    sweep_config,
    variables=['temperature', 'volume']
)
Results Analysis
python
analysis = pfr_simulator.analyze_results(sweep_results)
optimal = pfr_simulator.find_optimal_conditions(sweep_results)
DistillationSimulator API
Basic Simulation
python
dist_simulator = DistillationSimulator(controller)

config = {
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

results = dist_simulator.run_base_case(config)
Parametric Sweep
python
sweep_config = {
    'reflux_ratio': {'min': 1.0, 'max': 5.0, 'steps': 5},
    'stages': {'min': 5, 'max': 20, 'steps': 4}
}

sweep_results = dist_simulator.run_parametric_sweep(
    sweep_config,
    variables=['reflux_ratio', 'stages']
)
ParametricStudy API
Comprehensive Sweep
python
study = ParametricStudy(controller_factory)

config = {
    'pfr': {
        'ranges': {
            'temperature': {'min': 300, 'max': 400, 'steps': 5},
            'volume': {'min': 0.5, 'max': 5.0, 'steps': 5}
        }
    },
    'distillation': {
        'ranges': {
            'reflux_ratio': {'min': 1.0, 'max': 5.0, 'steps': 5},
            'stages': {'min': 5, 'max': 20, 'steps': 4}
        }
    }
}

results = study.run_comprehensive_sweep(config, parallel=True)
Export to DataFrame
python
dfs = study.export_to_dataframe(results)
pfr_df = dfs.get('pfr')
dist_df = dfs.get('distillation')
ResultsManager API
Saving Results
python
manager = ResultsManager()

# Save to CSV
manager.save_to_csv(results, 'results.csv')

# Save to JSON
manager.save_to_json(results, 'pfr_results.json', 'pfr')
manager.save_to_json(results, 'distillation_results.json', 'distillation')

# Generate HTML report
manager.generate_html_report(results, 'results_summary.html')
Validation
python
validation = manager.validate_results(results)
if validation['valid']:
    print("Results are valid")
else:
    print(f"Validation errors: {validation['errors']}")
Visualization API
Creating Plots
python
visualizer = Visualization()

# Create individual plots
visualizer.create_pfr_sweep_3d(results, 'plots/pfr_3d.png')
visualizer.create_distillation_optimization(results, 'plots/dist_opt.png')
visualizer.create_sensitivity_analysis(results, 'plots/sensitivity.png')

# Create all plots
plot_results = visualizer.create_all_plots(results, 'plots/')
Configuration Files
PFR Configuration (config/pfr_config.yaml)
yaml
reactor:
  volume: 1.0
  temperature: 350.0
  pressure: 101325

feed:
  temperature: 300.0
  pressure: 101325
  flow_rate: 100.0
  composition:
    A: 1.0
    B: 0.0

sweep:
  temperature:
    min: 300
    max: 400
    steps: 5
Distillation Configuration (config/distillation_config.yaml)
yaml
column:
  stages: 10
  feed_stage: 5
  reflux_ratio: 2.0
  distillate_rate: 50.0

feed:
  temperature: 350.0
  pressure: 101325
  flow_rate: 100.0
  composition:
    A: 0.5
    B: 0.5
Error Handling
All API methods include error handling. Check the success flag in results:

python
results = pfr_simulator.run_base_case(config)
if results.get('success', False):
    # Process successful results
    conversion = results['conversion_percent']
else:
    # Handle error
    error = results.get('error', 'Unknown error')
    print(f"Simulation failed: {error}")
Logging
python
from utils.logger import setup_logger

logger = setup_logger('my_simulation', log_level='DEBUG')
logger.info("Starting simulation")
logger.debug(f"Configuration: {config}")
logger.error(f"Simulation failed: {error}")
Environment Variables
Set these in .env file:

text
DWSIM_PATH=C:/Program Files/DWSIM
LOG_LEVEL=INFO
MAX_SIMULATION_TIME=30
SAVE_PLOTS=true
Testing
Run unit tests:

bash
pytest tests/ -v
Run specific test module:

bash
pytest tests/test_pfr.py
Troubleshooting
Common issues:

DWSIM not found: Set correct DWSIM_PATH in .env

Pythonnet issues: Ensure Python 3.8+ and .NET Framework 4.8+

Memory issues: Reduce parametric sweep size

Convergence issues: Adjust solver tolerances in config

See docs/troubleshooting.md for detailed solutions.