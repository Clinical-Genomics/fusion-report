# Download resources

Currently the tool supports three different databases:

* [FusionGDB](https://ccsm.uth.edu/FusionGDB/index.html)
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


## Manual download

### FusionGDB

Website: [https://ccsm.uth.edu/FusionGDB/index.html](https://ccsm.uth.edu/FusionGDB/index.html)

```bash
# Download all files
wget --no-check-certificate https://ccsm.uth.edu/FusionGDB/tables/TCGA_ChiTaRS_combined_fusion_information_on_hg19.txt -O TCGA_ChiTaRS_combined_fusion_information_on_hg19.txt
wget --no-check-certificate https://ccsm.uth.edu/FusionGDB/tables/TCGA_ChiTaRS_combined_fusion_ORF_analyzed_gencode_h19v19.txt -O TCGA_ChiTaRS_combined_fusion_ORF_analyzed_gencode_h19v19.txt
wget --no-check-certificate https://ccsm.uth.edu/FusionGDB/tables/uniprot_gsymbol.txt -O uniprot_gsymbol.txt
wget --no-check-certificate https://ccsm.uth.edu/FusionGDB/tables/fusion_uniprot_related_drugs.txt -O fusion_uniprot_related_drugs.txt
wget --no-check-certificate https://ccsm.uth.edu/FusionGDB/tables/fusion_ppi.txt -O fusion_ppi.txt
wget --no-check-certificate https://ccsm.uth.edu/FusionGDB/tables/fgene_disease_associations.txt -O fgene_disease_associations.txt
# Create database and import the data
sqlite3 fusiongdb.db < fusion_report/db/FusionGDB.sql
```

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