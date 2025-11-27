"""Setup script for Bugnosis CLI."""

from setuptools import setup, find_packages

setup(
    name='bugnosis',
    version='0.1.0',
    description='Find high-impact bugs to fix in open source',
    author='Bugnosis Contributors',
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0',
    ],
    entry_points={
        'console_scripts': [
            'bugnosis=bugnosis.cli:main',
        ],
    },
    python_requires='>=3.8',
)


