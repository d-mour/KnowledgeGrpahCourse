
-- Categories used to partition and organize.
CREATE TABLE 'StatisticCategories' (
	'Category'	TEXT NOT NULL,
	'Name'	TEXT,
	'IsHidden' BOOLEAN NOT NULL DEFAULT 0,
	'SortOrder'	INTEGER NOT NULL DEFAULT 100,
	PRIMARY KEY('Category')
);

CREATE TABLE 'StatisticCategoryRulesetOverrides' (
	'RulesetType' TEXT NOT NULL,
	'Category'	TEXT NOT NULL,
	'Name'	TEXT,
	'IsHidden' BOOLEAN NOT NULL DEFAULT 0,
	'SortOrder'	INTEGER NOT NULL DEFAULT 100,
	PRIMARY KEY('RulesetType','Category')
);

-- Definition of various statistics shown.
CREATE TABLE 'Statistics' (
	'DataPoint'	TEXT NOT NULL,
	'Name'	TEXT,
	'Icon'	TEXT,
	'ValueIconDefault' TEXT,
	'ValueIconOverride' TEXT,
	'Annotation'	TEXT,
	'Direction'	INTEGER NOT NULL DEFAULT 0,
	'Category'	TEXT NOT NULL,
	'Importance'	INTEGER NOT NULL DEFAULT 0,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY ('DataPoint'),
	FOREIGN KEY('Category') REFERENCES 'StatisticCategories'('Category') ON DELETE SET NULL ON UPDATE SET NULL
);

CREATE TABLE 'StatisticRulesetOverrides' (
	'RulesetType' TEXT NOT NULL,
	'DataPoint'	TEXT NOT NULL,
	'Name'	TEXT,
	'Icon'	TEXT,
	'ValueIconDefault' TEXT,
	'ValueIconOverride' TEXT,
	'Annotation'	TEXT,
	'Direction'	INTEGER NOT NULL DEFAULT 0,
	'Category'	TEXT NOT NULL,
	'Importance'	INTEGER NOT NULL DEFAULT 0,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY ('RulesetType', 'DataPoint'),
	FOREIGN KEY('Category') REFERENCES 'StatisticCategories'('Category') ON DELETE SET NULL ON UPDATE SET NULL
);

-- Accolades attributed to comparisons of data points.
CREATE TABLE 'Highlights' (
	'DataPoint'	TEXT NOT NULL,
	'Name'	TEXT NOT NULL,
	'Caption'	TEXT NOT NULL,
	'Icon'	TEXT,
	'MinValue'	NUMERIC,
	'MaxValue'	NUMERIC,
	'Importance'	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY('DataPoint','Name')
);

-- These are named SQL queries for defining aggregate data point scopes.
-- These queries are fed the following named parameters:
-- @ExtraData - The extra field passed in by DataPointAggregateScopes rows.
CREATE TABLE 'DataPointAggregateScopeQueries' (
	'Query'	TEXT,
	'SQL'	TEXT,
	PRIMARY KEY('Query')
);

-- These are scopes that define all entries that "may" contain the aggregate data point.
-- Aggregate updates enumerate all rows in a scope and perform the specified operation.
-- Scopes differ from aggregate queries in that the row returned by the scope is the item 
-- that contains the data point while the query is all of the items that are fed into the 
-- operation that generates the value of the data point.
CREATE TABLE 'DataPointAggregateScopes' (
	'Scope' TEXT NOT NULL,
	'Query'	TEXT,
	'ExtraData' TEXT,
	'SortIndex' INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY('Scope'),
	FOREIGN KEY('Query') REFERENCES 'DataPointAggregateScopeQueries'('Query') ON DELETE CASCADE ON UPDATE CASCADE
);

-- These are named SQL queries for defining sets used by aggregate data points.
-- These queries are fed the following named parameters:
-- @ObjectId - The player or object id.
-- @GameId - The game id.
-- @Ruleset - The ruleset.
-- @DataPoint - A data point passed in by DataPointAggregateUpdates rows.
-- @ExtraData - The extra field passed in by DataPointAggregateUpdates rows.
CREATE TABLE 'DataPointAggregateQueries' (
	'Query'	TEXT,
	'SQL'	TEXT,
	PRIMARY KEY('Query')
);

-- These are definitions for populating data points using a set of existing data points and some predefined operation.
-- The scope may either be 'Global', 'Game' or 'Player'.
-- Values are calculated by 'Player', then 'Game', then 'Global'
CREATE TABLE 'DataPointAggregateUpdates' (
	'AggregateDataPoint'	TEXT NOT NULL,
	'Scope'	TEXT NOT NULL,
	'Operation'	TEXT NOT NULL,
	'Query'	TEXT,
	'DataPoint' TEXT,
	'ExtraData' TEXT,
	'SortIndex' INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY('AggregateDataPoint', 'Scope'),
	FOREIGN KEY('Scope') REFERENCES 'DataPointAggregateScopes'('Scope') ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY('Query') REFERENCES 'DataPointAggregateQueries'('Query') ON DELETE CASCADE ON UPDATE CASCADE
);

-- These are named SQL queries for defining sets used by graphs.
-- These queries are fed the following named parameters:
-- @ObjectId - The player or object id.
-- @GameId - The game id.
-- @Ruleset - The ruleset. (only provided in 'Ruleset' scope)
-- @DataSet - The value of Dataset from the graph row.
-- @ExtraData - The extra field passed in by the graph row.
-- These queries are expected to return one or more of the following columns:
-- DataSetId | ObjectId | Type | [IsDelta]
CREATE TABLE 'GraphQueries' (
	'Query'	TEXT,
	'SQL'	TEXT,
	PRIMARY KEY('Query')
);

CREATE TABLE 'Graphs' (
	'Graph' TEXT NOT NULL,
	'Scope'	TEXT NOT NULL,
	'Name'	TEXT NOT NULL,
	'Description'	TEXT,
	'Direction'	INTEGER NOT NULL DEFAULT 0,
	'XLabel'	TEXT,
	'YLabel'	TEXT,
	'XUnit'	TEXT,
	'YUnit' TEXT,
	'Query'	TEXT NOT NULL,
	'DataSet'	TEXT,
	'ExtraData' TEXT,
	'UxHint' TEXT,
	'Importance'	INTEGER NOT NULL DEFAULT 0,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY ('Graph', 'Scope')
);

CREATE TABLE 'GraphRulesetOverrides' (
	'RulesetType' TEXT NOT NULL,
	'Graph' TEXT NOT NULL,
	'Scope'	TEXT NOT NULL,
	'Name'	TEXT NOT NULL,
	'Description'	TEXT,
	'Direction'	INTEGER NOT NULL DEFAULT 0,
	'XLabel'	TEXT,
	'YLabel'	TEXT,
	'XUnit'	TEXT,
	'YUnit' TEXT,
	'Query'	TEXT NOT NULL,
	'DataSet'	TEXT,
	'ExtraData' TEXT,
	'UxHint' TEXT,
	'Importance'	INTEGER NOT NULL DEFAULT 0,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY ('RulesetType', 'Graph', 'Scope')
);

-- These are named SQL queries for defining sets used by reports.
-- These queries are fed the following named parameters:
-- @ObjectId - The player or object id.
-- @GameId - The game id.
-- @Ruleset - The ruleset. (Note: only provided in ruleset-scoped queries).
-- @ExtraData - The extra field passed in by the Report row.
-- These queries are expected to return one or more of the following columns:
-- Type
-- GameId
-- ObjectId
CREATE TABLE 'ReportQueries' (
	'Query'	TEXT,
	'SQL'	TEXT,
	PRIMARY KEY('Query')
);

-- Reports represent tables where each row is an object and each column is a data point.
-- These reports are dynamically created so that modders may add extra columns or re-arrange things.
CREATE TABLE 'Reports' (
	'Report'	TEXT NOT NULL,
	'Scope'	TEXT NOT NULL,
	'Name'	TEXT NOT NULL,
	'Description'	TEXT,
	'InitialColumnName' TEXT,
	'InitialColumnDescription' TEXT,
	'InitialColumnUxHint' TEXT,
	'InitialColumnValueIconDefault' TEXT,
	'InitialColumnValueIconOverride' TEXT,
	'ShowEmptyRows' BOOLEAN NOT NULL DEFAULT 0,	
	'Query'	TEXT NOT NULL,
	'ExtraData' TEXT,
	'Importance'	INTEGER NOT NULL DEFAULT 0,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY('Report'),
	FOREIGN KEY('Query') REFERENCES 'ReportQueries'('Query') ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE 'ReportRulesetOverrides' (
	'RulesetType' TEXT NOT NULL,
	'Report'	TEXT NOT NULL,
	'Scope'	TEXT NOT NULL,
	'Name'	TEXT NOT NULL,
	'Description'	TEXT,
	'InitialColumnName' TEXT,
	'InitialColumnDescription' TEXT,
	'InitialColumnUxHint' TEXT,
	'InitialColumnValueIconDefault' TEXT,
	'InitialColumnValueIconOverride' TEXT,
	'ShowEmptyRows' BOOLEAN NOT NULL DEFAULT 0,	
	'Query'	TEXT NOT NULL,
	'ExtraData' TEXT,
	'Importance'	INTEGER NOT NULL DEFAULT 0,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY('RulesetType','Report'),
	FOREIGN KEY('Query') REFERENCES 'ReportQueries'('Query') ON DELETE CASCADE ON UPDATE CASCADE
);

-- Report columns represent individual columns in the report.
-- If there are no datapoint values for any of the rows in the column, then the column is not displayed.
CREATE TABLE 'ReportColumns' (
	'Report'	TEXT NOT NULL,
	'Name'	TEXT NOT NULL,
	'Description'	TEXT,
	'SortOrder'	INTEGER NOT NULL DEFAULT 100,
	'DataPoint'	TEXT NOT NULL,
	'UxHint'	TEXT,
	'Minor' BOOLEAN NOT NULL DEFAULT 0,
	'AlwaysShow' BOOLEAN NOT NULL DEFAULT 0,
	'EmptyValue' TEXT,
	'DefaultValue' TEXT,
	'ValueIconDefault' TEXT,
	'ValueIconOverride' TEXT,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY('Report','Name'),
	FOREIGN KEY('Report') REFERENCES 'Reports'('Report') ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE 'ReportColumnRulesetOverrides' (
	'RulesetType' TEXT NOT NULL,
	'Report'	TEXT NOT NULL,
	'Name'	TEXT NOT NULL,
	'Description'	TEXT,
	'SortOrder'	INTEGER NOT NULL DEFAULT 100,
	'DataPoint'	TEXT NOT NULL,
	'UxHint'	TEXT,
	'Minor' BOOLEAN NOT NULL DEFAULT 0,
	'AlwaysShow' BOOLEAN NOT NULL DEFAULT 0,
	'EmptyValue' TEXT,
	'DefaultValue' TEXT,
	'ValueIconDefault' TEXT,
	'ValueIconOverride' TEXT,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	PRIMARY KEY('RulesetType','Report','Name'),
	FOREIGN KEY('Report') REFERENCES 'Reports'('Report') ON DELETE CASCADE ON UPDATE CASCADE
);

