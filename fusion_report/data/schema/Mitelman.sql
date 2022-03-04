CREATE TABLE "MBCA" (
	"MolClin" char (1) NOT NULL ,
	"RefNo" int NOT NULL ,
	"InvNo" smallint NOT NULL ,
	"Morph" varchar (20) NULL ,
	"Topo" varchar (20) NULL ,
	"Immunology" char (1) NULL ,
	"GeneLength" smallint NULL ,
	"GeneShort" varchar (255) NULL ,
	"GeneLong" varchar2(4000) NULL ,
	"KaryLength" smallint NULL ,
	"KaryShort" varchar (255) NULL ,
	"KaryLong" varchar2(4000) NULL 
);