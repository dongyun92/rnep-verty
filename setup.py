from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rnep-verty",
    version="1.0.0",
    author="Verty",
    author_email="contact@verty.com",
    description="Risk and Noise Evaluation Platform for UAM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dongyun92/rnep-verty",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rnep=rnep.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rnep": ["data/aircraft/*.json"],
    },
)