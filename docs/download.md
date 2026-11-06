# Download resources

> If you already have the database files locally, you can use [`fusion_report createdb`](createdb.md) to build databases without downloading.

Currently the tool supports three different databases:

* [FusionGDB2](https://compbio.uth.edu/FusionGDB/combined_tables/combinedFGDB2genes_genes_ID_04302024.txt)
* [Mitelman](https://cgap.nci.nih.gov/Chromosomes/Mitelman)
* [COSMIC](https://cancer.sanger.ac.uk/cosmic/fusion)

You can download the databases running:

```bash
fusion_report download
    --cosmic_usr '<username>'
    --cosmic_passwd '<password>'
    /path/to/db
```

With a non-academic/research login -> using QIAGEN with a commercial license:

```bash
fusion_report download
    --cosmic_usr '<QIAGEN username>'
    --cosmic_passwd 'QIAGEN <password>'
    --qiagen
    /path/to/db
```

You can exclude a specific database with --no-cosmic/--no-mitelman/--no-fusiongdb2. Exemple for no cosmic:

```bash
fusion_report download
    --no-cosmic
    /path/to/db
```


## Troubleshooting

`download` validates every file before using it: HTTP errors, HTML pages served instead of data (for example when a source has moved or blocks automated downloads), files of the wrong type and truncated downloads all fail with a message that names the source. Transient errors (HTTP 429/5xx) are retried with backoff. Each database is downloaded independently, so one failing source does not stop the others, and the databases that succeeded are kept.

* **COSMIC and Mitelman are required** unless you pass `--no-cosmic`/`--no-mitelman`: if one of them fails, `download` exits with an error.
* **FusionGDB2 is optional**: it does not contribute to the [Fusion Indication Index](score.md), so if it cannot be downloaded a warning is shown and the other databases are still written. `run` skips a missing `fusiongdb2.db` with a warning as well.

### FusionGDB2 is not downloadable

The FusionGDB2 website (compbio.uth.edu) currently blocks automated downloads, see [#100](https://github.com/Clinical-Genomics/fusion-report/issues/100). The dataset itself is frozen (April 2024). Options:

* skip it with `--no-fusiongdb2` (no effect on scoring), or
* obtain `combinedFGDB2genes_genes_ID_04302024.txt` manually and build the database with `fusion_report createdb /path/to/db --fusiongdb2 combinedFGDB2genes_genes_ID_04302024.txt`. The original file has 98,154 rows and the sha256 checksum `c09b637b17e461d66cec869d8f083049647a5ee1a34d438d88df2af57d53278f`.

### SSL certificate errors

SSL certificates are verified by default. Behind a proxy that intercepts TLS, point `REQUESTS_CA_BUNDLE` at your organisation's CA bundle, or, as a last resort, turn verification off with `--no-ssl`.

### Full error details

Errors are shown as a single message. Add `--debug` before the command (`fusion_report --debug download ...`) to see the full traceback.

## Manual download

### Mitelman

Website: [https://cgap.nci.nih.gov/Chromosomes/Mitelman](https://cgap.nci.nih.gov/Chromosomes/Mitelman)

```bash
wget ftp://ftp1.nci.nih.gov/pub/CGAP/mitelman.tar.gz -O mitelman.tar.gz
tar -xvzf mitelman.tar.gz
for db_file in *.dat ; do
    # Remove the header
    sed -n '1!p' $db_file > "${db_file%.*}_stripped.dat"
    rm $db_file
done
# Create database and import the data
sqlite3 cosmic.db < fusion_report/db/Mitelman.sql
```

### COSMIC

Website: [https://cancer.sanger.ac.uk/cosmic/fusion](https://cancer.sanger.ac.uk/cosmic/fusion)

```bash
PASSWD=`echo "<username>:<password> | base64"`
URL=`curl -H "Authorization: Basic ${PASSWD}" https://cancer.sanger.ac.uk/cosmic/file_download/GRCh38/cosmic/v87/CosmicFusionExport.tsv.gz | jq .url`
curl $URL
sed -n '1!p' CosmicFusionExport.tsv > CosmicFusionExport_stripped.tsv
rm CosmicFusionExport.tsv
# Create database and import the data
sqlite3 cosmic.db < fusion_report/db/Cosmic.sql
```
