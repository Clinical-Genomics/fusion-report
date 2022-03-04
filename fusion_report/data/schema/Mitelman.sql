CREATE TABLE AUTHREF (
	Refno int NOT NULL ,
	Name varchar2 (100) NOT NULL ,
	NameOrder smallint NOT NULL 
)
;

CREATE TABLE CYTINV (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	InvDate varchar2 (8) NULL ,
	Tissue varchar2 (10) NULL ,
	Clones smallint NULL ,
	KaryLength smallint NULL ,
	KaryShort varchar2 (255) NULL ,
	KaryLong varchar2(4000) NULL ,
	CaseOrder varchard (200) NULL
)
;

CREATE TABLE CYTOGEN (
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
	Origin varchar2 (20) NULL
)
;


CREATE TABLE CYTOVAL (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	KaryLength smallint NULL ,
	KaryShort varchar (255) NULL ,
	KaryLong varchar2(4000) NULL ,
	Message varchar2 (4000) NULL ,
	Reason varchar2 (4000) NULL 
)
;

CREATE TABLE KABNORM (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Abnormality varchar2 (100) NOT NULL 
)
;

CREATE TABLE KBIT (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Bit varchar2 (255) NOT NULL 
)
;

CREATE TABLE KBREAK (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Breakpoint varchar2 (10) NOT NULL 
)
;

CREATE TABLE KCLONE (
	RefNo int NOT NULL ,
	CaseNo varchar2 (14) NOT NULL ,
	InvNo smallint NOT NULL ,
	CloneNo smallint NOT NULL ,
	ChromoMin smallint NOT NULL ,
	ChromoMax smallint NOT NULL ,
	CloneShort varchar2 (255) NOT NULL ,
	CloneLong varchar2(4000) NULL ,
	CloneLength int NOT NULL ,
	Sole char (1) NULL
)
;

CREATE TABLE KODER (
	Kod varchar2 (16) NOT NULL ,
	KodTyp varchar2 (16) NOT NULL ,
	Aktiv char (1) NOT NULL ,
	Intern char (1) NULL ,
	Benamning varchar2 (255) NOT NULL ,
	Kortnamn varchar2 (30) NULL ,
	Notering varchar2 (255) NULL ,
	Inregdatum varchar2 (255) NULL ,
	GiltigFran varchar2 (255) NULL ,
	GiltigTill varchar2 (255) NULL ,
	Flagga1 varchar2 (255) NULL ,
	Flagga2 varchar2 (255) NULL ,
	Flagga3 varchar2 (255) NULL ,
	Flagga4 varchar2 (255) NULL 
)
;

CREATE TABLE MBCA (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	Morph varchar (20) NULL ,
	Topo varchar (20) NULL ,
	Immunology char (1) NULL ,
	GeneLength smallint NULL ,
	GeneShort varchar (255) NULL ,
	GeneLong varchar2(4000) NULL ,
	KaryLength smallint NULL ,
	KaryShort varchar (255) NULL ,
	KaryLong varchar2(4000) NULL 
)
;

CREATE TABLE MCABNORM (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Abnormality varchar (100) NOT NULL 
)
;

CREATE TABLE MCBREAK (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Breakpoint varchar (10) NOT NULL 
)
;

CREATE TABLE MCGENE (
	MolClin char (1) NOT NULL ,
	RefNo int NOT NULL ,
	InvNo smallint NOT NULL ,
	OrderNo smallint NOT NULL ,
	Prefix char (2) ,
	Gene varchar (16) NOT NULL ,
	Suffix char (2)
)
;

CREATE TABLE RECAB (
	Chromosome varchar (255) NULL ,
	Arm varchar (255) NULL ,
	Band varchar (255) NULL ,
	Abnormality varchar (255) NULL ,
	Morph varchar (255) NULL ,
	Topo varchar (255) NULL ,
	TotalCases varchar (255) NULL ,
	Gene varchar (255) NULL ,
	ChrOrder varchar (255) NULL ,
	Type varchar (255) NULL
)
;

CREATE TABLE RECABNUM (
	Chromosome varchar (255) NULL ,
	Abnormality varchar (255) NULL ,
	Morph varchar (255) NULL ,
	Topo varchar (255) NULL ,
	TotalCases varchar (255) NULL ,
	ChrOrder varchar (255) NULL
)
;

CREATE TABLE REF (
	Refno NUMBER(9) NOT NULL ,
	TitleLength NUMBER(5) NULL ,
	TitleShort varchar2 (255) NULL ,
	TitleLong varchar2(4000) NULL ,
	Volume varchar2 (20) NULL ,
	Year NUMBER(4) NULL ,
	Journal varchar2 (255) NULL ,
	Text varchar2(4000) NULL ,
	Abbreviation varchar2 (255) NULL ,
	AuthorsLength NUMBER(5) NULL ,
	AuthorsShort varchar2 (255) NULL ,
	AuthorsLong varchar2(4000) NULL ,
	Flag varchar2 (1) NULL,
	PubMed varchar2 (255) NULL
)
;