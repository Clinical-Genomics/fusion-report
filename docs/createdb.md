# Create databases from local files

The `createdb` command lets you build fusion databases from local files without downloading them. This is useful when:

- You have pre-downloaded database files from institutional sources
- You want to use a specific COSMIC version without providing credentials each time
- You need to build databases in an air-gapped or offline environment
- You want to rebuild databases from custom or filtered data files

## Usage

Provide at least one database file. Only the databases for which files are supplied will be created.

### Build all three databases

```bash
fusion_report createdb /path/to/db \
    --cosmic <Cosmic_Fusion_vXXX_GRChYY.tsv.gz> \
    --mitelman mitelman_db.zip \
    --fusiongdb2 combinedFGDB2genes_genes_ID_04302024.txt
```

### Build only COSMIC

```bash
fusion_report createdb /path/to/db \
    --cosmic <Cosmic_Fusion_vXXX_GRChYY.tsv.gz>
```

### Build Mitelman + FusionGDB2 (no COSMIC credentials needed)

```bash
fusion_report createdb /path/to/db \
    --mitelman mitelman_db.zip \
    --fusiongdb2 combinedFGDB2genes_genes_ID_04302024.txt
```

## Supported file formats

| Database | Accepted formats | Notes |
|----------|-----------------|-------|
| **COSMIC** | `.tsv.gz` or `.tsv` | COSMIC Fusion Export file (gzipped or plain). Download from [COSMIC](https://cancer.sanger.ac.uk/cosmic/download) or the respective Qiagen (commercial case) sources |
| **Mitelman** | `.zip` or extracted `MBCA.TXT.DATA` | Mitelman database archive. Download from [Mitelman](https://mitfrednlm.nih.gov). |
| **FusionGDB2** | `.txt` or `.csv` | FusionGDB2 gene-ID table (headerless 6-column TSV) or a pre-processed CSV with one fusion per line (`GENE1--GENE2`). Download from [FusionGDB2](https://compbio.uth.edu/FusionGDB/combined_tables/combinedFGDB2genes_genes_ID_04302024.txt). |

## Comparison: `download` vs `createdb`

| Feature | `download` | `createdb` |
|---------|-----------|-----------|
| Downloads files automatically | Yes | No |
| Requires COSMIC credentials | Yes (unless `--no-cosmic`) | No |
| Works offline | No | Yes |
| Custom file versions | No (uses version in settings) | Yes |
| Selective DB creation | Via `--no-*` flags | Only builds what you provide |

## Output

The command creates `.db` files and a `DB-timestamp.txt` file in the output directory:

```
/path/to/db/
├── cosmic.db           # if --cosmic provided
├── mitelman.db         # if --mitelman provided
├── fusiongdb2.db       # if --fusiongdb2 provided
└── DB-timestamp.txt
```

These databases can then be used with `fusion_report run`:

```bash
fusion_report run "sample" /path/to/output /path/to/db/ \
    --starfusion starfusion.tsv \
    --arriba arriba.tsv
```

## All parameters

```bash
fusion_report createdb --help
```
