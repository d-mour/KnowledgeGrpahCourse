-- Modding Framework Schema
-- 
-- Revision History
-- Version 24:
-- * No changes. Bumping to force a rebuild.
-- Version 23:
-- * Added 'SettingCriteria' to control how settings are applied.
-- * Added 'AdditionalScannedFiles' table to track additional files referenced by other files.
-- * Removed unused 'Exclusivity' column from Mods table.
-- Version 22:
-- * Added 'Disabled' to ModGroupItems effectively giving them a tri-state instead of just an enabled/disabled state.
-- Version 21:
-- * Added 'ModCompatibilityWhitelist' table for checking whether a mod should ignore compatibility warnings.
-- Version 20:
-- * Added 'Any' attribute to criteria for whether to match any of the criterion rather than all.
-- * Moved 'Inverse' from Criteria to individual Criterion.
-- Version 19:
-- * Added support for migrating data during an upgrade.
-- * Added 'Inverse' to Criteria.
-- Version 18:
-- * Removed stored procedures for listing paths.  These are now handled internally.
-- Version 17:
-- * Component associations to Criteria is many to many instead of many to 1.
-- * Components may now contain a list of Uris as well as Files.
-- * Updated ComponentRelationships to remove title (not needed) and add override which infers ignoring their criteria.
-- * Added ReverseDependency relationship type.
-- * Removed Components.CriteriaRowId
-- * Added ComponentCriteria
-- * Added ComponentReferences
-- Version 16:
-- * Removed Component and Setting type tables.
-- * Removed reliance on Make_Hash function.
-- * Added criteria structures.
-- * Added mod group structures.
-- Version 15:
-- * Added Icons setting and component types.
-- Version 14:
-- * Added ModArt setting type.
-- Version 13:
-- * Added UpdateARX component type.
-- Version 12: 
-- * Removed SettingComponents table.
-- * Modified stored procedures to order by priority in descending order.
-- Version 11:
-- * Added UpdateAudio component type.
-- Version 10:
-- * Added LocalizedText setting and component types.
-- Version 9:
-- * Added GameplayScripts, ImportFiles, and UserInterface component types.
-- Version 8:
-- * Removed Component and Setting type constraints.
-- Version 7:
-- * Add ModArt Component type.
-- Version 6:
-- * ComponentTypes and SettingTypes now use hashed identifiers instead of enumerations.
-- Version 5:
-- * Renamed Settings.SettingsId to Settings.SettingId.
-- * Added StoredProcedures table with many procedures used by the game.
-- Version 4:
-- * Brought Version back (integer for now, SemVer 2.0 in a future update).
-- * Removed BuildId.
-- * Removed SteamWorkshop tables (this info is stored in-memory now)."
-- Version 3:
-- * Removed CRC32 from ModFiles."
-- * Removed Version from Mods."
-- * Added BuildId in Mods."
-- Version 2:
--	* Added SettingComponents 
--	* Fixed order of dropped tables during cleanup.
-- Version 1:
--	* First pass

-- Generate Schema
-- Name/Value pairs representing framework settings.
CREATE TABLE SystemSettings(
	'Name' TEXT PRIMARY KEY NOT NULL, 
	'Value' TEXT
);

-- A table containing all of the files 'discovered' by the modding framework.
-- A locally unique identifier representing the file.
-- @ScannedFileRowId is the locally unique identifier to the file.
-- @Path is the path to the file.
-- @LastWriteTime represents the time stamp the file was written.  Used to invalidate mods and other data.
CREATE TABLE ScannedFiles(
	'ScannedFileRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
	'Path' TEXT UNIQUE, 
	'LastWriteTime' INTEGER NOT NULL
);

-- Track any additional files associated with a mod.
-- @ScannedFileRowId is the specific scanned file associated.
-- @Path is the path to the file.
-- @LastWriteTime represents the time stamp the file was written.  Used to invalidate mods and other data.
CREATE TABLE AdditionalScannedFiles(
	'ScannedFileRowId' INTEGER NOT NULL,
	'Path' TEXT NOT NULL, 
	'LastWriteTime' INTEGER NOT NULL,
	PRIMARY KEY(ScannedFileRowId, Path)
	FOREIGN KEY(ScannedFileRowId) REFERENCES ScannedFiles(ScannedFileRowId) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Primary table of all discovered mods
-- @ModRowId is a locally unique identifier representing a discovered mod.
-- @FileId is a reference to the .modinfo file discovered in ScannedFiles.
-- @ModId is a globally unique identifier representing the mod.
-- @Version is an integer value > 0.  Values of 0 or less are considered invalid.
-- @LastRetrieved is a times tamp for when the mod was discovered.
CREATE TABLE Mods(
	'ModRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	'ScannedFileRowId' INTEGER NOT NULL, 
	'ModId' TEXT NOT NULL,
	'Version' INTEGER NOT NULL,
	FOREIGN KEY(ScannedFileRowId) REFERENCES ScannedFiles(ScannedFileRowId) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Criteria
-- @CriteriaRowId is the unique id associated with the criteria.
-- @ModRowId is the specific mod associated with the criteria.
-- @CriteriaId is the user friendly identifier of the criteria.
CREATE TABLE Criteria(
	'CriteriaRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	'ModRowId' INTEGER NOT NULL,
	'CriteriaId' INTEGER NOT NULL,
	'Any' BOOLEAN NOT NULL DEFAULT 0,
	FOREIGN KEY ('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- Individual criterion of criteria.
-- @CriterionRowId is the unique id associated with the criterion
-- @CriteriaRowId is the criteria which the criterion is associated with.
-- @CriteriaType is the type of criterion.
CREATE TABLE Criterion(
	'CriterionRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	'CriteriaRowId' INTEGER NOT NULL,
	'CriterionType' TEXT NOT NULL,
	'Inverse' BOOLEAN NOT NULL DEFAULT 0,
	FOREIGN KEY ('CriteriaRowId') REFERENCES Criteria('CriteriaRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- Properties of a criterion
-- @CriteriaRowId is the criteria which the criterion is associated with
-- @Name is the name of the property.
-- @Value is the value of the property (as text).
CREATE TABLE CriterionProperties(
	'CriterionRowId' INTEGER NOT NULL, 
	'Name' TEXT NOT NULL, 
	'Value' TEXT NOT NULL, 
	PRIMARY KEY ('CriterionRowId', 'Name'), 
	FOREIGN KEY ('CriterionRowId') REFERENCES Criterion('CriterionRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- All components in a mod.
-- @ModRowId is the mod containing the component.
-- @ComponentRowId is the locally unique id of the component.
-- @ComponentId is the globally unique id of the component.
-- @ComponentType is the type of the component.
CREATE TABLE Components(
	'ComponentRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	'ModRowId' INTEGER NOT NULL,
	'ComponentId' TEXT,
	'ComponentType' TEXT NOT NULL,
	FOREIGN KEY('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);	

-- All settings in a mod.
-- @ModRowId is the mod containing the setting.
-- @SettingRowId is the locally unique id of the setting.
-- @SettingId is the globally unique id of the setting.
-- @SettingType is the type of the setting.
CREATE Table Settings(
	'SettingRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
	'ModRowId' INTEGER NOT NULL,
	'SettingId' TEXT,
	'SettingType' TEXT NOT NULL,
	FOREIGN KEY('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);
	
-- A manifest of all files contained in a mod.
-- @FileRowId represents a locally unique identifier to the specific file.
-- @ModRowId represents the specific mod instance this file is a member of.
-- @Path represents the relative path to the file from the .modinfo
-- @Relative represents the relative path to the modinfo file.
CREATE TABLE ModFiles(
	'FileRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	'ModRowId' INTEGER NOT NULL, 
	'Path' TEXT NOT NULL, 
	FOREIGN KEY ('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains all local file references of the component.
-- @ComponentRowId is the locally unique identifier referring to the mod setting.
-- @FileRowId is the locally unique identifier to the mod file.
-- @Priority is the order in which the files should be executed.
CREATE TABLE ComponentFiles(
	'ComponentRowId' INTEGER NOT NULL,
	'FileRowId' INTEGER NOT NULL,
	'Priority' INTEGER NOT NULL,
	PRIMARY KEY('ComponentRowId', 'FileRowId'),
	FOREIGN KEY('ComponentRowId') REFERENCES Components('ComponentRowId') ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY('FileRowId') REFERENCES ModFiles('FileRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains all universal references of the component.
-- @ComponentRowId is the locally unique identifier referring to the mod setting.
-- @URI is a mod resource identifier, used commonly to reference files and components in other mods.
-- @Priority is the order in which the files should be executed.
CREATE TABLE ComponentReferences(
	'ComponentRowId' INTEGER NOT NULL,
	'URI' TEXT NOT NULL,
	'Priority' INTEGER NOT NULL,
	PRIMARY KEY('ComponentRowId', 'URI'),
	FOREIGN KEY('ComponentRowId') REFERENCES Components('ComponentRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains criteria that must be met for the component to be applied.
-- @ComponentRowId is the locally unique identifier referring to the component.
-- @CriteriaRowId is the locally unique identifier referring to the criteria.
CREATE TABLE ComponentCriteria(
	'ComponentRowId' INTEGER NOT NULL,
	'CriteriaRowId' TEXT NOT NULL,
	PRIMARY KEY('ComponentRowId', 'CriteriaRowId'),
	FOREIGN KEY('ComponentRowId') REFERENCES Components('ComponentRowId') ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY('CriteriaRowId') REFERENCES Criteria('CriteriaRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains criteria that must be met for the setting to be applied.
-- @SettingRowId is the locally unique identifier referring to the setting.
-- @CriteriaRowId is the locally unique identifier referring to the criteria.
CREATE TABLE SettingCriteria(
	'SettingRowId' INTEGER NOT NULL,
	'CriteriaRowId' TEXT NOT NULL,
	PRIMARY KEY('SettingRowId', 'CriteriaRowId'),
	FOREIGN KEY('SettingRowId') REFERENCES Settings('SettingRowId') ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY('CriteriaRowId') REFERENCES Criteria('CriteriaRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains all file references in settings.
-- @SettingRowId is the locally unique identifier referring to the mod setting.
-- @FileRowId is the locally unique identifier to the mod file.
-- @Priority is the order in which the files should be executed.
CREATE TABLE SettingFiles(
	'SettingRowId' INTEGER NOT NULL,
	'FileRowId' INTEGER NOT NULL,
	'Priority' INTEGER NOT NULL,
	PRIMARY KEY('SettingRowId', 'FileRowId'),
	FOREIGN KEY('SettingRowId') REFERENCES Settings('SettingRowId') ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY('FileRowId') REFERENCES ModFiles('FileRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- Name/Value pair representing properties of a mod.
-- @ModRowId represents the specific mod instance this file is a member of.
-- @Name is the name of the property.
-- @Value is the value of the property.
CREATE TABLE ModProperties(
	'ModRowId' INTEGER NOT NULL, 
	'Name' TEXT NOT NULL, 
	'Value' TEXT, 
	PRIMARY KEY ('ModRowId', 'Name'), 
	FOREIGN KEY ('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- Name/Value pair representing properties of a component.
-- @ComponentRowId represents the specific component instance this file is a member of.
-- @Name is the name of the property.
-- @Value is the value of the property.
CREATE TABLE ComponentProperties(
	'ComponentRowId' INTEGER NOT NULL,
	'Name' TEXT NOT NULL,
	'Value' TEXT NOT NULL,
	PRIMARY KEY ('ComponentRowId', 'Name'),
	FOREIGN KEY ('ComponentRowId') REFERENCES Components('ComponentRowId') ON DELETE CASCADE ON UPDATE CASCADE
);
	
-- Name/Value pair representing properties of a setting.
-- @SettingRowId represents the specific setting instance this file is a member of.
-- @Name is the name of the property.
-- @Value is the value of the property.
CREATE TABLE SettingProperties(
	'SettingRowId' INTEGER NOT NULL,
	'Name' TEXT NOT NULL,
	'Value' TEXT NOT NULL,
	PRIMARY KEY ('SettingRowId', 'Name'),
	FOREIGN KEY ('SettingRowId') REFERENCES Settings('SettingRowId') ON DELETE CASCADE ON UPDATE CASCADE
);
	
-- A table describing the relationship of one mod package to another.
-- @ModRowId represents the mod instance initiating the relationship
-- @OtherModId represents the other mod (note that this is the ModId and not ModRowId)
-- @Relationship represents the kind of relationship.
-- @OtherModTitle represents the name of the other mod (used for situations where the mod does not exist).
CREATE TABLE ModRelationships(
	'ModRowId' INTEGER NOT NULL, 
	'OtherModId' TEXT NOT NULL, 
	'Relationship' TEXT NOT NULL, 
	'OtherModTitle' TEXT, 
	FOREIGN KEY('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);
	
-- A table describing the relationship of one mod component to another.
-- @ComponentRowId represents the component instance initiating the relationship.
-- @OtherModId represents the other mod (note that this is the ModId and not ModRowId).
-- @OtherComponentId represents the other mod's component (note that this is ComponentId and not ComponentRowId).
-- @Relationship represents the kind of relationship.
CREATE TABLE ComponentRelationships(
	'ComponentRowId' INTEGER NOT NULL, 
	'OtherModId' TEXT NOT NULL,
	'OtherComponentId' TEXT NOT NULL,
	'Relationship' TEXT NOT NULL,
	FOREIGN KEY('ComponentRowId') REFERENCES Components('ComponentRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains localized versions of descriptive strings used by the modinfo
-- @ModRowId is mod instance that owns the string.
-- @Tag is the key that is used to reference the string.
-- @Locale represents what locale the text is localized for.
-- @Text is the actual text.
CREATE TABLE LocalizedText(
	'ModRowId' INTEGER NOT NULL,
	'Tag' TEXT NOT NULL,
	'Locale' TEXT NOT NULL,
	'Text' TEXT NOT NULL,
	PRIMARY KEY('ModRowId', 'Tag', 'Locale'),
	FOREIGN KEY('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains named groups of enabled mods.
-- @ModGroupRowId is the unique id associated with the group.
-- @Name is the user-provided name of the group.
-- @CanDelete is whether or not the load out can be deleted by UI.
-- @SortIndex is the sort index to use for the loadout.
CREATE TABLE ModGroups(
	'ModGroupRowId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	'Name' TEXT NOT NULL,
	'CanDelete' BOOLEAN DEFAULT 1,
	'Selected' BOOLEAN DEFAULT 0,
	'SortIndex' INTEGER DEFAULT 100
);

-- This table contains the mods which are enabled for a specific mod group.
-- @ModGroupRowId is the unique id associated with a mod group.
-- @ModRowId is the unique id associated with a mod.
CREATE TABLE ModGroupItems(
	'ModGroupRowId' INTEGER NOT NULL,
	'ModRowId' INTEGER NOT NULL,
	'Disabled' BOOLEAN DEFAULT 0,
	PRIMARY KEY ('ModGroupRowId', 'ModRowId'),	
	FOREIGN KEY ('ModGroupRowId') REFERENCES ModGroups('ModGroupRowId') ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- This table contains statements to assist with migrating data during a database upgrade.
-- @SQL is the statement to run.
-- @MinVersion is the minimal old database version to run the SQL.
-- @MaxVersion is the maximum old database version to run the SQL.
-- @SortIndex is the column used to sort the statements.
CREATE TABLE Migrations(
	'SQL' TEXT NOT NULL,
	'MinVersion' INTEGER NOT NULL,
	'MaxVersion' INTEGER NOT NULL,
	'SortIndex' INTEGER NOT NULL
);

-- This table contains a list of mods that should ignore compatibility warnings.
-- @ModRowId is the unique id associated with a mod.
CREATE TABLE ModCompatibilityWhitelist(
	'ModRowId' INTEGER NOT NULL,
	'GameVersion' TEXT NOT NULL,
	PRIMARY KEY ('ModRowId'),	
	FOREIGN KEY ('ModRowId') REFERENCES Mods('ModRowId') ON DELETE CASCADE ON UPDATE CASCADE
);

-- Static Data
INSERT INTO ModGroups('ModGroupRowId', 'Name', 'CanDelete', 'Selected', 'SortIndex') VALUES (1, 'LOC_MODS_GROUP_DEFAULT_NAME', 0, 1, 0);

-- Data Migrations.
-- Copy mod groups.
INSERT INTO Migrations('MinVersion', 'MaxVersion', 'SortIndex', 'SQL') VALUES(16,999,0,"INSERT INTO ModGroups SELECT * from old.ModGroups as omg where omg.CanDelete = 1");

-- Copy which mod group is selected.
INSERT INTO Migrations('MinVersion', 'MaxVersion', 'SortIndex', 'SQL') VALUES(16,999,1,"UPDATE ModGroups SET Selected = (SELECT Selected FROM old.ModGroups omg where omg.ModGroupRowId = ModGroups.ModGroupRowId LIMIT 1)");

-- Copy Scanned Files data (but set LastWriteTime to 0 to force rescan)
INSERT INTO Migrations('MinVersion', 'MaxVersion', 'SortIndex', 'SQL') VALUES(16,999,1,'INSERT INTO ScannedFiles(ScannedFileRowId,Path,LastWriteTime) SELECT ScannedFileRowId,Path,0 from old.ScannedFiles;');

-- Copy Mod data (the mod row ids are needed the most here)
INSERT INTO Migrations('MinVersion', 'MaxVersion', 'SortIndex', 'SQL') VALUES(16,999,1,"INSERT INTO Mods('ModRowId','ScannedFileRowId','ModId','Version') SELECT ModRowId,ScannedFileRowId,ModId,Version from old.Mods");

-- Copy Mod Group Item data
INSERT INTO Migrations('MinVersion', 'MaxVersion', 'SortIndex', 'SQL') VALUES(16,999,1,"INSERT INTO ModGroupItems('ModGroupRowId','ModRowId') SELECT ModGroupRowId,ModRowId from old.ModGroupItems");

-- User version is written at the end.
PRAGMA user_version(24);
