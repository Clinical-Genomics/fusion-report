CREATE TABLE "MBCA" (
	"molclin" char (1) NOT NULL ,
	"refno" int NOT NULL ,
	"invno" smallint NOT NULL ,
	"morph" varchar (20) NULL ,
	"topo" varchar (20) NULL ,
	"immunology" char (1) NULL ,
	"geneLength" smallint NULL ,
	"geneshort" varchar (255) NULL ,
	"genelong" varchar2(4000) NULL ,
	"karylength" smallint NULL ,
	"karyshort" varchar (255) NULL ,
	"karylong" varchar2(4000) NULL
);
