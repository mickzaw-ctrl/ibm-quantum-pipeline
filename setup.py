"""
IBM Quantum Hybrid Test Pipeline
---------------------------------

A complete quantum computing test pipeline with Qiskit Aer,
noise modeling, error mitigation, and benchmarking.

Author: Michał Ślusarczyk
Version: 1.0.0
License: MIT
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name="ibm-quantum-pipeline",
    version="1.0.0",
    author="Michał Ślusarczyk",
    author_email="michal.slusarczyk@example.com",
    description="Hybrid quantum test pipeline with Qiskit Aer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/ibm-quantum-pipeline",
    project_urls={
        "Bug Tracker": "https://github.com/YOUR_USERNAME/ibm-quantum-pipeline/issues",
        "Documentation": "https://github.com/YOUR_USERNAME/ibm-quantum-pipeline/docs",
        "Source Code": "https://github.com/YOUR_USERNAME/ibm-quantum-pipeline",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Quantum Computing",
        "Machine Learning",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "qiskit>=1.0.0",
        "qiskit-aer>=0.13.0",
        "qiskit-ibm-runtime>=0.25.0",
        "numpy>=1.21.0",
        "scipy>=1.9.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "quantum-pipeline=src.pipeline:main_cli",
        ],
    },
    keywords=[
        "quantum computing",
        "qiskit",
        "quantum simulation",
        "error mitigation",
        "benchmarking",
        "quantum machine learning",
    ],
)