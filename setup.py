from setuptools import find_packages, setup

PACKAGE_DATA = {"fusion_report": ["data/schema/*.sql" "arguments.json", "templates/*/*"]}

with open("README.md") as f:
    README = f.read()

with open("requirements.txt") as f:
    INSTALL_REQUIREMENTS = f.read().splitlines()

setup(
    name="fusion-report",
    python_requires=">=3.12",
    description="Tool for parsing outputs from fusion detection tools.",
    long_description=README,
    author="Martin Proks, Annick Renevey",
    url="https://github.com/Clinical-Genomics/fusion-report",
    license="GPL_v3",
    packages=find_packages(include=["fusion_report", "fusion_report.*"]),
    install_requires=INSTALL_REQUIREMENTS,
    zip_safe=False,
    scripts=["bin/fusion_report"],
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    package_data=PACKAGE_DATA,
    include_package_data=True,
)
