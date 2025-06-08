from setuptools import setup, find_packages
import os
import re

# Read version from _version.py
with open(os.path.join('smartflow', '_version.py'), 'r') as f:
    version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in _version.py")

setup(
    name="smartflow",
    version=version,
    packages=find_packages(),
    description="SmartFlow Workflow Engine by Gradient Momentum",
    author="Jeremy Sublett",
    author_email="jeremy@gradientmomentum.com",
    install_requires=[
        "pydantic",
        "pyyaml",
        "azure-storage-blob",
        "azure-data-tables",
        "azure-servicebus",
        "azure-core",
        "python-dotenv",
    ],
    python_requires=">=3.8",
)