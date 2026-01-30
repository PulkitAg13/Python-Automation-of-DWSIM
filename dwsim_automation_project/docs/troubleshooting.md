### **27. docs/troubleshooting.md**
```markdown
# Troubleshooting Guide

## Common Issues and Solutions

### 1. DWSIM Initialization Failures

**Issue**: `Failed to initialize DWSIM` error

**Solutions**:
1. **Check DWSIM installation path**:
   ```bash
   # In .env file, set correct path
   DWSIM_PATH=C:/Program Files/DWSIM  # Windows
   DWSIM_PATH=/opt/DWSIM              # Linux
   DWSIM_PATH=/Applications/DWSIM     # Mac
Verify .NET Framework:

DWSIM requires .NET Framework 4.8 or later

Download from: https://dotnet.microsoft.com/download/dotnet-framework

Run as Administrator (Windows):

Right-click on Command Prompt/PowerShell

Select "Run as administrator"

Check Pythonnet installation:

bash
pip uninstall pythonnet
pip install pythonnet==3.0.2
2. Pythonnet Import Errors
Issue: ModuleNotFoundError: No module named 'clr'

Solutions:

Reinstall pythonnet:

bash
pip uninstall pythonnet clr-loader
pip install pythonnet==3.0.2 clr-loader==0.2.4
Check Python architecture:

DWSIM requires 64-bit Python

Verify with: python -c "import struct; print(struct.calcsize('P') * 8)"

Should print 64

Set Pythonnet configuration:

python
import os
os.environ['PYTHONNET_PYDLL'] = 'python38.dll'  # Adjust for your Python version
3. Simulation Convergence Issues
Issue: Flowsheet fails to converge

Solutions:

Increase solver iterations:

yaml
# In config files
solver:
  max_iterations: 1000
  tolerance: 1e-5
Relax convergence criteria:

yaml
solver:
  tolerance: 1e-4  # Increase from 1e-6
Provide better initial guesses:

Modify feed conditions

Adjust temperature/pressure ranges

Check component properties:

Ensure all components are defined

Check property package compatibility

4. Memory Issues
Issue: MemoryError or slow performance with large parametric sweeps

Solutions:

Reduce sweep size:

yaml
sweep:
  temperature:
    steps: 5  # Reduce from 10
  volume:
    steps: 5  # Reduce from 10
Enable garbage collection:

python
import gc
gc.collect()  # Call between simulations
Use parallel processing cautiously:

python
# Reduce number of workers
results = study.run_comprehensive_sweep(config, parallel=True, max_workers=2)
Clear DWSIM between runs:

python
controller.cleanup()  # Ensure cleanup is called
5. Plot Generation Failures
Issue: Plots not generated or empty

Solutions:

Check matplotlib backend:

python
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
Install required libraries:

bash
pip install matplotlib plotly seaborn
Verify data availability:

Check if simulation results exist

Ensure enough data points for 3D plots (minimum 4)

Check write permissions:

python
import os
os.access('results/plots', os.W_OK)  # Should return True
6. CSV/JSON Export Issues
Issue: Files not created or incomplete

Solutions:

Check directory permissions:

bash
# Ensure write permissions
chmod 755 results  # Linux/Mac
Verify data structure:

python
print(type(results))  # Should be dict
print(results.keys())  # Should contain 'pfr' or 'distillation'
Increase recursion limit for JSON:

python
import sys
sys.setrecursionlimit(10000)
Handle NaN/Inf values:

python
import numpy as np

def clean_data(data):
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    elif isinstance(data, float):
        return None if np.isnan(data) or np.isinf(data) else data
    else:
        return data
7. Parallel Processing Issues
Issue: Parallel simulations fail or hang

Solutions:

Disable parallel processing:

python
results = study.run_comprehensive_sweep(config, parallel=False)
Reduce number of workers:

python
results = study.run_comprehensive_sweep(config, parallel=True, max_workers=2)
Use joblib backend:

python
from joblib import parallel_backend

with parallel_backend('loky'):  # or 'threading'
    results = study.run_comprehensive_sweep(config, parallel=True)
Add timeouts:

python
from joblib import TimeoutError

try:
    results = study.run_comprehensive_sweep(config, parallel=True)
except TimeoutError:
    print("Parallel processing timed out")
8. Component Definition Issues
Issue: Components not found or properties missing

Solutions:

Check component names:

Use exact names as in DWSIM database

Case-sensitive

Define all components:

python
composition = {
    'Water': 0.5,
    'Ethanol': 0.5
}
Use simple components for testing:

python
composition = {
    'A': 0.5,  # Generic components
    'B': 0.5
}
Check property package:

Raoult's Law for ideal mixtures

NRTL for non-ideal mixtures

9. Log File Issues
Issue: Logs not created or empty

Solutions:

Check log directory permissions:

bash
mkdir -p logs
chmod 755 logs
Set log level explicitly:

python
from utils.logger import setup_logger
logger = setup_logger(level='DEBUG', log_file='logs/simulation.log')
Verify logger initialization:

python
import logging
print(logging.getLogger('dwsim').handlers)  # Should have handlers
Check disk space:

bash
df -h .  # Linux/Mac
dir  # Windows
10. Docker Container Issues
Issue: Docker container fails to start or run

Solutions:

Build with correct tags:

bash
docker build -t dwsim-automation:latest .
Check Docker resources:

bash
docker system df  # Check disk usage
docker stats      # Check resource usage
Mount volumes correctly:

bash
docker run -v $(pwd)/results:/app/results dwsim-automation
Check .NET installation in container:

bash
docker run dwsim-automation dotnet --info
11. Configuration File Errors
Issue: YAML parsing errors or invalid config

Solutions:

Validate YAML syntax:

bash
python -c "import yaml; yaml.safe_load(open('config/pfr_config.yaml'))"
Check indentation:

YAML uses 2-space indentation

No tabs allowed

Validate config structure:

python
from utils.validation import validate_config
valid, errors = validate_config(config, 'pfr')
print(errors)
Use default configs:

Copy from provided examples

Start with minimal config

12. Performance Optimization
Issue: Simulations run too slowly

Solutions:

Reduce sweep granularity:

yaml
sweep:
  temperature:
    steps: 5  # Instead of 10
Cache results:

python
import pickle

with open('cached_results.pkl', 'wb') as f:
    pickle.dump(results, f)
Use warm starts:

Reuse converged solutions as initial guesses

Profile code:

bash
python -m cProfile -o profile_stats run_screening.py
13. Getting Help
If issues persist:

Check logs: logs/simulation.log

Enable debug mode:

bash
export LOG_LEVEL=DEBUG
python run_screening.py
Create minimal test case:

python
# test_minimal.py
controller = DWSIMController()
print(controller.initialize())
Check DWSIM GUI: Run same simulation in GUI first

Consult documentation: docs/api_documentation.md

14. Known Limitations
DWSIM version: Requires DWSIM 7 or later

Operating system: Best support on Windows

Memory: Large sweeps may require 8GB+ RAM

Components: Some DWSIM components may not be accessible via API

Reactions: Limited to conversion reactions in this implementation

15. Emergency Recovery
If simulation hangs:

Keyboard interrupt: Ctrl+C

Kill Python process:

bash
# Linux/Mac
pkill -f python

# Windows
taskkill /f /im python.exe
Clear temporary files:

bash
rm -rf __pycache__/
rm -f *.dwxm  # DWSIM temporary files


### **28. run_screening.py** (Main Entry Point)
```python
#!/usr/bin/env python3
"""
Main entry point for DWSIM automation project
Required by project specification: run_screening.py
"""

