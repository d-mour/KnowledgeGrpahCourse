-- Input Configuration
-- These tables are used to store available input actions.
CREATE TABLE 'InputCategories'(
	'CategoryId' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	'SortIndex' INTEGER NOT NULL DEFAULT 0,
	Primary Key('CategoryId')
);

CREATE TABLE 'InputContexts'(
	'ContextId' TEXT NOT NULL,
	'Value' INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY('ContextId')
);

CREATE TABLE 'InputActions'(
	'ActionId' TEXT NOT NULL,
	'Name' TEXT,
	'Description' TEXT,
	'CategoryId' TEXT NOT NULL,
	'ContextId' TEXT NOT NULL,
	'LayoutType' TEXT NOT NULL DEFAULT 'PC',
	PRIMARY KEY('ActionId'),
	FOREIGN KEY('CategoryId') REFERENCES 'InputCategories'('CategoryId') ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY('ContextId') REFERENCES 'InputContexts'('ContextId') ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE 'InputActionDefaultGestures' (
	'ActionId' TEXT NOT NULL,
	'Index' INTEGER NOT NULL,
	'GestureType' TEXT NOT NULL,
	'GestureData' TEXT NOT NULL,	
	PRIMARY KEY('ActionId', 'Index'),
	FOREIGN KEY('ActionId') REFERENCES 'InputActions'('ActionId')
);

CREATE TABLE 'InputKeyData' (
	'KeyId' TEXT NOT NULL,
	'KeyString' TEXT NOT NULL,
	'KeyIcon' TEXT NOT NULL,
	'KeyType' TEXT NOT NULL,
	PRIMARY KEY('KeyId')
);
