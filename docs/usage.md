# Running the tool

> Before running the tool make sure you have downloaded all the necessary resources!

## Run all fusion detection tools

```bash
fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/ \
  --arriba tests/test_data/arriba.tsv \
  --ericscript tests/test_data/ericscript.tsv \
  --starfusion tests/test_data/starfusion.tsv \
  --fusioncatcher tests/test_data/fusioncatcher.txt \
  --squid tests/test_data/squid.txt \
  --pizzly tests/test_data/pizzly.tsv \
  --dragen tests/test_data/dragen.tsv \
  --allow-multiple-gene-symbols
```

## Multiple gene symbols

In case fusion gene symbol can't be uniquely determined some tools provide possible list of fusions. Each fusion tool handles this differently.
There are two options:

### Example case

Dummy fusion detected by Squid: `15	34347968	34348134	19	15254151	15254264	.	9	-	-	fusion-gene	BRD4:NUTM1,BRD4-1:NUTM1`.

1. Omitting `--allow-multiple-gene-symbols` will report **only** first fusion: `BRD4:NUTM1`.
2. Adding `--allow-multiple-gene-symbols` will treat each fusion as unique and report `BRD4:NUTM1` and `BRD4-1:NUTM1`.

## Set a custom weight for tool

Each tool has a predefined weight when estimating score of a fusion. On default all tools have an equal weight
`(100 / NUMBER_OF_RUNNING_TOOLS)`. To change the weights follow the steps below:

```bash
fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/ \
  --ericscript tests/test_data/ericscript.tsv \
  --ericscript_weight 30.5 \
  --fusioncatcher tests/test_data/fusioncatcher.txt \
  --fusioncatcher_weight 70.5
```

## All parameters and options

```bash
fusion_report --help
fusion_report run --help
fusion_report download --help
fusion_report sync --help
```
