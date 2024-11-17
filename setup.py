from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="tradier_api",
    version="0.1.1",
    description="A Python library for the Tradier API",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Ensure PyPI renders the description properly
    author="KickshawProgrammer",
    author_email="kickshawprogrammer@gmail.com",
    license="MIT",
    packages=find_packages(include=["tradier_api", "tradier_api.*"]),
    include_package_data=True,  # Make sure additional files like README.md are included
    install_requires=[
        "requests>=2.32.3",
        "websockets>=14.1",
        
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/kickshawprogrammer/tradier_api",  # Replace with your GitHub repo
    project_urls={
        "Documentation": "https://github.com/kickshawprogrammer/tradier_api/wiki",  # Add later if applicable
        "Source": "https://github.com/kickshawprogrammer/tradier_api",
        "Bug Tracker": "https://github.com/kickshawprogrammer/tradier_api/issues",
    },
)
