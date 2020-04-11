CREATE TABLE AuthorReference (
	Refno int NOT NULL ,
	Name varchar2 (100) NOT NULL ,
	NameOrder smallint NOT NULL 
);

CREATE TABLE Cytogen (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	Sex char (1) NULL ,
	Age smallint NULL ,
	Race char (1) NULL ,
	Series char (1) NULL ,
	Country char (4) NULL ,
	PrevTum char (1) NULL ,
	PrevMorph varchar2 (20) NULL ,
	PrevTopo varchar2 (20) NULL ,
	PrevTreat varchar2 (255) NULL ,
	HerDis char (3) NULL ,
	SpecHerDis varchar2 (100) NULL ,
	Morph varchar2 (20) NULL ,
	SpecMorph varchar2 (100) NULL ,
	Topo varchar2 (20) NULL ,
	Immunology char (1) NULL ,
	SpecObs varchar2 (255) NULL ,
	Origin char (1) NULL
);

CREATE TABLE CytogenInv (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	InvDate varchar2 (8) NULL ,
	Tissue varchar2 (10) NULL ,
	Clones smallint NULL ,
	KaryLength smallint NULL ,
	KaryShort varchar2 (255) NULL ,
	KaryLong varchar2(4000) NULL
)
;

CREATE TABLE KaryAbnorm (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Abnormality varchar2 (100) NOT NULL 
)
;

CREATE TABLE KaryBit (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Bit varchar2 (255) NOT NULL 
)
;

CREATE TABLE KaryBreak (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Breakpoint varchar2 (10) NOT NULL 
)
;

CREATE TABLE KaryClone (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	ChromoMin smallint NOT NULL ,
	ChromoMax smallint NOT NULL ,
	CloneShort varchar2 (255) NOT NULL ,
	CloneLong varchar2(4000) NULL ,
	CloneLength int NOT NULL ,
	SoleAbnorm char (1) NULL
)
;

CREATE TABLE Koder (
	Kod varchar2 (16) NOT NULL ,
	KodTyp varchar2 (16) NOT NULL ,
	Aktiv char (1) NOT NULL ,
	Intern char (1) NULL ,
	Benamning varchar2 (255) NOT NULL ,
	Kortnamn varchar2 (30) NULL ,
	Notering varchar2 (255) NULL 
)
;

CREATE TABLE MolBiolClinAssoc (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	Morph varchar (20) NULL ,
	Top varchar (20) NULL ,
	Immunology char (1) NULL ,
	GeneLength smallint NULL ,
	GeneShort varchar (255) NULL ,
	GeneLong varchar2(4000) NULL ,
	KaryLength smallint NULL ,
	KaryShort varchar (255) NULL ,
	KaryLong varchar2(4000) NULL 
);

CREATE TABLE MolClinAbnorm (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Abnormality varchar (100) NOT NULL 
);

CREATE TABLE MolClinBreak (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Breakpoint varchar (10) NOT NULL 
);

CREATE TABLE MolClinGene (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Prefix char (2) ,
	Gene varchar (16) NOT NULL ,
	Suffix char (2) 
);

CREATE TABLE Reference (
	Refno NUMBER(9) NOT NULL ,
	TitleLength NUMBER(5) NULL ,
	TitleShort varchar2 (255) NULL ,
	TitleLong varchar2(4000) NULL ,
	Volume varchar2 (20) NULL ,
	Year NUMBER(4) NULL ,
	Journal varchar2 (255) NULL ,
	Text varchar2(4000) NULL ,
	Abbreviation varchar2 (100) NULL ,
	AuthorsLength NUMBER(5) NULL ,
	AuthorsShort varchar2 (255) NULL ,
	AuthorsLong varchar2(4000) NULL ,
	Flag varchar2 (1) NULL,
	PubMed NUMBER 
)
;

CREATE TABLE RECURRENT_DATA (
   CHROMOSOME                                         VARCHAR2(5) ,
   ARM                                                VARCHAR2(2) ,
   BAND                                               NUMBER ,
   ABERRATION                                         VARCHAR2(100) ,
   CODE                                               VARCHAR2(10) ,
   ORGAN                                              VARCHAR2(10) ,
   TOTAL_CASES                                        VARCHAR2(5) ,
   GENE                                               VARCHAR2(100) ,
   CHR_ORDER                                          NUMBER ,
   TYPE                                               CHAR(1)
)
;

CREATE TABLE RECURRENT_NUM_DATA (
   CHROMOSOME                                         VARCHAR2(5) ,
   ABNORMALITY                                        VARCHAR2(5) ,
   CODE                                               VARCHAR2(10) ,
   ORGAN                                              VARCHAR2(10) ,
   TOTAL_CASES                                        VARCHAR2(5) ,
   CHR_ORDER                                          NUMBER
)
;