#!/usr/bin/env python3
"""
GRAPE Recorder - HF Time Signal Data Products

Decimation, spectrograms, Digital RF packaging, and PSWS upload
for WWV/WWVH/CHU time signal recordings.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="grape-recorder",
    version="0.1.0",
    author="Michael James Hauan",
    author_email="ac0g@arrl.net",
    description="HF time signal data products - decimation, spectrograms, and PSWS upload",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HamSCI/grape-recorder",
    project_urls={
        "Bug Tracker": "https://github.com/HamSCI/grape-recorder/issues",
        "Documentation": "https://github.com/HamSCI/grape-recorder#readme",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Communications :: Ham Radio",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "h5py>=3.0.0",
        "paramiko>=2.9.0",  # For SFTP upload
        "hf-timestd>=0.1.0",  # Core recording and timing analysis
    ],
    extras_require={
        "drf": [
            "digital_rf>=2.6.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "grape-recorder=grape_recorder.cli:main",
            "grape-decimate=grape_recorder.cli:decimate",
            "grape-spectrogram=grape_recorder.cli:spectrogram",
            "grape-upload=grape_recorder.cli:upload",
            "grape-package-drf=grape_recorder.cli:package_drf",
        ],
    },
)
