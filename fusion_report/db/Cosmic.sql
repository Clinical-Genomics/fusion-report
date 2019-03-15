CREATE TABLE "CosmicFusionExport" (
	"sample_id" integer NOT NULL,
	"sample_name" varchar(50) NOT NULL DEFAULT '',
	"primary_site" varchar(50) NOT NULL DEFAULT '',
	"site_subtype_1" varchar(50) NOT NULL DEFAULT '',
	"site_subtype_2" varchar(50) NOT NULL DEFAULT '',
    "site_subtype_3" varchar(50) NOT NULL DEFAULT '',
	"primary_histology" varchar(50) NOT NULL DEFAULT '',
    "histology_subtype_1" varchar(50) NOT NULL DEFAULT '',
    "histology_subtype_2" varchar(50) NOT NULL DEFAULT '',
    "histology_subtype_3" varchar(50) NOT NULL DEFAULT '',
    "fusion_id" integer NOT NULL,
    "translocation_name" varchar(50) NOT NULL DEFAULT '',
    "translocation_type" varchar(50) NOT NULL DEFAULT '',
    "pubmed" integer NOT NULL,
    "id_study" integer NOT NULL
);

.separator "\t"
.import CosmicFusionExport_stripped.tsv CosmicFusionExport