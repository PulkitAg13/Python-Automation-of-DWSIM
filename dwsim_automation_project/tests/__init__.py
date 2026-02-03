"""
Test package for DWSIM automation
"""

from .test_pfr import TestPFRSimulator
from .test_distillation import TestDistillationSimulator
from .test_parametric import TestParametricStudy

__all__ = [
    'TestPFRSimulator',
    'TestDistillationSimulator',
    'TestParametricStudy'
]