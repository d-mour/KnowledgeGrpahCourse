-- Additional Configuration Tables.
-- These are tables that are not directly used by the configuration logic
-- But are referenced in queries.
-- These tables are intended to make it easier to supply additional values or
-- restrict domains without significant SQL work.
CREATE TABLE 'Credits'(
	'Package' TEXT NOT NULL,
	'DisplayName' TEXT NOT NULL,
	'Credits' TEXT NOT NULL,
	'SortOrder' INTEGER NOT NULL DEFAULT 0
);

-- Stores references to main menu logos.  
-- The row with the highest priority is shown.
CREATE TABLE 'Logos'(
	'LogoTexture' TEXT NOT NULL,
	'LogoMovie' TEXT NOT NULL,
	'Priority' INTEGER NOT NULL
);

CREATE TABLE 'Defeats'(
	'Domain' TEXT NOT NULL DEFAULT 'StandardDefeats',
	'DefeatType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT NOT NULL,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	'ReadOnly' TEXT NOT NULL DEFAULT 0
);

CREATE TABLE 'Difficulties' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardDifficulties',
	'DifficultyType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'SortIndex' INTEGER NOT NULL,
	PRIMARY KEY('Domain', 'DifficultyType')
);

CREATE TABLE 'Eras' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardEras',
	'EraType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT NOT NULL,
	'SortIndex' INTEGER NOT NULL,
	PRIMARY KEY('Domain', 'EraType')
);

CREATE TABLE 'GameCores'(
	'GameCore' TEXT NOT NULL,
	'PackageId' TEXT,
	'DllPrefix' TEXT NOT NULL,
	PRIMARY KEY('GameCore')
);

CREATE TABLE 'GameModeItems' (
	'GameModeType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT,
	'Icon' TEXT,
	'UnitIcon' TEXT,
	'UnitDescription' TEXT,
	'UnitName' TEXT,
	'Portrait' TEXT,
	'Background' TEXT,
	'SortIndex' INTEGER DEFAULT 0
);


-- This table can be used to provide simple overrides to players for when certain game modes are active.
-- This table is not referenced directly but rather by a 'Query'.  For more complex overrides (such as when multiple modes are active but another mode is inactive)
-- an additional query can be created that has the additional necessary criteria.
-- These are applied by sorting the final set ascending by priority and overriding values with any non-null value.
CREATE TABLE 'GameModePlayerInfoOverrides' (
	'GameModeType' TEXT NOT NULL,
	'Domain' TEXT NOT NULL DEFAULT 'Players:StandardPlayers',
	'CivilizationType' TEXT NOT NULL,
	'LeaderType' TEXT NOT NULL,
	'LeaderAbilityName' TEXT,
	'LeaderAbilityDescription' TEXT,
	'LeaderAbilityIcon' TEXT,
	'CivilizationAbilityName' TEXT,
	'CivilizationAbilityDescription' TEXT,
	'CivilizationAbilityIcon' TEXT,
	'Priority' INTEGER DEFAULT 0,
	PRIMARY KEY('GameModeType', 'Domain', 'CivilizationType', 'LeaderType')
);

-- This table can be used to provide simple overrides to player items for when certain game modes are active.
-- This table is not referenced directly but rather by a 'Query'.  For more complex overrides (such as when multiple modes are active but another mode is inactive)
-- an additional query can be created that has the additional necessary criteria.
-- These are applied by sorting the final set ascending by priority and overriding values with any non-null value.
-- A special value 'ShouldRemove' is initialized to false.  If after going through the set, 'ShouldRemove' is true, then the row is deleted.
CREATE TABLE 'GameModePlayerItemOverrides' (
	'GameModeType' TEXT NOT NULL,
	'Domain' TEXT NOT NULL DEFAULT 'Players:StandardPlayers',
	'CivilizationType' TEXT NOT NULL,
	'LeaderType' TEXT NOT NULL,
	'Type' TEXT NOT NULL,
	'Name' TEXT,
	'Description' TEXT,
	'Icon' TEXT,
	'SortIndex' INTEGER,
	'ShouldRemove' BOOLEAN NOT NULL DEFAULT 0,
	'Priority' INTEGER DEFAULT 0,
	PRIMARY KEY('GameModeType', 'Domain', 'CivilizationType', 'LeaderType', 'Type')
);

CREATE TABLE 'GameSpeeds' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardGameSpeeds',
	'GameSpeedType' TEXT NOT NULL,
	'Name' TEXT,
	'Description' TEXT,
	'SortIndex' INTEGER NOT NULL,
	PRIMARY KEY('Domain', 'GameSpeedType')
);

CREATE TABLE 'Maps' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardMaps',
	'File' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT,
	'Image' TEXT,
	'StaticMap' BOOLEAN NOT NULL DEFAULT 0,
	'WorldBuilderOnly' BOOLEAN NOT NULL DEFAULT 0,
	'RequiresUniqueLeaders' BOOLEAN NOT NULL DEFAULT 0,
	'DisableWorldWrap' BOOLEAN NOT NULL DEFAULT 0,
	'SortIndex' INTEGER NOT NULL DEFAULT 10,
	PRIMARY KEY ('Domain', 'File')
);

-- This is similar to MapSupportedValues but is leader specific and domain agnostic.
CREATE TABLE 'MapLeaders' (
	'Map' TEXT NOT NULL,		-- A reference to Maps::File
	'LeaderType' TEXT NOT NULL,	-- A leader type (ignoring domain)
	PRIMARY KEY ('Map', 'LeaderType')
);

CREATE TABLE 'MapStartPositions' (
	'Map' TEXT NOT NULL,		-- A reference to Maps::File
	'Plot' INTEGER NOT NULL,
	'Type' TEXT NOT NULL,
	'Value' TEXT
);

CREATE TABLE 'MapSizes' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardMapSizes',
	'MapSizeType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT,
	'MinPlayers' INTEGER NOT NULL DEFAULT 2,
	'MaxPlayers' INTEGER NOT NULL DEFAULT 2,
	'DefaultPlayers' INTEGER NOT NULL DEFAULT 2,
	'MinCityStates' INTEGER NOT NULL DEFAULT 0,
	'MaxCityStates' INTEGER NOT NULL DEFAULT 0,
	'DefaultCityStates' INTEGER NOT NULL DEFAULT 0,
	'SortIndex' INTEGER NOT NULL,
	PRIMARY KEY('Domain','MapSizeType')
);

CREATE TABLE 'NaturalWonders' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardNaturalWonders',
	'FeatureType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT,
	'Icon' TEXT,
	'SortIndex' INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ('Domain','FeatureType')
);

CREATE TABLE 'CityStates' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardCityStates',
	'CivilizationType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Icon' TEXT NOT NULL,
	'CityStateCategory' TEXT NOT NULL,
	'Bonus' TEXT NOT NULL,
	'Bonus_XP1' TEXT,
	'Bonus_XP2' TEXT,
	'SortIndex' INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY ('Domain','CivilizationType')
);

CREATE TABLE 'Rulesets' (
	'RulesetType' TEXT NOT NULL,
 	'Name' TEXT NOT NULL,
	'Description' TEXT,
	'LongDescription' TEXT,
	'DefeatDomain' TEXT NOT NULL DEFAULT 'StandardDefeats',
	'VictoryDomain' TEXT NOT NULL DEFAULT 'StandardVictories',
	'MaxTurns' INTEGER,
	'FixedMaxTurns' BOOLEAN NOT NULL DEFAULT 0,
	'SupportsSinglePlayer' BOOLEAN NOT NULL DEFAULT 1,
	'SupportsMultiPlayer' BOOLEAN NOT NULL DEFAULT 1,
	'SupportsHotSeat' BOOLEAN NOT NULL DEFAULT 1,
	'SupportsPlayByCloud' BOOLEAN NOT NULL DEFAULT 1,
	'SortIndex' INTEGER NOT NULL DEFAULT 100,
	'IsScenario' BOOLEAN NOT NULL DEFAULT 0,
	'RequiresNoTeams' BOOLEAN NOT NULL DEFAULT 0,
	'RequiresUniqueCivilizations' BOOLEAN NOT NULL DEFAULT 0,
	'RequiresUniqueLeaders' BOOLEAN NOT NULL DEFAULT 0,
	'ScenarioSetupPortrait' TEXT,
	'ScenarioSetupPortraitBackground' TEXT,
	'GameCore' TEXT NOT NULL DEFAULT 'Base',
	PRIMARY KEY('RulesetType')
);

-- List of types for a given ruleset.
CREATE TABLE 'RulesetTypes' (
	'Ruleset' TEXT NOT NULL,
	'Type' TEXT NOT NULL,
	'Kind' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Icon' TEXT,
	PRIMARY KEY('Ruleset','Type'),
	FOREIGN KEY('Ruleset') REFERENCES 'Rulesets'('RulesetType') ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE 'Players' (
	'Domain' TEXT DEFAULT 'Players:StandardPlayers',
	'CivilizationType' TEXT NOT NULL,
	'LeaderType' TEXT NOT NULL,
	'LeaderName' TEXT NOT NULL,
	'LeaderIcon' TEXT NOT NULL,
	'CivilizationName' TEXT NOT NULL,
	'CivilizationIcon' TEXT NOT NULL,
	'LeaderAbilityName' TEXT NOT NULL,
	'LeaderAbilityDescription' TEXT NOT NULL,
	'LeaderAbilityIcon' TEXT NOT NULL,
	'CivilizationAbilityName' TEXT NOT NULL,
	'CivilizationAbilityDescription' TEXT NOT NULL,
	'CivilizationAbilityIcon' TEXT NOT NULL,
	'Portrait' TEXT,
	'PortraitBackground' TEXT,
	'PlayerColor' TEXT,
	'HumanPlayable' BOOLEAN NOT NULL DEFAULT 1,
	'SortIndex' INTEGER,
	PRIMARY KEY('Domain', 'CivilizationType', 'LeaderType')
);

CREATE TABLE 'PlayerInfoOverrideQueries'(
	'QueryId' TEXT NOT NULL,
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'PlayerItems' (
	'Domain' TEXT DEFAULT 'Players:StandardPlayers',
	'CivilizationType' TEXT NOT NULL,
	'LeaderType' TEXT NOT NULL,
	'Type' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT NOT NULL,
	'Icon' TEXT NOT NULL,
	'SortIndex' INTEGER DEFAULT 0,
	PRIMARY KEY('Domain', 'CivilizationType', 'LeaderType', 'Type')
);

CREATE TABLE 'PlayerItemOverrideQueries' (
	'QueryId' TEXT NOT NULL,
	FOREIGN KEY('QueryId') REFERENCES 'Queries'('QueryId')
);

CREATE TABLE 'DuplicateLeaders' (
	'Domain' TEXT DEFAULT 'Players:StandardPlayers',
	'LeaderType' TEXT NOT NULL,
	'OtherLeaderType' TEXT NOT NULL
);

CREATE TABLE 'DuplicateCivilizations' (
	'Domain' TEXT DEFAULT 'Players:StandardPlayers',
	'CivilizationType' TEXT NOT NULL,
	'OtherCivilizationType' TEXT NOT NULL
);

CREATE TABLE 'TurnTimers' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardTurnTimers',
	'TurnTimerType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT NOT NULL,
	'SortIndex' INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE 'TurnPhases' (
	'Domain' TEXT NOT NULL DEFAULT 'StandardTurnPhases',
	'TurnPhaseType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT NOT NULL,
	'SortIndex' INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE 'Victories'(
	'Domain' TEXT NOT NULL DEFAULT 'StandardVictories',
	'VictoryType' TEXT NOT NULL,
	'Name' TEXT NOT NULL,
	'Description' TEXT NOT NULL,
	'Icon' TEXT,
	'Visible' BOOLEAN NOT NULL DEFAULT 1,
	'ReadOnly' BOOLEAN NOT NULL DEFAULT 0,
	'EnabledByDefault' BOOLEAN NOT NULL DEFAULT 1
);

-- Rulesets are pretty much the only thing which replaces domains.
CREATE TABLE 'MapDomainOverrides'(
	'Map' TEXT NOT NULL,				-- The map file
	'PlayerId' INTEGER,					-- Optional: The player slot.
	'ParameterId' TEXT NOT NULL,		-- The parameterId to replace the domain.
	'Domain' TEXT NOT NULL				-- The new domain.  This is a REPLACEMENT not a Union.
);

CREATE TABLE 'RulesetDomainOverrides'(
	'Ruleset' TEXT NOT NULL,			-- The ruleset type.
	'PlayerId' INTEGER,					-- Optional: The player slot.
	'ParameterId' TEXT NOT NULL,		-- The parameterId to replace the domain.
	'Domain' TEXT NOT NULL				-- The new domain.  This is a REPLACEMENT not a Union.
);

-- These tables are meant to restrict domains, rather than replace them.
-- Restriction is done via set intersecting.
-- Restrict parameter values based on what map is selected.
CREATE TABLE 'MapSupportedValues'(
	'Map' TEXT NOT NULL,				-- The primary key of Maps.
	'PlayerId' INTEGER,					-- Optional: The player slot.
	'Domain' TEXT NOT NULL,				-- The domain of the value.
	'Value' TEXT NOT NULL				-- The domain value to intersect with.
);

CREATE TABLE 'MapUnSupportedValues'(
	'Map' TEXT NOT NULL,				-- The primary key of Maps.
	'PlayerId' INTEGER,					-- Optional: The player slot.
	'Domain' TEXT NOT NULL,				-- The domain of the value.
	'Value' TEXT NOT NULL				-- The domain value to intersect with.
);

CREATE TABLE 'RulesetSupportedValues'(
	'Ruleset' TEXT NOT NULL,			-- The ruleset type.
	'PlayerId' INTEGER,					-- Optional: The player slot.
	'Domain' TEXT NOT NULL,				-- The domain of the value.
	'Value' TEXT NOT NULL				-- The domain value to intersect with.
);

CREATE TABLE 'RulesetUnSupportedValues'(
	'Ruleset' TEXT NOT NULL,			-- The ruleset type.
	'PlayerId' INTEGER,					-- Optional: The player slot.
	'Domain' TEXT NOT NULL,				-- The domain of the value.
	'Value' TEXT NOT NULL				-- The domain value to intersect with.
);


