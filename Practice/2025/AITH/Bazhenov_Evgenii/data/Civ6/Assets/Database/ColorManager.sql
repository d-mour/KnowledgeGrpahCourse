
PRAGMA user_version = 1;
 
CREATE TABLE 'Colors'(
	'Type' TEXT NOT NULL,
	'Color' TEXT NOT NULL,
	PRIMARY KEY('Type')
);

CREATE TABLE 'PlayerColors'(
	'Type' TEXT NOT NULL, 
	'Usage' TEXT NOT NULL, 
	'PrimaryColor' TEXT NOT NULL, 
	'SecondaryColor' TEXT NOT NULL, 
	'Alt1PrimaryColor' TEXT,
	'Alt1SecondaryColor' TEXT,
	'Alt2PrimaryColor' TEXT,
	'Alt2SecondaryColor' TEXT,
	'Alt3PrimaryColor' TEXT,
	'Alt3SecondaryColor' TEXT,
	PRIMARY KEY ('Type')
);