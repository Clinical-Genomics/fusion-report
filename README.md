# ![fusion-report](https://raw.githubusercontent.com/matq007/fusion-report/master/docs/_src/_static/fusion-report.png)

[![Build Status](https://travis-ci.org/matq007/fusion-report.svg?branch=master)](https://travis-ci.org/matq007/fusion-report)
[![MIT License](https://img.shields.io/github/license/matq007/fusion-report.svg)](https://github.com/matq007/fusion-report/blob/master/LICENSE)
[![Slack Status](https://nf-core-invite.herokuapp.com/badge.svg)](https://nf-core-invite.herokuapp.com)

This python script generates an interactive summary report from fusion detection tools. Fusion-report is part of a bigger project [nf-core/rnafusion](https://github.com/nf-core/rnafusion) which is designed to detect and report fusion genes from RNA-seq data.

> **TL;DR**: Live demo [here](https://matq007.github.io/fusion-report/example).

## Supported tools

* [STAR-Fusion](https://github.com/STAR-Fusion/STAR-Fusion)
* [EricScript](https://sites.google.com/site/bioericscript/)
* [Pizzly](https://github.com/pmelsted/pizzly)
* [Squid](https://github.com/Kingsford-Group/squid)
* [Arriba](https://github.com/suhrig/arriba) (coming soon)

## Installation

```bash
python3 setup.py install
```

## Usage

```bash
fusion_report "<SAMPLE NAME>" /path/to/output /path/to/db/ 
  --ericscript tests/test_data/ericscript.tsv 
  --starfusion tests/test_data/starfusion.tsv 
  --fusioncatcher tests/test_data/fusioncatcher.txt
  --squid tests/test_data/squid.txt 
  --pizzly tests/test_data/pizzly.tsv
```

Or get help and list all possible parameters.

```bash
fusion_report --help
```

For more info on how to run the script, please see the [documentation](https://matq007.github.io/fusion-report/).

## Credits

DNA icon made by [Freepik](https://www.freepik.com) from [Flaticon](https://www.flaticon.com) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/).