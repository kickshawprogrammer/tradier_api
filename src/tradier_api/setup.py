from setuptools import setup, find_packages

setup(
    name="tradier_api",  # Match the directory name for consistency
    version="0.1.0",
    description="A Python API wrapper for the Tradier API",
    author="Kickshaw Programmer",
    license="Feel free to use in any way you wish; but please, be kind and do good!",
    packages=find_packages(include=["tradier_api", "tradier_api.*"]),
    install_requires=[
        "requests>=2.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
