# Fusion report

[![Build Status](https://travis-ci.org/matq007/fusion-report.svg?branch=master)](https://travis-ci.org/matq007/fusion-report)
[![MIT License](https://img.shields.io/github/license/matq007/fusion-report.svg)](https://github.com/matq007/fusion-report/blob/master/LICENSE)

**Live demo [here](https://matq007.github.io/fusion-report/example/).**

This is a python script for generating interactive summary report from output of fusion detection tools.
Currently tools below are supported:

* STAR-Fusion
* EricScript
* FusionCatcher
* Pizzly
* Squid
* Arriba (coming)

Fusion-report is part of a bigger project [nf-core/rnafusion](https://github.com/nf-core/rnafusion) which a pipeline
for detecting fusion genes from RNA-seq data. Running the script is simple, just type:

```bash
fusion_report --help
```

## Installation

```bash
python3 setup.py install
```
