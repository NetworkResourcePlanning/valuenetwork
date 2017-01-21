PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
DROP TABLE "work_ocp_artwork_type";
CREATE TABLE "work_ocp_artwork_type" ("artwork_type_id" integer NOT NULL PRIMARY KEY REFERENCES "general_artwork_type" ("typ_id"), "facet_id" integer NULL UNIQUE REFERENCES "valueaccounting_facet" ("id"), "facet_value_id" integer NULL REFERENCES "valueaccounting_facetvalue" ("id"), "material_type_id" integer NULL REFERENCES "general_material_type" ("artwork_type_id"), "nonmaterial_type_id" integer NULL REFERENCES "general_nonmaterial_type" ("artwork_type_id"), "resource_type_id" integer NULL UNIQUE REFERENCES "valueaccounting_economicresourcetype" ("id"), "context_agent_id" integer NULL REFERENCES "valueaccounting_economicagent" ("id"));
INSERT INTO "work_ocp_artwork_type" VALUES(9,1,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(10,3,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(49,NULL,17,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(50,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(51,NULL,22,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(52,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(53,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(54,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(55,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(56,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(57,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(65,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(71,NULL,19,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(72,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(73,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(74,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(75,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(76,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(77,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(78,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(79,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(80,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(81,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(82,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(83,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(84,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(85,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(86,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(87,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(88,NULL,9,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(89,NULL,10,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(90,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(91,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(92,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(93,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(94,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(95,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(96,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(97,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(98,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(149,NULL,16,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(151,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(152,NULL,NULL,NULL,NULL,36,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(153,NULL,NULL,NULL,NULL,6,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(155,NULL,24,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(156,NULL,NULL,NULL,NULL,46,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(157,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(158,NULL,24,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(159,NULL,NULL,NULL,NULL,47,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(160,NULL,21,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(161,NULL,8,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(162,NULL,NULL,NULL,NULL,31,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(163,NULL,NULL,NULL,NULL,33,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(164,NULL,NULL,NULL,NULL,17,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(165,NULL,NULL,NULL,NULL,37,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(166,NULL,NULL,NULL,NULL,32,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(167,NULL,NULL,NULL,NULL,44,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(168,NULL,NULL,NULL,NULL,28,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(169,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(170,NULL,NULL,NULL,NULL,24,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(171,NULL,NULL,NULL,NULL,15,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(172,NULL,NULL,NULL,NULL,14,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(175,NULL,NULL,NULL,NULL,29,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(177,NULL,NULL,NULL,NULL,NULL,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(178,NULL,NULL,NULL,NULL,48,'context_agent_id');
INSERT INTO "work_ocp_artwork_type" VALUES(179,NULL,NULL,NULL,NULL,27,'context_agent_id');
CREATE INDEX "work_ocp_artwork_type_068969e6" ON "work_ocp_artwork_type" ("facet_value_id");
CREATE INDEX "work_ocp_artwork_type_bcca2c2a" ON "work_ocp_artwork_type" ("material_type_id");
CREATE INDEX "work_ocp_artwork_type_61e152a3" ON "work_ocp_artwork_type" ("nonmaterial_type_id");
CREATE INDEX "work_ocp_artwork_type_1bc0cee2" ON "work_ocp_artwork_type" ("context_agent_id");
COMMIT;

