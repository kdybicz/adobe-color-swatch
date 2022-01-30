from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="adobe-swatch",
    version="1.0.0",
    entry_points={
        "console_scripts": ["swatch=swatch.cli:main"],
    },
    install_requires=[],
    packages=find_packages(exclude=["tests", "tests.*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kdybicz/adobe-swatch-generator",
    description="The finest selection of Chuck Norris jokes."
)
