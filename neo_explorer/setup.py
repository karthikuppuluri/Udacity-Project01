"""
Setup script for NEO Explorer package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent.parent / 'README.md'
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ''

setup(
    name="neo-explorer",
    version="2.0.0",
    author="NEO Explorer Team",
    author_email="team@neo-explorer.com",
    description="A robust tool for exploring Near-Earth Objects and their close approaches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neo-explorer/neo-explorer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies required for basic functionality
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "neo-explorer=neo_explorer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "neo_explorer": ["py.typed"],
    },
    zip_safe=False,
) 