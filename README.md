# ![fusion-report](https://raw.githubusercontent.com/matq007/fusion-report/master/fusion_report/templates/assets/img/fusion-report.png)

[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/fusion-report/README.html)
![build](https://github.com/matq007/fusion-report/workflows/CI%20%5Bmaster%5D/badge.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/932dff8661394cc28448af7b22748bb5)](https://app.codacy.com/app/mproksik/fusion-report?utm_source=github.com&utm_medium=referral&utm_content=matq007/fusion-report&utm_campaign=Badge_Grade_Dashboard)
[![DOI](https://zenodo.org/badge/173453958.svg)](https://zenodo.org/badge/latestdoi/173453958)
[![Slack Status](https://img.shields.io/badge/slack-join-brightgreen)](https://nf-co.re/join/slack)

This python script generates an interactive summary report from fusion detection tools. Fusion-report is part of a bigger project [nf-core/rnafusion](https://github.com/nf-core/rnafusion) which is designed to detect and report fusion genes from RNA-seq data.

> **TL;DR**: Live demo [here](https://matq007.github.io/fusion-report/example).

## Supported tools

* [STAR-Fusion](https://github.com/STAR-Fusion/STAR-Fusion)
* [EricScript](https://sites.google.com/site/bioericscript/)
* [Pizzly](https://github.com/pmelsted/pizzly)
* [Squid](https://github.com/Kingsford-Group/squid)
* [Dragen](https://emea.illumina.com/products/by-type/informatics-products/dragen-bio-it-platform.html)
* [Arriba](https://github.com/suhrig/arriba)
* [Illumina Dragen](https://emea.illumina.com/products/by-type/informatics-products/dragen-bio-it-platform.html)

## Installation

### Using Conda

```bash
conda install -c bioconda fusion-report=2.0.2
```

### From source

```bash
sudo apt-get install sqlite3 wget
python3 setup.py install
```

## Usage

```bash
# Download required databases
# Currently supported databases: FusionGDB, Mitelman and COSMIC
# COSMIC requires login credentials to download Fusion gene Database
fusion_report download --cosmic_usr '<username>' --cosmic_passwd '<password>' /path/to/db/

# Run the fusion-report
fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/ \
  --arriba tests/test_data/arriba.tsv \
  --dragen tests/test_data/dragen.tsv \
  --ericscript tests/test_data/ericscript.tsv \
  --fusioncatcher tests/test_data/fusioncatcher.txt \
  --pizzly tests/test_data/pizzly.tsv \
  --squid tests/test_data/squid.txt \
  --starfusion tests/test_data/starfusion.tsv
```

Or get help and list all possible parameters.

```bash
fusion_report --help
fusion_report run --help
fusion_report download --help
```

For more info on how to run the script, please see the [documentation](https://matq007.github.io/fusion-report/).

## Credits

* Testing dataset copied from [ndaniel/fusioncatcher](https://github.com/ndaniel/fusioncatcher).
* DNA icon made by [Freepik](https://www.freepik.com) from [Flaticon](https://www.flaticon.com) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/).
