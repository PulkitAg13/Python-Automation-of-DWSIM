from setuptools import setup, find_packages

setup(
    name="dwsim-automation",
    version="1.0.0",
    author="DWSIM Automation Team",
    description="Automation scripts for DWSIM simulations",
    packages=find_packages(),
    install_requires=[
        "pythonnet>=3.0.2",
        "clr-loader>=0.2.4",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "plotly>=5.14.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "rich>=13.4.0",
        "scipy>=1.10.0",
        "joblib>=1.2.0",
        "tqdm>=4.65.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dwsim-run=run_screening:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
)