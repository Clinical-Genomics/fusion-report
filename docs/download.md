# Download resources

Currently the tool supports three different databases:

* [FusionGDB2](https://compbio.uth.edu/FusionGDB2/tables)
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