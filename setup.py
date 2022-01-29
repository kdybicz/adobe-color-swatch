from setuptools import setup, find_packages

setup(
    name='swatch-cli',
    version='0.1.0',
    entry_points={
        'console_scripts': ['swatch=swatch.cli:main'],
    },
    install_requires=[],
    packages=find_packages(exclude=["tests", "tests.*"]),
)
