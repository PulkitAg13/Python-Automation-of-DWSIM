"""
DWSIM Automation Package
"""

__version__ = "1.0.0"
__author__ = "DWSIM Automation Team"

from .dwsim_controller import DWSIMController
from .pfr_simulator import PFRSimulator
from .distillation_simulator import DistillationSimulator
from .parametric_study import ParametricStudy
from .results_manager import ResultsManager
from .visualization import Visualization

__all__ = [
    'DWSIMController',
    'PFRSimulator',
    'DistillationSimulator', 
    'ParametricStudy',
    'ResultsManager',
    'Visualization'
]