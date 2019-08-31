# Running the tool

> Before running the tool make sure you have downloaded all the necessary resources!

## Run all fusion detection tools
   
```bash
fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/
  --arriba tests/test_data/arriba.tsv
  --ericscript tests/test_data/ericscript.tsv
  --starfusion tests/test_data/starfusion.tsv
  --fusioncatcher tests/test_data/fusioncatcher.txt
  --squid tests/test_data/squid.txt
  --pizzly tests/test_data/pizzly.tsv
  --dragen tests/test_data/dragen.tsv
```

## Set a custom weight for tool

Each tool has a predefined weight when estimating score of a fusion. On default all tools have an equal weight
`(100 / NUMBER_OF_RUNNING_TOOLS)`. To change the weights follow the steps below:

```bash
fusion_report run "<SAMPLE NAME>" /path/to/output /path/to/db/
  --ericscript tests/test_data/ericscript.tsv
  --ericscript_weight 30.5
  --fusioncatcher tests/test_data/fusioncatcher.txt
  --fusioncatcher_weight 70.5
```

## All parameters and options

```bash
fusion_report --help
fusion_report run --help
fusion_report download --help
```