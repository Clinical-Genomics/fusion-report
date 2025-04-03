CREATE TABLE "cosmic_fusion_v101_grch38" (
	"COSMIC_SAMPLE_ID" integer NOT NULL,
	"SAMPLE_NAME" varchar(50) NOT NULL DEFAULT '',
	"COSMIC_PHENOTYPE_ID" varchar(50) NOT NULL DEFAULT '',
	"COSMIC_FUSION_ID" varchar(50) NOT NULL DEFAULT '',
	"FUSION_SYNTAX" varchar(50) NOT NULL DEFAULT '',
    "FIVE_PRIME_CHROMOSOME" varchar(50) NOT NULL DEFAULT '',
	"FIVE_PRIME_STRAND" varchar(50) NOT NULL DEFAULT '',
    "FIVE_PRIME_TRANSCRIPT_ID" varchar(50) NOT NULL DEFAULT '',
    "FIVE_PRIME_GENE_SYMBOL" varchar(50) NOT NULL DEFAULT '',
    "FIVE_PRIME_LAST_OBSERVE_EXON" varchar(50) NOT NULL DEFAULT '',
    "FIVE_PRIME_GENOME_START_FROM" integer NOT NULL,
    "FIVE_PRIME_GENOME_START_TO" varchar(50) NOT NULL DEFAULT '',
    "FIVE_PRIME_GENOME_STOP_FROM" varchar(50) NOT NULL DEFAULT '',
    "FIVE_PRIME_GENOME_STOP_TO" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_CHROMOSOME" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_STRAND" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_TRANSCRIPT_ID" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_GENE_SYMBOL" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_FIRST_OBSERVE_EXON" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_GENOME_START_FROM" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_GENOME_START_TO" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_GENOME_STOP_FROM" varchar(50) NOT NULL DEFAULT '',
    "THREE_PRIME_GENOME_STOP_TO" varchar(50) NOT NULL DEFAULT '',
    "FUSION_TYPE" varchar(50) NOT NULL DEFAULT '',
    "PUBMED_PMID" varchar(50) NOT NULL DEFAULT ''
);
