
CREATE TABLE 'Queries' (
	'QueryId' TEXT NOT NULL,
	'SQL' TEXT NOT NULL,
 	PRIMARY KEY('QueryId')
);

CREATE TABLE 'QueryCriteria'(
	'QueryId' TEXT NOT NULL,
	'ConfigurationGroup' TEXT NOT NULL,
	'ConfigurationId' TEXT NOT NULL,
	'Operator' TEXT NOT NULL DEFAULT 'Equals',
	'ConfigurationValue',
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'QueryParameters'(
	'QueryId' TEXT NOT NULL,
	'Index' INTEGER NOT NULL,
	'ConfigurationGroup' TEXT NOT NULL,
	'ConfigurationId' TEXT NOT NULL,
	PRIMARY KEY('QueryId', 'Index'),
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'ParameterQueries'(
	'ParameterQueryId' TEXT NOT NULL,
	'QueryId' TEXT NOT NULL,
	'ParameterIdField' TEXT NOT NULL DEFAULT 'ParameterId',
	'NameField' TEXT NOT NULL DEFAULT 'Name',
	'DescriptionField' TEXT NOT NULL DEFAULT 'Description',
	'DomainField' TEXT NOT NULL DEFAULT 'Domain',
	'HashField' TEXT NOT NULL DEFAULT 'Hash',
	'ArrayField' TEXT NOT NULL DEFAULT 'Array',
	'DefaultValueField' TEXT NOT NULL DEFAULT 'DefaultValue',
	'ConfigurationGroupField' TEXT NOT NULL DEFAULT 'ConfigurationGroup',
	'ConfigurationIdField' TEXT NOT NULL DEFAULT 'ConfigurationId',
	'DomainConfigurationIdField' TEXT NOT NULL DEFAULT 'DomainConfigurationId',
	'DomainValuesConfigurationIdField' TEXT NOT NULL DEFAULT 'DomainValuesConfigurationId',
	'ValueNameConfigurationIdField' TEXT NOT NULL DEFAULT 'ValueNameConfigurationId',
	'ValueDomainConfigurationIdField' TEXT NOT NULL DEFAULT 'ValueDomainConfigurationId',
	'NameArrayConfigurationIdField' TEXT NOT NULL DEFAULT 'NameArrayConfigurationId',
	'GroupField' TEXT NOT NULL DEFAULT 'GroupId',
	'VisibleField' TEXT NOT NULL DEFAULT 'Visible',
	'ReadOnlyField' TEXT NOT NULL DEFAULT 'ReadOnly',
	'SupportsSinglePlayerField' TEXT NOT NULL DEFAULT 'SupportsSinglePlayer',
	'SupportsLANMultiplayerField' TEXT NOT NULL DEFAULT 'SupportsLANMultiplayer',
	'SupportsInternetMultiplayerField' TEXT NOT NULL DEFAULT 'SupportsInternetMultiplayer',
	'SupportsHotSeatField' TEXT NOT NULL DEFAULT 'SupportsHotSeat',
	'SupportsPlayByCloudField' TEXT NOT NULL DEFAULT 'SupportsPlayByCloud',
	'ChangeableAfterGameStartField' TEXT NOT NULL DEFAULT 'ChangeableAfterGameStart',
	'ChangeableAfterPlayByCloudMatchCreateField' TEXT NOT NULL DEFAULT 'ChangeableAfterPlayByCloudMatchCreate',
	'UxHintField' TEXT NOT NULL DEFAULT 'UxHint',
	'SortIndexField' TEXT NOT NULL DEFAULT 'SortIndex',
	PRIMARY KEY('ParameterQueryId'),
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'ParameterQueryCriteria'(
	'ParameterQueryId' TEXT NOT NULL,
	'ConfigurationGroup' TEXT NOT NULL,
	'ConfigurationId' TEXT NOT NULL,
	'Operator' TEXT NOT NULL DEFAULT 'Equals',
	'ConfigurationValue'
);

CREATE TABLE 'ParameterQueryDependencies'(
	'ParameterQueryId' TEXT NOT NULL,
	'ConfigurationGroup' TEXT NOT NULL,
	'ConfigurationId' TEXT NOT NULL,
	'Operator' TEXT NOT NULL DEFAULT 'Equals',
	'ConfigurationValue'
);

CREATE TABLE 'Parameters'(
	'Key1' TEXT,
	'Key2' TEXT,
	'ParameterId' TEXT NOT NULL,								-- A semi-unique identifier of the parameter.  Semi-unique because it depends on Key1 and Key2.
	'Name' TEXT NOT NULL,										-- The name of the parameter.
	'Description' TEXT,											-- The description of the parameter (used for UI purposes, typically a tooltip).
	'Domain' TEXT NOT NULL,										-- The domain of values to use
	'Hash' BOOLEAN NOT NULL DEFAULT 0,							-- Whether or not to hash the value when writing to the config.  Only applies to the value, not other config entries.
	'Array' BOOLEAN NOT NULL DEFAULT 0,							-- Whether or not the value of the parameter is an array of 0-N values.
	'DefaultValue',												-- The default value to use, null allowed.
	'ConfigurationGroup' TEXT NOT NULL,							-- The map used to write all of the configuration values (e.g Game, Map, Player[id])
	'ConfigurationId' TEXT NOT NULL,							-- The key used to write out the value of the parameter.
	'DomainConfigurationId' TEXT,								-- [Optional] Write out the parameter's domain to the configuration.
	'DomainValuesConfigurationId' TEXT,							-- [Optional] Write out a comma delimited list of all values (including original domain).  This only applies to name-value domains.					
	'ValueNameConfigurationId' TEXT,							-- [Optional] Write out the name of the value as a localization bundle.	This only applies to name-value domains.
	'ValueDomainConfigurationId' TEXT,							-- [Optional] Write out the original domain of the selected value. (This may not match the parameter's domain).
	'NameArrayConfigurationId' TEXT,							-- [Optional] Include the name of the parameter in a comma delimited list so long as the value is not false or null.
	'GroupId' TEXT NOT NULL,									-- Used by the UI to determine how to triage the parameter.
	'Visible' BOOLEAN NOT NULL DEFAULT 1,						-- Used by the UI to determine whether the parameter should be shown.  Parameter dependencies may override this.
	'ReadOnly' BOOLEAN NOT NULL DEFAULT 0,						-- Used by the UI to determine whether the parameter should be disabled. Parameter criteria may override this.
	'SupportsSinglePlayer' BOOLEAN NOT NULL DEFAULT 1,
	'SupportsLANMultiplayer' BOOLEAN NOT NULL DEFAULT 1,
	'SupportsInternetMultiplayer' BOOLEAN NOT NULL DEFAULT 1,
	'SupportsHotSeat' BOOLEAN NOT NULL DEFAULT 1,
	'SupportsPlayByCloud' BOOLEAN NOT NULL DEFAULT 1,			-- This parameter is supported by the PlayByCloud mode.
	'ChangeableAfterGameStart' BOOLEAN NOT NULL DEFAULT 0,
	'ChangeableAfterPlayByCloudMatchCreate' BOOLEAN NOT NULL DEFAULT 1,	-- Is this a parameter that can be changed after a PlayByCloud match is created.
	'UxHint' TEXT,												-- This column 'suggests' what kind of Ux should be used to display it. (e.x. 'SimpleSelectPanel', 'MultiSelectPanel').
	'SortIndex' INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE 'ParameterCriteriaQueries'(
	'QueryId' TEXT NOT NULL,
	'ParameterIdField' TEXT NOT NULL DEFAULT 'ParameterId',
	'ConfigurationGroupField' TEXT NOT NULL DEFAULT 'ConfigurationGroup',
	'ConfigurationIdField' TEXT NOT NULL DEFAULT 'ConfigurationId',
	'OperatorField' TEXT NOT NULL DEFAULT 'Operator',
	'ConfigurationValueField' TEXT NOT NULL DEFAULT 'ConfigurationValue'
);

CREATE TABLE 'ParameterCriteria'(
	'ParameterId' TEXT NOT NULL,
	'ConfigurationGroup' TEXT NOT NULL,
	'ConfigurationId' TEXT NOT NULL,
	'Operator' TEXT NOT NULL DEFAULT 'Equals',
	'ConfigurationValue'
);

CREATE TABLE 'ParameterDependencyQueries'(
	'QueryId' TEXT NOT NULL,
	'ParameterIdField' TEXT NOT NULL DEFAULT 'ParameterId',
	'ConfigurationGroupField' TEXT NOT NULL DEFAULT 'ConfigurationGroup',
	'ConfigurationIdField' TEXT NOT NULL DEFAULT 'ConfigurationId',
	'OperatorField' TEXT NOT NULL DEFAULT 'Operator',
	'ConfigurationValueField' TEXT NOT NULL DEFAULT 'ConfigurationValue'
);

CREATE TABLE 'ParameterDependencies'(
	'ParameterId' TEXT NOT NULL,
	'ConfigurationGroup' TEXT NOT NULL,
	'ConfigurationId' TEXT NOT NULL,
	'Operator' TEXT NOT NULL DEFAULT 'Equals',
	'ConfigurationValue'
);

CREATE TABLE 'DomainRangeQueries'(
	'QueryId' TEXT NOT NULL,
	'DomainField' TEXT NOT NULL DEFAULT 'Domain',
	'MinimumValueField' TEXT NOT NULL DEFAULT 'MinimumValue',
	'MaximumValueField' TEXT NOT NULL DEFAULT 'MaximumValue',
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'DomainRanges'(
	'Domain' TEXT NOT NULL,
	'MinimumValue' INT NOT NULL DEFAULT 0,
	'MaximumValue' INT NOT NULL
);

CREATE TABLE 'DomainOverrideQueries'(
	'QueryId' TEXT NOT NULL,
	'ParameterIdField' TEXT NOT NULL DEFAULT 'ParameterId',
	'DomainField' TEXT NOT NULL DEFAULT 'Domain',
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'DomainOverrides'(
	'Key1' TEXT,
	'Key2' TEXT,
	'ParameterId' TEXT,
	'DomainOverride' TEXT NOT NULL
);

CREATE TABLE 'DomainValueQueries'(
	'QueryId' TEXT NOT NULL,
	'DomainField' TEXT NOT NULL DEFAULT 'Domain',
	'ValueField' TEXT NOT NULL DEFAULT 'Value',
	'NameField' TEXT NOT NULL DEFAULT 'Name',
	'DescriptionField' TEXT NOT NULL DEFAULT 'Description',
	'IconField' TEXT NOT NULL DEFAULT 'Icon',
	'SortIndexField' TEXT NOT NULL DEFAULT 'SortIndex',
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'DomainValues'(
	'Key1' TEXT,
	'Key2' TEXT,
	'Domain' TEXT NOT NULL,
	'Value' NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT,
	'Icon' TEXT,
	'SortIndex' INTEGER NOT NULL DEFAULT 100,
	PRIMARY KEY('Key1','Key2','Domain','Value')
);

-- Include the values of 'OtherDomain' into the values of 'Domain'
CREATE TABLE 'DomainValueUnionQueries'(
	'QueryId' TEXT NOT NULL,
	'DomainField' TEXT NOT NULL DEFAULT 'Domain',
	'OtherDomainField' TEXT NOT NULL DEFAULT 'OtherDomain',
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'DomainValueUnions'(
	'Key1' TEXT,
	'Key2' TEXT,
	'Domain' TEXT NOT NULL,
	'OtherDomain' TEXT NOT NULL,
	PRIMARY KEY('Key1','Key2','Domain','OtherDomain')
);

CREATE TABLE 'DomainValueFilterQueries'(
	'QueryId' TEXT NOT NULL,
	'DomainField' TEXT NOT NULL DEFAULT 'Domain',
	'ValueField' TEXT NOT NULL DEFAULT 'Value',
	'FilterField' TEXT NOT NULL DEFAULT 'Filter',
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'DomainValueFilters'(
	'Key1' TEXT,
	'Key2' TEXT,
	'Domain' TEXT NOT NULL,
	'Value' NOT NULL,
	'Filter' TEXT NOT NULL,
	PRIMARY KEY('Key1','Key2','Domain','Value')
);

-- Indirect method of populating recursive configuration updates.
CREATE TABLE 'ConfigurationUpdateQueries'(
	'QueryId' TEXT NOT NULL,
	'SourceGroupField' TEXT NOT NULL DEFAULT 'SourceGroup',
	'SourceIdField' TEXT NOT NULL DEFAULT 'SourceId',
	'SourceValueField' TEXT NOT NULL DEFAULT 'SourceValue',
	'TargetGroupField' TEXT NOT NULL DEFAULT 'TargetGroup',
	'TargetIdField' TEXT NOT NULL DEFAULT 'TargetId',
	'TargetValueField' TEXT NOT NULL DEFAULT 'TargetValue',
	'HashField' TEXT NOT NULL DEFAULT 'Hash',
	'StaticField' TEXT NOT NULL DEFAULT 'Static',
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

-- When a setup parameter writes to the configuration..
-- Recursively match to the source rows and write the target values.
CREATE TABLE 'ConfigurationUpdates'(
	'Key1' TEXT,
	'Key2' TEXT,
	'SourceGroup' TEXT NOT NULL,
	'SourceId' TEXT NOT NULL,
	'SourceValue' NOT NULL,
	'TargetGroup' TEXT NOT NULL,
	'TargetId' TEXT NOT NULL,
	'TargetValue',
	'Hash' BOOLEAN NOT NULL DEFAULT 0,
	'Static' BOOLEAN NOT NULL DEFAULT 0
);
