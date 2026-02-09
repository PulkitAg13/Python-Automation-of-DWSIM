# DWSIM Automation Project

Complete Python automation for DWSIM process simulations with PFR reactors and distillation columns.

## Features
- ✅ Full automation of DWSIM via Python
- ✅ PFR reactor simulation with kinetic reactions
- ✅ Distillation column simulation
- ✅ Parametric sweep studies
- ✅ Headless execution (no GUI)
- ✅ Comprehensive error handling
- ✅ Advanced visualization
- ✅ HTML reporting
- ✅ Parallel processing support

## Installation

1. **Install DWSIM** (version 7 or later)
2. **Clone this repository**
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt

4. Configure environment:

bash
cp .env.example .env
# Edit .env and set your DWSIM installation path
Quick Start
Run the complete simulation study:

bash
python run_screening.py
Project Structure
text
dwsim_automation_project/
├── src/              # Source code modules
├── config/           # Configuration files (YAML)
├── tests/           # Unit tests
├── results/         # Output files (CSV, JSON, HTML, plots)
├── logs/            # Log files
├── utils/           # Utility functions
└── docs/            # Documentation
Configuration
Edit the YAML files in config/ to customize:

Reaction kinetics

Column specifications

Parametric sweep ranges

Simulation tolerances

Outputs
After running simulations, check the results/ directory for:

results.csv - Main simulation results

HTML report with interactive visualizations

JSON files with detailed data

Publication-quality plots

Testing
Run the test suite:

bash
pytest tests/ -v
Troubleshooting
Common issues and solutions are documented in docs/troubleshooting.md

License
MIT License