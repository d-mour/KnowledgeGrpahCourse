INSERT INTO "Languages" VALUES('zh_Hant_HK','汉语/漢語 (Traditional Chinese)',null,1,0);
INSERT INTO "Languages" VALUES('zh_Hans_CN','汉语/漢語 (Simplified Chinese)',null,1,0);

INSERT INTO "LanguagePriorities" VALUES('zh_Hans_CN','zh_Hans_CN',100);
INSERT INTO "LanguagePriorities" VALUES('zh_Hant_HK','zh_Hant_HK',100);

INSERT INTO "FontStyleSheets" VALUES('zh_Hans_CN','Civ6_FontStyles_zh_Hans_CN.xml', null, 'NotoSansCJKsc-Medium.otf');
INSERT INTO "FontStyleSheets" VALUES('zh_Hant_HK','Civ6_FontStyles_zh_Hant_HK.xml', null, 'NotoSansCJKtc-Medium.otf');

INSERT INTO "AudioLanguages" VALUES('Chinese(Taiwan)', 'zh_Hans_CN');
INSERT INTO "AudioLanguages" VALUES('Chinese(PRC)', 'zh_Hant_HK');

INSERT INTO "DefaultAudioLanguages" VALUES('zh_Hant_HK','Chinese(PRC)');
INSERT INTO "DefaultAudioLanguages" VALUES('zh_Hans_CN','Chinese(Taiwan)');
