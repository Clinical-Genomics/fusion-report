# Fusion report

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
bin/fusion-report --help
```

![Example summary report](docs/images/example-summary-report.png)