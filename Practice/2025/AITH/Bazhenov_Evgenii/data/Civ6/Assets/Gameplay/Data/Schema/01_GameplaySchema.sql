-- Version 1
PRAGMA schema_version = 1000;

-- This meta-table contains information about additional relations between one table and another.
-- It is used by C++ and Lua exposures to create more user-friendly references.
-- The data in this table is auto-generated but could later be modified by modders.
-- Query Requirements:
--		Query must only return 1 column (a rowid from the target table).
--		Query must only accept 1 argument (a rowid from the source table).
--		If "IsCollection" is non-zero, property is assumed to point to a collection.
CREATE TABLE NavigationProperties("BaseTable" TEXT NOT NULL, "PropertyName" TEXT NOT NULL, "TargetTable" TEXT NOT NULL, IsCollection INTEGER DEFAULT 0, "Query" TEXT NOT NULL, PRIMARY KEY("BaseTable", "PropertyName", "TargetTable"));
CREATE TABLE "Adjacency_YieldChanges" (
		"ID" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL DEFAULT 0,
		"TilesRequired" INTEGER NOT NULL DEFAULT 1,
		"OtherDistrictAdjacent" BOOLEAN NOT NULL CHECK (OtherDistrictAdjacent IN (0,1)) DEFAULT 0,
		"AdjacentSeaResource" BOOLEAN NOT NULL CHECK (AdjacentSeaResource IN (0,1)) DEFAULT 0,
		"AdjacentTerrain" TEXT,
		"AdjacentFeature" TEXT,
		"AdjacentRiver" BOOLEAN NOT NULL CHECK (AdjacentRiver IN (0,1)) DEFAULT 0,
		"AdjacentWonder" BOOLEAN NOT NULL CHECK (AdjacentWonder IN (0,1)) DEFAULT 0,
		"AdjacentNaturalWonder" BOOLEAN NOT NULL CHECK (AdjacentNaturalWonder IN (0,1)) DEFAULT 0,
		"AdjacentImprovement" TEXT,
		"AdjacentDistrict" TEXT,
		"PrereqCivic" TEXT,
		"PrereqTech" TEXT,
		"ObsoleteCivic" TEXT,
		"ObsoleteTech" TEXT,
		"AdjacentResource" BOOLEAN NOT NULL CHECK (AdjacentResource IN (0,1)) DEFAULT 0,
		"AdjacentResourceClass" TEXT NOT NULL DEFAULT "NO_RESOURCECLASS",
		"Self" BOOLEAN NOT NULL CHECK (Self IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ID),
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AdjacentTerrain) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AdjacentFeature) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AdjacentImprovement) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AdjacentDistrict) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (ObsoleteCivic) REFERENCES Civics(CivicType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (ObsoleteTech) REFERENCES Technologies(TechnologyType) ON DELETE SET NULL ON UPDATE CASCADE);

CREATE TABLE "Adjacent_AppealYieldChanges" (
		"DistrictType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"MaximumValue" INTEGER NOT NULL,
		"BuildingType" TEXT NOT NULL DEFAULT "NO_BUILDING",
		"MinimumValue" INTEGER NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		"Description" TEXT NOT NULL,
		"Unimproved" BOOLEAN NOT NULL CHECK (Unimproved IN (0,1)) DEFAULT 0,
		PRIMARY KEY(DistrictType, YieldType, MaximumValue, BuildingType, MinimumValue),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Agendas" (
		"AgendaType" TEXT NOT NULL UNIQUE,
		"OperationList" TEXT,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		PRIMARY KEY(AgendaType),
		FOREIGN KEY (OperationList) REFERENCES AiOperationLists(ListType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AgendaPreferredLeaders" (
		"AgendaType" TEXT NOT NULL,
		"LeaderType" TEXT NOT NULL,
		"PercentageChance" INTEGER NOT NULL DEFAULT 100,
		PRIMARY KEY(AgendaType, LeaderType),
		FOREIGN KEY (AgendaType) REFERENCES RandomAgendas(AgendaType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AgendaTraits" (
		"AgendaType" TEXT NOT NULL,
		"TraitType" TEXT NOT NULL,
		PRIMARY KEY(AgendaType, TraitType),
		FOREIGN KEY (AgendaType) REFERENCES Agendas(AgendaType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AiBuildSpecializations" (
		"SpecializationType" TEXT NOT NULL,
		"BuildingYield" TEXT,
		"IncludePopulation" BOOLEAN NOT NULL CHECK (IncludePopulation IN (0,1)) DEFAULT 0,
		"IncludeDefense" BOOLEAN NOT NULL CHECK (IncludeDefense IN (0,1)) DEFAULT 0,
		"IncludeMilitaryUnits" BOOLEAN NOT NULL CHECK (IncludeMilitaryUnits IN (0,1)) DEFAULT 0,
		"IncludeTradeUnits" BOOLEAN NOT NULL CHECK (IncludeTradeUnits IN (0,1)) DEFAULT 0,
		"PrioritizationYield" TEXT NOT NULL,
		"PriorityOffset" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(SpecializationType, PrioritizationYield),
		FOREIGN KEY (BuildingYield) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrioritizationYield) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Special events sent by the AI
CREATE TABLE "AiEvents" (
		"EventType" TEXT NOT NULL,
		PRIMARY KEY(EventType));

CREATE TABLE "AiFavoredItems" (
		"ListType" TEXT,
		"Item" TEXT NOT NULL,
		"Favored" BOOLEAN NOT NULL CHECK (Favored IN (0,1)) DEFAULT 1,
		"Value" INTEGER NOT NULL DEFAULT 0,
		"StringVal" TEXT,
		"MinDifficulty" TEXT,
		"MaxDifficulty" TEXT,
		"TooltipString" TEXT,
		PRIMARY KEY(ListType, Item, Favored, Value, StringVal),
		FOREIGN KEY (MinDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MaxDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ListType) REFERENCES AiListTypes(ListType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AiLists" (
		"ListType" TEXT NOT NULL,
		"LeaderType" TEXT,
		"AgendaType" TEXT,
		"System" TEXT NOT NULL,
		"MinDifficulty" TEXT,
		"MaxDifficulty" TEXT,
		PRIMARY KEY(ListType, LeaderType, AgendaType),
		FOREIGN KEY (MaxDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MinDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ListType) REFERENCES AiListTypes(ListType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AiListTypes" (
		"ListType" TEXT,
		PRIMARY KEY(ListType));

CREATE TABLE "AiOperationDefs" (
		"OperationName" TEXT NOT NULL,
		"TargetType" TEXT NOT NULL,
		"TargetParameter" INTEGER NOT NULL DEFAULT 0,
		"EnemyType" TEXT NOT NULL DEFAULT "NONE",
		"BehaviorTree" TEXT,
		"Priority" INTEGER NOT NULL DEFAULT 3,
		"MaxTargetDistInRegion" INTEGER NOT NULL DEFAULT 10,
		"MaxTargetDistInArea" INTEGER NOT NULL DEFAULT 5,
		"MaxTargetDistInWorld" INTEGER NOT NULL DEFAULT 0,
		"MaxTargetStrength" INTEGER NOT NULL DEFAULT -1,
		"MaxTargetDefense" INTEGER NOT NULL DEFAULT -1,
		"MinOddsOfSuccess" REAL NOT NULL DEFAULT 0,
		"SelfStart" BOOLEAN NOT NULL CHECK (SelfStart IN (0,1)) DEFAULT 0,
		"MustBeAtWar" BOOLEAN NOT NULL CHECK (MustBeAtWar IN (0,1)) DEFAULT 0,
		"MustHaveNukes" BOOLEAN NOT NULL CHECK (MustHaveNukes IN (0,1)) DEFAULT 0,
		"MustHaveUnits" INTEGER NOT NULL DEFAULT -1,
		"OperationType" TEXT,
		"AllowTargetUpdate" BOOLEAN NOT NULL CHECK (AllowTargetUpdate IN (0,1)) DEFAULT 1,
		"TargetLuaScript" TEXT,
		"ActiveEmergency" TEXT,
		PRIMARY KEY(OperationName),
		FOREIGN KEY (BehaviorTree) REFERENCES BehaviorTrees(TreeName) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TargetType) REFERENCES TargetTypes(TargetType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OperationType) REFERENCES AiOperationTypes(OperationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AiOperationLimits" (
		"ListType" TEXT NOT NULL,
		"OperationType" TEXT NOT NULL,
		"BaseValue" INTEGER,
		"DeltaValue" INTEGER,
		PRIMARY KEY(ListType, OperationType),
		FOREIGN KEY (ListType) REFERENCES AiOperationLists(ListType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OperationType) REFERENCES AiOperationTypes(OperationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AiOperationLists" (
		"ListType" TEXT NOT NULL,
		"BaseList" TEXT,
		PRIMARY KEY(ListType),
		FOREIGN KEY (BaseList) REFERENCES AiOperationLists(ListType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AiOperationTeams" (
		"TeamName" TEXT NOT NULL,
		"OperationName" TEXT NOT NULL,
		"MinUnits" INTEGER NOT NULL DEFAULT 1,
		"MaxUnits" INTEGER NOT NULL DEFAULT -1,
		"InitialStrengthAdvantage" REAL NOT NULL DEFAULT 0,
		"OngoingStrengthAdvantage" REAL NOT NULL DEFAULT 0,
		"SafeRallyPoint" BOOLEAN NOT NULL CHECK (SafeRallyPoint IN (0,1)) DEFAULT 0,
		"Condition" TEXT,
		PRIMARY KEY(TeamName, OperationName),
		FOREIGN KEY (OperationName) REFERENCES AiOperationDefs(OperationName) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TeamName) REFERENCES AiTeams(TeamName) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AiOperationTypes" (
		"OperationType" TEXT NOT NULL,
		"Value" INTEGER NOT NULL,
		PRIMARY KEY(OperationType));

CREATE TABLE "AiScoutUses" (
		"ScoutUseType" TEXT NOT NULL UNIQUE,
		PRIMARY KEY(ScoutUseType));

CREATE TABLE "AiTeams" (
		"TeamName" TEXT,
		PRIMARY KEY(TeamName));

CREATE TABLE "AllowedMoves" (
		"AllowedMoveType" TEXT NOT NULL UNIQUE,
		"Value" INTEGER NOT NULL,
		"IsHomeland" BOOLEAN NOT NULL CHECK (IsHomeland IN (0,1)) DEFAULT 0,
		"IsTactical" BOOLEAN NOT NULL CHECK (IsTactical IN (0,1)) DEFAULT 0,
		PRIMARY KEY(AllowedMoveType));

CREATE TABLE "AllowedOperations" (
		"ListType" TEXT NOT NULL,
		"OperationDef" TEXT NOT NULL,
		"RemoveRef" BOOLEAN NOT NULL CHECK (RemoveRef IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ListType, OperationDef),
		FOREIGN KEY (ListType) REFERENCES AiOperationLists(ListType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OperationDef) REFERENCES AiOperationDefs(OperationName) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "AppealHousingChanges" (
		"DistrictType" TEXT NOT NULL,
		"MinimumValue" INTEGER NOT NULL,
		"AppealChange" INTEGER NOT NULL,
		"Description" TEXT NOT NULL,
		PRIMARY KEY(DistrictType, MinimumValue),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BarbarianAttackForces" (
		"AttackForceType" TEXT NOT NULL,
		"MinTargetDifficulty" TEXT,
		"MaxTargetDifficulty" TEXT,
		"SpawnRate" INTEGER NOT NULL DEFAULT 2,
		"MeleeTag" TEXT,
		"NumMeleeUnits" INTEGER NOT NULL DEFAULT 0,
		"RangeTag" TEXT,
		"NumRangeUnits" INTEGER NOT NULL DEFAULT 0,
		"SiegeTag" TEXT,
		"NumSiegeUnits" INTEGER NOT NULL DEFAULT 0,
		"SupportTag" TEXT,
		"NumSupportUnits" INTEGER NOT NULL DEFAULT 0,
		"RaidingForce" BOOLEAN NOT NULL CHECK (RaidingForce IN (0,1)) DEFAULT 0,
		PRIMARY KEY(AttackForceType),
		FOREIGN KEY (MinTargetDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MaxTargetDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BarbarianTribes" (
		"TribeType" TEXT NOT NULL UNIQUE,
		"IsCoastal" BOOLEAN NOT NULL CHECK (IsCoastal IN (0,1)) DEFAULT 0,
		"RequiredResource" TEXT,
		"ResourceRange" INTEGER NOT NULL DEFAULT 0,
		"PercentRangedUnits" INTEGER NOT NULL DEFAULT 0,
		"TurnsToWarriorSpawn" INTEGER NOT NULL DEFAULT 15,
		"ScoutTag" TEXT NOT NULL,
		"MeleeTag" TEXT NOT NULL,
		"RangedTag" TEXT NOT NULL,
		"SiegeTag" TEXT NOT NULL,
		"DefenderTag" TEXT NOT NULL,
		"SupportTag" TEXT,
		"ScoutingBehaviorTree" TEXT NOT NULL,
		"RaidingBehaviorTree" TEXT NOT NULL,
		"RaidingBoldness" INTEGER NOT NULL DEFAULT 20,
		"CityAttackOperation" TEXT NOT NULL,
		"CityAttackBoldness" INTEGER NOT NULL DEFAULT 25,
		"Name" TEXT,
		PRIMARY KEY(TribeType),
		FOREIGN KEY (RequiredResource) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BarbarianTribe_ExtraUnits" (
		"TribeType" TEXT NOT NULL,
		"UnitType" TEXT NOT NULL,
		"Number" INTEGER NOT NULL DEFAULT 1,
		PRIMARY KEY(TribeType, UnitType));

CREATE TABLE "BarbarianTribe_MapConditions" (
		"MapConditionSetType" TEXT NOT NULL,
		"TerrainType" TEXT,
		"FeatureType" TEXT,
		"ResourceType" TEXT,
		"Range" INTEGER NOT NULL DEFAULT 0,
		"Invert" BOOLEAN NOT NULL CHECK (Invert IN (0,1)) DEFAULT 0,
		PRIMARY KEY(MapConditionSetType, TerrainType, FeatureType, ResourceType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MapConditionSetType) REFERENCES BarbarianTribe_MapConditionSets(MapConditionSetType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BarbarianTribe_MapConditionSets" (
		"MapConditionSetType" TEXT NOT NULL,
		"TribeType" TEXT NOT NULL,
		"Test" TEXT NOT NULL,
		"Priority" INTEGER NOT NULL DEFAULT 1,
		PRIMARY KEY(MapConditionSetType),
		FOREIGN KEY (TribeType) REFERENCES BarbarianTribes(TribeType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BarbarianTribe_UnitConditions" (
		"TribeType" TEXT NOT NULL,
		"UnitType" TEXT NOT NULL,
		"ReplacesUnitType" TEXT,
		"MaxPerTribe" INTEGER NOT NULL DEFAULT 1,
		PRIMARY KEY(TribeType, UnitType),
		FOREIGN KEY (TribeType) REFERENCES BarbarianTribes(TribeType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ReplacesUnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BarbarianTribeForces" (
		"AttackForceType" TEXT NOT NULL,
		"TribeType" TEXT,
		"SpecificTribeType" TEXT,
		PRIMARY KEY(AttackForceType, TribeType, SpecificTribeType),
		FOREIGN KEY (AttackForceType) REFERENCES BarbarianAttackForces(AttackForceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TribeType) REFERENCES BarbarianTribes(TribeType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (SpecificTribeType) REFERENCES BarbarianTribeNames(TribeNameType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BarbarianTribeNames" (
		"TribeNameType" TEXT NOT NULL,
		"TribeType" TEXT NOT NULL,
		"NumMilitary" INTEGER DEFAULT 5,
		"NumScouts" INTEGER,
		"PercentRangedUnits" INTEGER,
		"TurnsToWarriorSpawn" INTEGER,
		"TribeDisplayName" TEXT NOT NULL,
		"ScoutingBehaviorTree" TEXT,
		"RaidingBehaviorTree" TEXT,
		"RaidingBoldness" INTEGER,
		PRIMARY KEY(TribeNameType),
		FOREIGN KEY (TribeType) REFERENCES BarbarianTribes(TribeType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BehaviorTrees" (
		"TreeName" TEXT NOT NULL,
		PRIMARY KEY(TreeName));

CREATE TABLE "BehaviorTreeNodes" (
		"TreeName" TEXT NOT NULL,
		"NodeId" INTEGER NOT NULL,
		"JumpTo" INTEGER NOT NULL DEFAULT 0,
		"NodeType" TEXT NOT NULL,
		"PrimaryKey" INTEGER NOT NULL,
		PRIMARY KEY(PrimaryKey),
		FOREIGN KEY (TreeName) REFERENCES BehaviorTrees(TreeName) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (NodeType) REFERENCES NodeDefinitions(NodeType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Beliefs" (
		"BeliefType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"BeliefClassType" TEXT NOT NULL,
		PRIMARY KEY(BeliefType),
		FOREIGN KEY (BeliefClassType) REFERENCES BeliefClasses(BeliefClassType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (BeliefType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BeliefClasses" (
		"BeliefClassType" TEXT NOT NULL UNIQUE,
		"Name" TEXT NOT NULL,
		"MaxInReligion" INTEGER NOT NULL DEFAULT 1,
		"AdoptionOrder" INTEGER NOT NULL DEFAULT 1,
		PRIMARY KEY(BeliefClassType));

CREATE TABLE "BeliefModifiers" (
		"BeliefType" TEXT NOT NULL,
		"ModifierID" TEXT NOT NULL,
		PRIMARY KEY(BeliefType, ModifierID),
		FOREIGN KEY (BeliefType) REFERENCES Beliefs(BeliefType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BonusMinorStartingUnits" (
		"Unit" TEXT NOT NULL,
		"Era" TEXT NOT NULL,
		"Quantity" INTEGER NOT NULL DEFAULT 1,
		"OnDistrictCreated" BOOLEAN NOT NULL CHECK (OnDistrictCreated IN (0,1)) DEFAULT 0,
		"District" TEXT NOT NULL DEFAULT "DISTRICT_CITY_CENTER",
		"MinDifficulty" TEXT,
		"DifficultyDelta" REAL NOT NULL DEFAULT 0,
		PRIMARY KEY(Unit, Era, MinDifficulty),
		FOREIGN KEY (Era) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Unit) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MinDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Boosts" (
		"BoostID" INTEGER NOT NULL,
		"TechnologyType" TEXT,
		"CivicType" TEXT,
		"Boost" INTEGER NOT NULL,
		"TriggerId" INTEGER NOT NULL DEFAULT 0,
		"TriggerDescription" TEXT NOT NULL,
		"TriggerLongDescription" TEXT NOT NULL,
		"Unit1Type" TEXT,
		"BoostClass" TEXT NOT NULL,
		"Unit2Type" TEXT,
		"BuildingType" TEXT,
		"ImprovementType" TEXT,
		"BoostingTechType" TEXT,
		"ResourceType" TEXT,
		"NumItems" INTEGER NOT NULL DEFAULT 0,
		"DistrictType" TEXT,
		"RequiresResource" BOOLEAN NOT NULL CHECK (RequiresResource IN (0,1)) DEFAULT 0,
		"RequirementSetId" TEXT,
		"GovernmentSlotType" TEXT,
		"BoostingCivicType" TEXT,
		"GovernmentTierType" TEXT,
		PRIMARY KEY(BoostID),
		FOREIGN KEY (TechnologyType) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Unit1Type) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Unit2Type) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (BoostClass) REFERENCES BoostNames(BoostType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (BoostingTechType) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CivicType) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (BoostingCivicType) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GovernmentSlotType) REFERENCES GovernmentSlots(GovernmentSlotType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GovernmentTierType) REFERENCES GovernmentTiers(TierType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BoostHandlers" (
		"HandlerId" TEXT,
		"TechBoostType" TEXT NOT NULL,
		"BehaviorTree" TEXT,
		"OperationName" TEXT,
		"LuaScript" TEXT,
		"UniquenessTag" TEXT,
		"WinnowFunction" TEXT,
		PRIMARY KEY(HandlerId),
		FOREIGN KEY (BehaviorTree) REFERENCES BehaviorTrees(TreeName) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TechBoostType) REFERENCES BoostNames(BoostType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OperationName) REFERENCES AiOperationDefs(OperationName) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BoostNames" (
		"BoostType" TEXT NOT NULL,
		"BoostValue" INTEGER NOT NULL UNIQUE,
		PRIMARY KEY(BoostType));

CREATE TABLE "Buildings" (
		"BuildingType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"Cost" INTEGER NOT NULL,
		"MaxPlayerInstances" INTEGER NOT NULL DEFAULT -1,
		"MaxWorldInstances" INTEGER NOT NULL DEFAULT -1,
		"Capital" BOOLEAN NOT NULL CHECK (Capital IN (0,1)) DEFAULT 0,
		"PrereqDistrict" TEXT,
		"AdjacentDistrict" TEXT,
		"Description" TEXT,
		"RequiresPlacement" BOOLEAN NOT NULL CHECK (RequiresPlacement IN (0,1)) DEFAULT 0,
		"RequiresRiver" BOOLEAN NOT NULL CHECK (RequiresRiver IN (0,1)) DEFAULT 0,
		"OuterDefenseHitPoints" INTEGER,
		"Housing" INTEGER NOT NULL DEFAULT 0,
		"Entertainment" INTEGER NOT NULL DEFAULT 0,
		"AdjacentResource" TEXT,
		"Coast" BOOLEAN CHECK (Coast IN (0,1)),
		"EnabledByReligion" BOOLEAN NOT NULL CHECK (EnabledByReligion IN (0,1)) DEFAULT 0,
		"AllowsHolyCity" BOOLEAN NOT NULL CHECK (AllowsHolyCity IN (0,1)) DEFAULT 0,
		"PurchaseYield" TEXT,
		"MustPurchase" BOOLEAN NOT NULL CHECK (MustPurchase IN (0,1)) DEFAULT 0,
		"Maintenance" INTEGER NOT NULL DEFAULT 0,
		"IsWonder" BOOLEAN NOT NULL CHECK (IsWonder IN (0,1)) DEFAULT 0,
		"TraitType" TEXT,
		"OuterDefenseStrength" INTEGER NOT NULL DEFAULT 0,
		"CitizenSlots" INTEGER,
		"MustBeLake" BOOLEAN NOT NULL CHECK (MustBeLake IN (0,1)) DEFAULT 0,
		"MustNotBeLake" BOOLEAN NOT NULL CHECK (MustNotBeLake IN (0,1)) DEFAULT 0,
		"RegionalRange" INTEGER NOT NULL DEFAULT 0,
		"AdjacentToMountain" BOOLEAN NOT NULL CHECK (AdjacentToMountain IN (0,1)) DEFAULT 0,
		"ObsoleteEra" TEXT NOT NULL DEFAULT "NO_ERA",
		"RequiresReligion" BOOLEAN NOT NULL CHECK (RequiresReligion IN (0,1)) DEFAULT 0,
		"GrantFortification" INTEGER NOT NULL DEFAULT 0,
		"DefenseModifier" INTEGER NOT NULL DEFAULT 0,
		"InternalOnly" BOOLEAN NOT NULL CHECK (InternalOnly IN (0,1)) DEFAULT 0,
		"RequiresAdjacentRiver" BOOLEAN NOT NULL CHECK (RequiresAdjacentRiver IN (0,1)) DEFAULT 0,
		"Quote" TEXT,
		"QuoteAudio" TEXT,
		"MustBeAdjacentLand" BOOLEAN NOT NULL CHECK (MustBeAdjacentLand IN (0,1)) DEFAULT 0,
		"AdvisorType" TEXT,
		"AdjacentCapital" BOOLEAN NOT NULL CHECK (AdjacentCapital IN (0,1)) DEFAULT 0,
		"AdjacentImprovement" TEXT,
		"CityAdjacentTerrain" TEXT,
		"UnlocksGovernmentPolicy" BOOLEAN CHECK (UnlocksGovernmentPolicy IN (0,1)) DEFAULT 0,
		"GovernmentTierRequirement" TEXT,
		PRIMARY KEY(BuildingType),
		FOREIGN KEY (AdjacentDistrict) REFERENCES Districts(DistrictType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqDistrict) REFERENCES Districts(DistrictType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (AdjacentResource) REFERENCES Resources(ResourceType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PurchaseYield) REFERENCES Yields(YieldType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (BuildingType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AdjacentImprovement) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CityAdjacentTerrain) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_CitizenYieldChanges" (
		"BuildingType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(BuildingType, YieldType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_GreatPersonPoints" (
		"BuildingType" TEXT NOT NULL,
		"GreatPersonClassType" TEXT NOT NULL,
		"PointsPerTurn" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(BuildingType, GreatPersonClassType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonClassType) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_GreatWorks" (
		"BuildingType" TEXT NOT NULL,
		"GreatWorkSlotType" TEXT NOT NULL,
		"NumSlots" INTEGER NOT NULL DEFAULT 1,
		"ThemingUniquePerson" BOOLEAN NOT NULL CHECK (ThemingUniquePerson IN (0,1)) DEFAULT 0,
		"ThemingSameObjectType" BOOLEAN NOT NULL CHECK (ThemingSameObjectType IN (0,1)) DEFAULT 0,
		"ThemingUniqueCivs" BOOLEAN NOT NULL CHECK (ThemingUniqueCivs IN (0,1)) DEFAULT 0,
		"ThemingSameEras" BOOLEAN NOT NULL CHECK (ThemingSameEras IN (0,1)) DEFAULT 0,
		"ThemingYieldMultiplier" INTEGER NOT NULL DEFAULT 0,
		"ThemingTourismMultiplier" INTEGER NOT NULL DEFAULT 0,
		"NonUniquePersonYield" INTEGER NOT NULL DEFAULT 0,
		"NonUniquePersonTourism" INTEGER NOT NULL DEFAULT 0,
		"ThemingBonusDescription" TEXT,
		PRIMARY KEY(BuildingType, GreatWorkSlotType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatWorkSlotType) REFERENCES GreatWorkSlotTypes(GreatWorkSlotType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_RequiredFeatures" (
		"BuildingType" TEXT NOT NULL,
		"FeatureType" TEXT NOT NULL,
		PRIMARY KEY(BuildingType, FeatureType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_ValidFeatures" (
		"BuildingType" TEXT NOT NULL,
		"FeatureType" TEXT NOT NULL,
		PRIMARY KEY(BuildingType, FeatureType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_ValidTerrains" (
		"BuildingType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(BuildingType, TerrainType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_YieldChanges" (
		"BuildingType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(BuildingType, YieldType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_YieldDistrictCopies" (
		"BuildingType" TEXT NOT NULL,
		"OldYieldType" TEXT NOT NULL DEFAULT "NO_YIELD",
		"NewYieldType" TEXT NOT NULL DEFAULT "NO_YIELD",
		PRIMARY KEY(BuildingType, OldYieldType, NewYieldType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OldYieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (NewYieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Building_YieldsPerEra" (
		"BuildingType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL DEFAULT "NO_YIELD",
		"YieldChange" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(BuildingType, YieldType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BuildingConditions" (
		"BuildingType" TEXT NOT NULL,
		"UnlocksFromEffect" BOOLEAN NOT NULL CHECK (UnlocksFromEffect IN (0,1)) DEFAULT 0,
		PRIMARY KEY(BuildingType),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BuildingModifiers" (
		"BuildingType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(BuildingType, ModifierId),
		FOREIGN KEY (BuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BuildingPrereqs" (
		"Building" TEXT NOT NULL,
		"PrereqBuilding" TEXT NOT NULL,
		PRIMARY KEY(Building, PrereqBuilding),
		FOREIGN KEY (Building) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqBuilding) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "BuildingReplaces" (
		"CivUniqueBuildingType" TEXT NOT NULL,
		"ReplacesBuildingType" TEXT NOT NULL,
		PRIMARY KEY(CivUniqueBuildingType, ReplacesBuildingType),
		FOREIGN KEY (CivUniqueBuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ReplacesBuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Calendar types
CREATE TABLE "Calendars" (
		"CalendarType" TEXT NOT NULL,
		"Description" TEXT,
		PRIMARY KEY(CalendarType));

CREATE TABLE "CityEvents" (
		"EventType" TEXT NOT NULL,
		PRIMARY KEY(EventType));

CREATE TABLE "CityNames" (
		"ID" INTEGER,
		"CivilizationType" TEXT,
		"LeaderType" TEXT,
		"ContinentType" TEXT,
		"CityName" TEXT NOT NULL,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(ID),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ContinentType) REFERENCES Continents(ContinentType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Civics" (
		"CivicType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Cost" INTEGER NOT NULL,
		"Repeatable" BOOLEAN NOT NULL CHECK (Repeatable IN (0,1)) DEFAULT 0,
		"Description" TEXT,
		"EraType" TEXT NOT NULL,
		"BarbarianFree" BOOLEAN NOT NULL CHECK (BarbarianFree IN (0,1)) DEFAULT 0,
		"UITreeRow" INTEGER DEFAULT 0,
		"AdvisorType" TEXT,
		"EmbarkAll" BOOLEAN NOT NULL CHECK (EmbarkAll IN (0,1)) DEFAULT 0,
		"EmbarkUnitType" TEXT,
		PRIMARY KEY(CivicType),
		FOREIGN KEY (EraType) REFERENCES Eras(EraType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (CivicType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Civics_XP2" (
		"CivicType" TEXT NOT NULL,
		"RandomPrereqs" BOOLEAN NOT NULL CHECK (RandomPrereqs IN (0,1)) DEFAULT 0,
		"HiddenUntilPrereqComplete" BOOLEAN NOT NULL CHECK (HiddenUntilPrereqComplete IN (0,1)) DEFAULT 0,
		PRIMARY KEY(CivicType),
		FOREIGN KEY (CivicType) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivicModifiers" (
		"CivicType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(CivicType, ModifierId),
		FOREIGN KEY (CivicType) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivicPrereqs" (
		"Civic" TEXT NOT NULL,
		"PrereqCivic" TEXT NOT NULL,
		PRIMARY KEY(Civic, PrereqCivic),
		FOREIGN KEY (Civic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivicQuotes" (
		"CivicType" TEXT NOT NULL,
		"Quote" TEXT NOT NULL,
		"QuoteAudio" TEXT,
		PRIMARY KEY(CivicType, Quote),
		FOREIGN KEY (CivicType) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivicRandomCosts" (
		"CivicType" TEXT NOT NULL,
		"Cost" INTEGER NOT NULL,
		PRIMARY KEY(CivicType, Cost),
		FOREIGN KEY (CivicType) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Civilizations" (
		"CivilizationType" TEXT NOT NULL,
		"Name" LocalizedText NOT NULL,
		"Description" TEXT,
		"Adjective" TEXT NOT NULL,
		"RandomCityNameDepth" INTEGER NOT NULL DEFAULT 1,
		"StartingCivilizationLevelType" TEXT NOT NULL,
		"Ethnicity" TEXT,
		PRIMARY KEY(CivilizationType),
		FOREIGN KEY (StartingCivilizationLevelType) REFERENCES CivilizationLevels(CivilizationLevelType) ON DELETE SET DEFAULT ON UPDATE CASCADE,
		FOREIGN KEY (CivilizationType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

-- Allows us to change the background and leader images on the diplomacy screen.
CREATE TABLE "CivilizationAudioTags" (
		"CivilizationType" TEXT NOT NULL,
		"MusicOverride" BOOLEAN NOT NULL CHECK (MusicOverride IN (0,1)),
		PRIMARY KEY(CivilizationType),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivilizationCitizenNames" (
		"CivilizationType" TEXT NOT NULL,
		"CitizenName" TEXT NOT NULL,
		"Female" BOOLEAN NOT NULL CHECK (Female IN (0,1)) DEFAULT 0,
		"Modern" BOOLEAN NOT NULL CHECK (Modern IN (0,1)) DEFAULT 0,
		PRIMARY KEY(CivilizationType, CitizenName),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Random bits of information about the Civilization
CREATE TABLE "CivilizationInfo" (
		"CivilizationType" TEXT NOT NULL,
		"Header" TEXT NOT NULL,
		"Caption" TEXT NOT NULL,
		"SortIndex" INTEGER NOT NULL DEFAULT 100,
		PRIMARY KEY(CivilizationType, Header),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivilizationLeaders" (
		"LeaderType" TEXT NOT NULL,
		"CivilizationType" TEXT NOT NULL,
		"CapitalName" TEXT NOT NULL,
		PRIMARY KEY(LeaderType, CivilizationType),
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivilizationLevels" (
		"CivilizationLevelType" TEXT NOT NULL,
		"CanFoundCities" BOOLEAN NOT NULL CHECK (CanFoundCities IN (0,1)),
		"CanAnnexTilesWithCulture" BOOLEAN NOT NULL CHECK (CanAnnexTilesWithCulture IN (0,1)),
		"CanAnnexTilesWithGold" BOOLEAN NOT NULL CHECK (CanAnnexTilesWithGold IN (0,1)),
		"CanAnnexTilesWithReceivedInfluence" BOOLEAN NOT NULL CHECK (CanAnnexTilesWithReceivedInfluence IN (0,1)),
		"CanEarnGreatPeople" BOOLEAN NOT NULL CHECK (CanEarnGreatPeople IN (0,1)),
		"CanGiveInfluence" BOOLEAN NOT NULL CHECK (CanGiveInfluence IN (0,1)),
		"CanReceiveInfluence" BOOLEAN NOT NULL CHECK (CanReceiveInfluence IN (0,1)),
		"StartingTilesForCity" INTEGER NOT NULL,
		"CanBuildWonders" BOOLEAN NOT NULL CHECK (CanBuildWonders IN (0,1)),
		"IgnoresUnitStrategicResourceRequirements" BOOLEAN NOT NULL CHECK (IgnoresUnitStrategicResourceRequirements IN (0,1)) DEFAULT 0,
		PRIMARY KEY(CivilizationLevelType));

CREATE TABLE "CivilizationTraits" (
		"CivilizationType" TEXT NOT NULL,
		"TraitType" TEXT NOT NULL,
		PRIMARY KEY(CivilizationType, TraitType),
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "CivilopediaPages" (
		"SectionId" TEXT NOT NULL,
		"PageId" TEXT NOT NULL,
		"PageGroupId" TEXT,
		"PageLayoutId" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Tooltip" TEXT,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		"TextKeyPrefix" TEXT,
		PRIMARY KEY(SectionId, PageId));

CREATE TABLE "CivilopediaPageChapterHeaders" (
		"SectionId" TEXT NOT NULL,
		"PageId" TEXT NOT NULL,
		"ChapterId" TEXT NOT NULL,
		"Header" LocalizedText NOT NULL,
		PRIMARY KEY(SectionId, PageId, ChapterId));

CREATE TABLE "CivilopediaPageChapterParagraphs" (
		"SectionId" TEXT NOT NULL,
		"PageId" TEXT NOT NULL,
		"ChapterId" TEXT NOT NULL,
		"Paragraph" LocalizedText NOT NULL,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(SectionId, PageId, ChapterId, Paragraph));

-- This table specifies pages that should be hidden from the civilopedia.
CREATE TABLE "CivilopediaPageExcludes" (
		"SectionId" TEXT NOT NULL,
		"PageId" TEXT NOT NULL,
		PRIMARY KEY(SectionId, PageId));

CREATE TABLE "CivilopediaPageGroups" (
		"SectionId" TEXT NOT NULL,
		"PageGroupId" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Tooltip" TEXT,
		"VisibleIfEmpty" BOOLEAN NOT NULL CHECK (VisibleIfEmpty IN (0,1)) DEFAULT 0,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(SectionId, PageGroupId));

CREATE TABLE "CivilopediaPageGroupExcludes" (
		"SectionId" TEXT NOT NULL,
		"PageGroupId" TEXT NOT NULL,
		PRIMARY KEY(SectionId, PageGroupId));

CREATE TABLE "CivilopediaPageGroupQueries" (
		"RowId" INTEGER NOT NULL,
		"SectionId" TEXT NOT NULL,
		"SQL" TEXT NOT NULL,
		"PageGroupIdColumn" TEXT NOT NULL DEFAULT "PageGroupId",
		"NameColumn" TEXT NOT NULL DEFAULT "Name",
		"TooltipColumn" TEXT,
		"VisibleIfEmptyColumn" TEXT,
		"SortIndexColumn" TEXT,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(RowId));

CREATE TABLE "CivilopediaPageLayouts" (
		"PageLayoutId" TEXT NOT NULL,
		"ScriptTemplate" TEXT NOT NULL,
		PRIMARY KEY(PageLayoutId, ScriptTemplate));

CREATE TABLE "CivilopediaPageLayoutChapters" (
		"PageLayoutId" TEXT NOT NULL,
		"ChapterId" TEXT NOT NULL,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(PageLayoutId, ChapterId));

CREATE TABLE "CivilopediaPageQueries" (
		"RowId" INTEGER NOT NULL,
		"SectionId" TEXT NOT NULL,
		"SQL" TEXT NOT NULL,
		"PageIdColumn" TEXT NOT NULL DEFAULT "PageId",
		"PageGroupIdColumn" TEXT,
		"PageLayoutIdColumn" TEXT NOT NULL DEFAULT "PageLayoutId",
		"NameColumn" TEXT NOT NULL DEFAULT "Name",
		"TooltipColumn" TEXT DEFAULT "Tooltip",
		"TextKeyPrefixColumn" TEXT,
		"SortIndexColumn" TEXT,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(RowId));

-- Additional single word terms that can be used when searching the pedia.
CREATE TABLE "CivilopediaPageSearchTerms" (
		"SectionId" TEXT NOT NULL,
		"PageId" TEXT NOT NULL,
		"Term" LocalizedText NOT NULL,
		PRIMARY KEY(SectionId, PageId, Term));

-- Queries to dynamically provide additional search terms.
CREATE TABLE "CivilopediaPageSearchTermQueries" (
		"RowId" INTEGER NOT NULL,
		"SQL" TEXT NOT NULL,
		"SectionIdColumn" TEXT NOT NULL DEFAULT "SectionId",
		"PageIdColumn" TEXT NOT NULL DEFAULT "PageId",
		"SearchTermColumn" TEXT NOT NULL DEFAULT "Term",
		PRIMARY KEY(RowId));

CREATE TABLE "CivilopediaSections" (
		"SectionId" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Icon" TEXT,
		"SortIndex" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(SectionId));

CREATE TABLE "CivilopediaSectionExcludes" (
		"SectionId" TEXT NOT NULL,
		PRIMARY KEY(SectionId));

CREATE TABLE "CivilopediaTranslateCharacters" (
		"RowID" INTEGER,
		"Character" TEXT NOT NULL,
		"TranslateCharacter" TEXT NOT NULL,
		PRIMARY KEY(RowID));

CREATE TABLE "Continents" (
		"ContinentType" TEXT NOT NULL,
		"Description" TEXT,
		PRIMARY KEY(ContinentType));

CREATE TABLE "CorporationNames" (
		"ID" INTEGER NOT NULL,
		"NameType" TEXT NOT NULL,
		"TextKey" TEXT NOT NULL,
		PRIMARY KEY(ID));

CREATE TABLE "DataTypes" (
		"TypeName" TEXT NOT NULL UNIQUE,
		"DataId" INTEGER NOT NULL UNIQUE,
		PRIMARY KEY(DataId));

CREATE TABLE "DealItems" (
		"DealItemType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"AllowDurationTrade" BOOLEAN NOT NULL CHECK (AllowDurationTrade IN (0,1)) DEFAULT 1,
		PRIMARY KEY(DealItemType));

CREATE TABLE "Defeats" (
		"DefeatType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Blurb" TEXT NOT NULL,
		"RequirementSetId" TEXT NOT NULL,
		"EnabledByDefault" BOOLEAN NOT NULL CHECK (EnabledByDefault IN (0,1)) DEFAULT 1,
		"OneMoreTurn" BOOLEAN CHECK (OneMoreTurn IN (0,1)) DEFAULT 0,
		"Global" BOOLEAN NOT NULL CHECK (Global IN (0,1)) DEFAULT 0,
		PRIMARY KEY(DefeatType),
		FOREIGN KEY (DefeatType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

-- Difficulties available. The game will assume there are at least 8 members of this table. Do not have less.
CREATE TABLE "Difficulties" (
		"DifficultyType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		PRIMARY KEY(DifficultyType));

-- Allows us to change the background and leader images on the diplomacy screen.
CREATE TABLE "DiplomacyInfo" (
		"Type" TEXT NOT NULL,
		"BackgroundImage" TEXT,
		PRIMARY KEY(Type));

CREATE TABLE "DiplomaticActions" (
		"DiplomaticActionType" TEXT NOT NULL,
		"Name" TEXT,
		"Description" TEXT,
		"CivilopediaKey" TEXT,
		"InitiatorPrereqCivic" TEXT,
		"InitiatorPrereqTech" TEXT,
		"TargetPrereqCivic" TEXT,
		"TargetPrereqTech" TEXT,
		"InitiatorObsoleteCivic" TEXT,
		"Cost" INTEGER NOT NULL DEFAULT 0,
		"RequiresCapitalPath" BOOLEAN NOT NULL CHECK (RequiresCapitalPath IN (0,1)) DEFAULT 0,
		"RequiresConvertedCity" BOOLEAN NOT NULL CHECK (RequiresConvertedCity IN (0,1)) DEFAULT 0,
		"RequiresOccupiedCity" BOOLEAN NOT NULL CHECK (RequiresOccupiedCity IN (0,1)) DEFAULT 0,
		"RequiresOccupiedFriendlyCity" BOOLEAN NOT NULL CHECK (RequiresOccupiedFriendlyCity IN (0,1)) DEFAULT 0,
		"RequiresWarOnAlliedCityState" BOOLEAN NOT NULL CHECK (RequiresWarOnAlliedCityState IN (0,1)) DEFAULT 0,
		"RequiresLeadXEras" INTEGER NOT NULL DEFAULT 0,
		"RequiresArchaeologyIntrusion" BOOLEAN NOT NULL CHECK (RequiresArchaeologyIntrusion IN (0,1)) DEFAULT 0,
		"RequiresAdjacentEmpires" BOOLEAN NOT NULL CHECK (RequiresAdjacentEmpires IN (0,1)) DEFAULT 0,
		"RequiresEspionageIntrusion" BOOLEAN NOT NULL CHECK (RequiresEspionageIntrusion IN (0,1)) DEFAULT 0,
		"NoCurrentDelegation" BOOLEAN NOT NULL CHECK (NoCurrentDelegation IN (0,1)) DEFAULT 0,
		"NoCurrentEmbassy" BOOLEAN NOT NULL CHECK (NoCurrentEmbassy IN (0,1)) DEFAULT 0,
		"NoCurrentOpenBorders" BOOLEAN NOT NULL CHECK (NoCurrentOpenBorders IN (0,1)) DEFAULT 0,
		"NoCurrentDenunciation" BOOLEAN NOT NULL CHECK (NoCurrentDenunciation IN (0,1)) DEFAULT 0,
		"NoCurrentDOF" BOOLEAN NOT NULL CHECK (NoCurrentDOF IN (0,1)) DEFAULT 0,
		"NoCurrentResearchAgreement" BOOLEAN NOT NULL CHECK (NoCurrentResearchAgreement IN (0,1)) DEFAULT 0,
		"NoCurrentDefensivePact" BOOLEAN NOT NULL CHECK (NoCurrentDefensivePact IN (0,1)) DEFAULT 0,
		"Agreement" BOOLEAN NOT NULL CHECK (Agreement IN (0,1)) DEFAULT 0,
		"WarmongerPercent" INTEGER NOT NULL DEFAULT 0,
		"CaptureWarmongerPercent" INTEGER NOT NULL DEFAULT 0,
		"RazeWarmongerPercent" INTEGER NOT NULL DEFAULT 0,
		"UIGroup" TEXT,
		"DenouncementTurnsRequired" INTEGER NOT NULL DEFAULT -1,
		"RequiresAlliance" BOOLEAN NOT NULL CHECK (RequiresAlliance IN (0,1)) DEFAULT 0,
		"RequiresTeamMembership" BOOLEAN NOT NULL CHECK (RequiresTeamMembership IN (0,1)) DEFAULT 0,
		"Duration" INTEGER NOT NULL DEFAULT 30,
		PRIMARY KEY(DiplomaticActionType),
		FOREIGN KEY (InitiatorPrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TargetPrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (InitiatorObsoleteCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (InitiatorPrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TargetPrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DiplomaticActionType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticStartStates" (
		"PlayerCivLevel" TEXT NOT NULL,
		"OpponentCivLevel" TEXT NOT NULL,
		"DiplomaticStateType" TEXT NOT NULL,
		PRIMARY KEY(PlayerCivLevel, OpponentCivLevel),
		FOREIGN KEY (PlayerCivLevel) REFERENCES CivilizationLevels(CivilizationLevelType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OpponentCivLevel) REFERENCES CivilizationLevels(CivilizationLevelType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DiplomaticStateType) REFERENCES DiplomaticStates(StateType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticStates" (
		"StateType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"DiplomaticYieldBonus" INTEGER NOT NULL DEFAULT 0,
		"RelationshipLevel" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(StateType));

CREATE TABLE "DiplomaticStateActions" (
		"StateType" INTEGER NOT NULL,
		"DiplomaticActionType" INTEGER NOT NULL,
		"AiAllowed" BOOLEAN NOT NULL CHECK (AiAllowed IN (0,1)) DEFAULT 1,
		"Worth" INTEGER NOT NULL DEFAULT 0,
		"Cost" INTEGER NOT NULL DEFAULT 0,
		"TransitionToState" TEXT,
		"TeamOnly" BOOLEAN NOT NULL CHECK (TeamOnly IN (0,1)) DEFAULT 0,
		PRIMARY KEY(StateType, DiplomaticActionType),
		FOREIGN KEY (StateType) REFERENCES DiplomaticStates(StateType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DiplomaticActionType) REFERENCES DiplomaticActions(DiplomaticActionType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TransitionToState) REFERENCES DiplomaticStates(StateType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticStateTransitions" (
		"BaseState" TEXT NOT NULL,
		"TransitionState" TEXT NOT NULL,
		"RequireTransitionMax" INTEGER,
		"ThrottleTurns" INTEGER NOT NULL DEFAULT 0,
		"AllowTransitionMin" INTEGER,
		"RequireTransitionMin" INTEGER,
		"AllowTransitionMax" INTEGER,
		"AllowTransitionCheck" TEXT,
		"OnTransitionAction" TEXT,
		PRIMARY KEY(BaseState, TransitionState, AllowTransitionCheck),
		FOREIGN KEY (TransitionState) REFERENCES DiplomaticStates(StateType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (BaseState) REFERENCES DiplomaticStates(StateType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticTriggers" (
		"TriggerType" TEXT NOT NULL,
		PRIMARY KEY(TriggerType));

CREATE TABLE "DiplomaticTriggeredTransitions" (
		"TriggerType" TEXT NOT NULL,
		"CivilizationLevel" TEXT NOT NULL,
		"OpponentCivilizationLevel" TEXT NOT NULL,
		"TransitionState" TEXT NOT NULL,
		PRIMARY KEY(TriggerType, CivilizationLevel, OpponentCivilizationLevel),
		FOREIGN KEY (TransitionState) REFERENCES DiplomaticStates(StateType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TriggerType) REFERENCES DiplomaticTriggers(TriggerType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CivilizationLevel) REFERENCES CivilizationLevels(CivilizationLevelType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OpponentCivilizationLevel) REFERENCES CivilizationLevels(CivilizationLevelType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticTriggers_RequiredStates" (
		"TriggerType" TEXT NOT NULL,
		"RequiredState" TEXT NOT NULL,
		PRIMARY KEY(TriggerType, RequiredState),
		FOREIGN KEY (TriggerType) REFERENCES DiplomaticTriggers(TriggerType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (RequiredState) REFERENCES DiplomaticStates(StateType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DiplomaticVisibilitySources" (
		"VisibilitySourceType" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"ActionDescription" TEXT NOT NULL,
		"GossipString" TEXT NOT NULL,
		"Trader" BOOLEAN NOT NULL CHECK (Trader IN (0,1)) DEFAULT 0,
		"Delegate" BOOLEAN NOT NULL CHECK (Delegate IN (0,1)) DEFAULT 0,
		"Ally" BOOLEAN NOT NULL CHECK (Ally IN (0,1)) DEFAULT 0,
		"Spy" BOOLEAN NOT NULL CHECK (Spy IN (0,1)) DEFAULT 0,
		"PrereqTech" TEXT,
		"TraitType" TEXT,
		"GreatPersonIndividualType" TEXT,
		"FromCitizen" BOOLEAN NOT NULL CHECK (FromCitizen IN (0,1)) DEFAULT 0,
		"LevelRequired" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(VisibilitySourceType),
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonIndividualType) REFERENCES GreatPersonIndividuals(GreatPersonIndividualType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Districts" (
		"DistrictType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"Coast" BOOLEAN NOT NULL CHECK (Coast IN (0,1)) DEFAULT 0,
		"Description" TEXT,
		"Cost" INTEGER NOT NULL DEFAULT 0,
		"RequiresPlacement" BOOLEAN NOT NULL CHECK (RequiresPlacement IN (0,1)),
		"RequiresPopulation" BOOLEAN NOT NULL CHECK (RequiresPopulation IN (0,1)) DEFAULT 1,
		"NoAdjacentCity" BOOLEAN NOT NULL CHECK (NoAdjacentCity IN (0,1)),
		"CityCenter" BOOLEAN NOT NULL CHECK (CityCenter IN (0,1)) DEFAULT 0,
		"Aqueduct" BOOLEAN NOT NULL CHECK (Aqueduct IN (0,1)),
		"InternalOnly" BOOLEAN NOT NULL CHECK (InternalOnly IN (0,1)),
		"ZOC" BOOLEAN CHECK (ZOC IN (0,1)) DEFAULT 0,
		"FreeEmbark" BOOLEAN NOT NULL CHECK (FreeEmbark IN (0,1)) DEFAULT 0,
		"HitPoints" INTEGER DEFAULT 0,
		"CaptureRemovesBuildings" BOOLEAN NOT NULL CHECK (CaptureRemovesBuildings IN (0,1)),
		"CaptureRemovesCityDefenses" BOOLEAN NOT NULL CHECK (CaptureRemovesCityDefenses IN (0,1)),
		"PlunderType" TEXT NOT NULL,
		"PlunderAmount" INTEGER NOT NULL DEFAULT 0,
		"TradeEmbark" BOOLEAN NOT NULL CHECK (TradeEmbark IN (0,1)) DEFAULT 0,
		"MilitaryDomain" TEXT NOT NULL,
		"CostProgressionModel" TEXT NOT NULL DEFAULT "NO_COST_PROGRESSION",
		"CostProgressionParam1" INTEGER NOT NULL DEFAULT 0,
		"TraitType" TEXT,
		"Appeal" INTEGER NOT NULL DEFAULT 0,
		"Housing" INTEGER NOT NULL DEFAULT 0,
		"Entertainment" INTEGER NOT NULL DEFAULT 0,
		"OnePerCity" BOOLEAN NOT NULL CHECK (OnePerCity IN (0,1)) DEFAULT 1,
		"AllowsHolyCity" BOOLEAN NOT NULL CHECK (AllowsHolyCity IN (0,1)) DEFAULT 0,
		"Maintenance" INTEGER NOT NULL DEFAULT 0,
		"AirSlots" INTEGER NOT NULL DEFAULT 0,
		"CitizenSlots" INTEGER,
		"TravelTime" INTEGER NOT NULL DEFAULT -1,
		"CityStrengthModifier" INTEGER NOT NULL DEFAULT 0,
		"AdjacentToLand" BOOLEAN NOT NULL CHECK (AdjacentToLand IN (0,1)) DEFAULT 0,
		"CanAttack" BOOLEAN NOT NULL CHECK (CanAttack IN (0,1)) DEFAULT 0,
		"AdvisorType" TEXT,
		"CaptureRemovesDistrict" BOOLEAN NOT NULL CHECK (CaptureRemovesDistrict IN (0,1)) DEFAULT 0,
		"MaxPerPlayer" REAL NOT NULL DEFAULT -1,
		PRIMARY KEY(DistrictType),
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (DistrictType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "District_Adjacencies" (
		"DistrictType" TEXT NOT NULL,
		"YieldChangeId" TEXT NOT NULL,
		PRIMARY KEY(DistrictType, YieldChangeId),
		FOREIGN KEY (YieldChangeId) REFERENCES Adjacency_YieldChanges(ID) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "District_CitizenGreatPersonPoints" (
		"DistrictType" TEXT NOT NULL,
		"GreatPersonClassType" TEXT NOT NULL,
		"PointsPerTurn" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(DistrictType, GreatPersonClassType),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonClassType) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "District_CitizenYieldChanges" (
		"DistrictType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(DistrictType, YieldType),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "District_GreatPersonPoints" (
		"DistrictType" TEXT NOT NULL,
		"GreatPersonClassType" TEXT NOT NULL,
		"PointsPerTurn" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(DistrictType, GreatPersonClassType),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonClassType) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "District_RequiredFeatures" (
		"DistrictType" TEXT NOT NULL,
		"FeatureType" TEXT NOT NULL,
		PRIMARY KEY(DistrictType, FeatureType),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "District_TradeRouteYields" (
		"DistrictType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChangeAsOrigin" REAL NOT NULL DEFAULT 0,
		"YieldChangeAsDomesticDestination" REAL NOT NULL DEFAULT 0,
		"YieldChangeAsInternationalDestination" REAL NOT NULL DEFAULT 0,
		PRIMARY KEY(DistrictType, YieldType),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "District_ValidTerrains" (
		"DistrictType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(DistrictType, TerrainType),
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DistrictModifiers" (
		"DistrictType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(DistrictType, ModifierId),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DistrictReplaces" (
		"CivUniqueDistrictType" TEXT NOT NULL,
		"ReplacesDistrictType" TEXT NOT NULL,
		PRIMARY KEY(CivUniqueDistrictType),
		FOREIGN KEY (CivUniqueDistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ReplacesDistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DuplicateCivilizations" (
		"CivilizationType" TEXT NOT NULL,
		"OtherCivilizationType" TEXT NOT NULL,
		PRIMARY KEY(CivilizationType, OtherCivilizationType),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OtherCivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DuplicateLeaders" (
		"LeaderType" TEXT NOT NULL,
		"OtherLeaderType" TEXT NOT NULL,
		PRIMARY KEY(LeaderType, OtherLeaderType),
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (OtherLeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "DynamicModifiers" (
		"ModifierType" TEXT NOT NULL,
		"CollectionType" TEXT NOT NULL,
		"EffectType" TEXT NOT NULL,
		PRIMARY KEY(ModifierType),
		FOREIGN KEY (CollectionType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ModifierType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (EffectType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Eras" (
		"EraType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT,
		"ChronologyIndex" INTEGER NOT NULL UNIQUE,
		"WarmongerPoints" INTEGER NOT NULL DEFAULT 0,
		"GreatPersonBaseCost" INTEGER NOT NULL,
		"EraTechBackgroundTexture" TEXT,
		"EraCivicBackgroundTexture" TEXT,
		"WarmongerLevelDescription" TEXT,
		"EmbarkedUnitStrength" INTEGER NOT NULL,
		"EraTechBackgroundTextureOffsetX" INTEGER NOT NULL DEFAULT 0,
		"EraCivicBackgroundTextureOffsetX" INTEGER NOT NULL DEFAULT 0,
		"TechTreeLayoutMethod" INTEGER,
		PRIMARY KEY(EraType),
		FOREIGN KEY (EraType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "EventPopupData" (
		"Type" TEXT NOT NULL UNIQUE,
		"Title" TEXT NOT NULL,
		"Description" TEXT,
		"BackgroundImage" TEXT,
		"ForegroundImage" TEXT,
		"Effects" TEXT,
		"ImageText" TEXT,
		"FilterCondition" TEXT,
		"EffectType" TEXT,
		PRIMARY KEY(Type));

CREATE TABLE "ExcludedAdjacencies" (
		"TraitType" TEXT NOT NULL,
		"YieldChangeId" TEXT NOT NULL,
		PRIMARY KEY(TraitType, YieldChangeId),
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldChangeId) REFERENCES Adjacency_YieldChanges(ID) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ExcludedDistricts" (
		"DistrictType" TEXT NOT NULL,
		"TraitType" TEXT NOT NULL,
		PRIMARY KEY(DistrictType, TraitType),
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ExcludedGreatPersonClasses" (
		"GreatPersonClassType" TEXT NOT NULL,
		"TraitType" TEXT NOT NULL,
		PRIMARY KEY(GreatPersonClassType, TraitType),
		FOREIGN KEY (GreatPersonClassType) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Combinations of agenda that cannot appear on the same AI. These are symmetric
CREATE TABLE "ExclusiveAgendas" (
		"AgendaOne" TEXT NOT NULL,
		"AgendaTwo" TEXT NOT NULL,
		PRIMARY KEY(AgendaOne, AgendaTwo),
		FOREIGN KEY (AgendaOne) REFERENCES Agendas(AgendaType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AgendaTwo) REFERENCES Agendas(AgendaType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Table of suggested religions. Will try to match leader first, then civ, then random pick
CREATE TABLE "FavoredReligions" (
		"LeaderType" TEXT,
		"CivilizationType" TEXT,
		"ReligionType" TEXT NOT NULL,
		PRIMARY KEY(LeaderType, CivilizationType, ReligionType),
		FOREIGN KEY (ReligionType) REFERENCES Religions(ReligionType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Features" (
		"FeatureType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT UNIQUE,
		"Quote" TEXT UNIQUE,
		"Coast" BOOLEAN NOT NULL CHECK (Coast IN (0,1)) DEFAULT 0,
		"NoCoast" BOOLEAN NOT NULL CHECK (NoCoast IN (0,1)) DEFAULT 0,
		"NoRiver" BOOLEAN NOT NULL CHECK (NoRiver IN (0,1)) DEFAULT 0,
		"NoAdjacentFeatures" BOOLEAN NOT NULL CHECK (NoAdjacentFeatures IN (0,1)) DEFAULT 0,
		"RequiresRiver" BOOLEAN NOT NULL CHECK (RequiresRiver IN (0,1)) DEFAULT 0,
		"MovementChange" INTEGER NOT NULL DEFAULT 0,
		"SightThroughModifier" INTEGER NOT NULL DEFAULT 0,
		"Impassable" BOOLEAN NOT NULL CHECK (Impassable IN (0,1)) DEFAULT 0,
		"NaturalWonder" BOOLEAN NOT NULL CHECK (NaturalWonder IN (0,1)) DEFAULT 0,
		"RemoveTech" TEXT,
		"Removable" BOOLEAN NOT NULL CHECK (Removable IN (0,1)) DEFAULT 0,
		"AddCivic" TEXT,
		"DefenseModifier" INTEGER NOT NULL DEFAULT 0,
		"AddsFreshWater" BOOLEAN NOT NULL CHECK (AddsFreshWater IN (0,1)) DEFAULT 0,
		"Appeal" INTEGER NOT NULL DEFAULT 0,
		"MinDistanceLand" INTEGER NOT NULL DEFAULT 0,
		"MaxDistanceLand" INTEGER NOT NULL DEFAULT 0,
		"NotNearFeature" BOOLEAN NOT NULL CHECK (NotNearFeature IN (0,1)) DEFAULT 0,
		"Lake" BOOLEAN NOT NULL CHECK (Lake IN (0,1)) DEFAULT 0,
		"Tiles" INTEGER NOT NULL DEFAULT 1,
		"Adjacent" BOOLEAN NOT NULL CHECK (Adjacent IN (0,1)) DEFAULT 1,
		"NoResource" BOOLEAN NOT NULL CHECK (NoResource IN (0,1)) DEFAULT 0,
		"DoubleAdjacentTerrainYield" BOOLEAN NOT NULL CHECK (DoubleAdjacentTerrainYield IN (0,1)) DEFAULT 0,
		"NotCliff" BOOLEAN NOT NULL CHECK (NotCliff IN (0,1)) DEFAULT 0,
		"MinDistanceNW" INTEGER NOT NULL DEFAULT -1,
		"CustomPlacement" TEXT,
		"Forest" BOOLEAN NOT NULL CHECK (Forest IN (0,1)) DEFAULT 0,
		"AntiquityPriority" INTEGER NOT NULL DEFAULT 0,
		"QuoteAudio" TEXT,
		"Settlement" BOOLEAN NOT NULL CHECK (Settlement IN (0,1)) DEFAULT 1,
		"FollowRulesInWB" BOOLEAN NOT NULL CHECK (FollowRulesInWB IN (0,1)) DEFAULT 1,
		"DangerValue" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(FeatureType),
		FOREIGN KEY (RemoveTech) REFERENCES Technologies(TechnologyType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (AddCivic) REFERENCES Civics(CivicType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_AdjacentFeatures" (
		"FeatureType" TEXT NOT NULL,
		"FeatureTypeAdjacent" TEXT NOT NULL,
		PRIMARY KEY(FeatureType, FeatureTypeAdjacent),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureTypeAdjacent) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_AdjacentTerrains" (
		"FeatureType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(FeatureType, TerrainType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_AdjacentYields" (
		"FeatureType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(FeatureType, YieldType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_NotAdjacentTerrains" (
		"FeatureType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(FeatureType, TerrainType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_NotNearFeatures" (
		"FeatureType" TEXT NOT NULL,
		"FeatureTypeAvoid" TEXT NOT NULL,
		PRIMARY KEY(FeatureType, FeatureTypeAvoid),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureTypeAvoid) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_Removes" (
		"FeatureType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"Yield" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(FeatureType, YieldType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Unit Movement modifiers for a feature
CREATE TABLE "Feature_UnitMovements" (
		"FeatureType" TEXT NOT NULL,
		"AllowPassthrough" BOOLEAN NOT NULL CHECK (AllowPassthrough IN (0,1)) DEFAULT 1,
		"AllowDestination" BOOLEAN NOT NULL CHECK (AllowDestination IN (0,1)) DEFAULT 1,
		PRIMARY KEY(FeatureType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_ValidTerrains" (
		"FeatureType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(FeatureType, TerrainType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Feature_YieldChanges" (
		"FeatureType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(FeatureType, YieldType),
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Flavors" (
		"FlavorType" TEXT NOT NULL UNIQUE,
		PRIMARY KEY(FlavorType));

CREATE TABLE "GameCapabilities" (
		"GameCapability" TEXT,
		PRIMARY KEY(GameCapability),
		FOREIGN KEY (GameCapability) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GameCapabilityDependencies" (
		"ID" INTEGER,
		"GameCapability" INTEGER,
		"DependsOnCapability" TEXT,
		PRIMARY KEY(ID),
		FOREIGN KEY (GameCapability) REFERENCES GameCapabilities(GameCapability) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DependsOnCapability) REFERENCES GameCapabilities(GameCapability) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GameEffects" (
		"Type" TEXT,
		"CommonName" TEXT,
		"Description" TEXT,
		"Tags" TEXT,
		"GameCapabilities" TEXT,
		"ContextInterfaces" TEXT,
		"SubjectInterfaces" TEXT,
		"SupportsRemove" BOOLEAN CHECK (SupportsRemove IN (0,1)),
		PRIMARY KEY(Type),
		FOREIGN KEY (Type) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GameEffectArguments" (
		"Type" TEXT,
		"Name" TEXT NOT NULL,
		"CommonName" TEXT,
		"Description" TEXT,
		"ArgumentType" TEXT,
		"DefaultValue" TEXT,
		"Required" BOOLEAN NOT NULL CHECK (Required IN (0,1)) DEFAULT 0,
		"MinValue" TEXT,
		"MaxValue" TEXT,
		"DatabaseKind" TEXT,
		PRIMARY KEY(Type, Name),
		FOREIGN KEY (Type) REFERENCES GameEffects(Type) ON DELETE CASCADE ON UPDATE CASCADE);

-- A Set of modifiers that are attached to the game upon start-up.
CREATE TABLE "GameModifiers" (
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(ModifierId));

CREATE TABLE "GameSpeeds" (
		"GameSpeedType" TEXT NOT NULL,
		"Name" TEXT,
		"Description" TEXT,
		"CostMultiplier" INTEGER NOT NULL DEFAULT 100,
		"CivicUnlockMaxCost" INTEGER NOT NULL,
		"CivicUnlockPerTurnDrop" INTEGER NOT NULL,
		"CivicUnlockMinCost" INTEGER NOT NULL,
		PRIMARY KEY(GameSpeedType));

CREATE TABLE "GameSpeed_Durations" (
		"GameSpeedScalingType" TEXT NOT NULL,
		"NumberOfTurnsOnStandard" INTEGER NOT NULL,
		"NumberOfTurnsScaled" INTEGER NOT NULL,
		PRIMARY KEY(GameSpeedScalingType, NumberOfTurnsOnStandard),
		FOREIGN KEY (GameSpeedScalingType) REFERENCES GameSpeed_Scalings(GameSpeedScalingType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GameSpeed_Scalings" (
		"GameSpeedScalingType" TEXT NOT NULL,
		"GameSpeedType" TEXT NOT NULL,
		"ScalingType" TEXT NOT NULL,
		"DefaultCostMultiplier" INTEGER NOT NULL DEFAULT 100,
		PRIMARY KEY(GameSpeedScalingType),
		FOREIGN KEY (GameSpeedType) REFERENCES GameSpeeds(GameSpeedType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GameSpeed_Turns" (
		"GameSpeedType" TEXT NOT NULL,
		"MonthIncrement" INTEGER NOT NULL,
		"TurnsPerIncrement" INTEGER NOT NULL,
		PRIMARY KEY(GameSpeedType, MonthIncrement, TurnsPerIncrement),
		FOREIGN KEY (GameSpeedType) REFERENCES GameSpeeds(GameSpeedType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GlobalParameters" (
		"Name" TEXT NOT NULL,
		"Value" TEXT NOT NULL,
		PRIMARY KEY(Name));

CREATE TABLE "GoodyHuts" (
		"GoodyHutType" TEXT NOT NULL,
		"ImprovementType" TEXT NOT NULL DEFAULT "IMPROVEMENT_GOODY_HUT",
		"Weight" INTEGER NOT NULL,
		"ShowMoment" BOOLEAN NOT NULL CHECK (ShowMoment IN (0,1)) DEFAULT 1,
		PRIMARY KEY(GoodyHutType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GoodyHutSubTypes" (
		"GoodyHut" TEXT NOT NULL,
		"SubTypeGoodyHut" TEXT NOT NULL UNIQUE,
		"Description" TEXT,
		"Weight" INTEGER NOT NULL,
		"ModifierID" TEXT NOT NULL,
		"UpgradeUnit" BOOLEAN NOT NULL CHECK (UpgradeUnit IN (0,1)) DEFAULT 0,
		"Turn" INTEGER NOT NULL DEFAULT 0,
		"Experience" BOOLEAN NOT NULL CHECK (Experience IN (0,1)) DEFAULT 0,
		"Heal" INTEGER NOT NULL DEFAULT 0,
		"Relic" BOOLEAN NOT NULL CHECK (Relic IN (0,1)) DEFAULT 0,
		"Trader" BOOLEAN NOT NULL CHECK (Trader IN (0,1)) DEFAULT 0,
		"MinOneCity" BOOLEAN NOT NULL CHECK (MinOneCity IN (0,1)) DEFAULT 0,
		"RequiresUnit" BOOLEAN NOT NULL CHECK (RequiresUnit IN (0,1)) DEFAULT 0,
		PRIMARY KEY(SubTypeGoodyHut),
		FOREIGN KEY (GoodyHut) REFERENCES GoodyHuts(GoodyHutType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Gossips" (
		"GossipType" TEXT NOT NULL UNIQUE,
		"VisibilityLevel" INTEGER NOT NULL DEFAULT 0,
		"Description" TEXT,
		"Message" TEXT NOT NULL,
		"Filter" BOOLEAN NOT NULL CHECK (Filter IN (0,1)) DEFAULT 1,
		"ErasUntilObsolete" INTEGER NOT NULL DEFAULT 0,
		"LevelRequired" INTEGER NOT NULL DEFAULT 0,
		"GroupType" TEXT,
		PRIMARY KEY(GossipType),
		FOREIGN KEY (GossipType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Governments" (
		"GovernmentType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"PrereqCivic" TEXT,
		"InherentBonusDesc" TEXT NOT NULL,
		"AccumulatedBonusShortDesc" TEXT NOT NULL,
		"AccumulatedBonusDesc" TEXT NOT NULL,
		"OtherGovernmentIntolerance" INTEGER NOT NULL DEFAULT 0,
		"InfluencePointsPerTurn" INTEGER NOT NULL,
		"InfluencePointsThreshold" INTEGER NOT NULL,
		"InfluenceTokensPerThreshold" INTEGER NOT NULL,
		"BonusType" TEXT NOT NULL,
		"PolicyToUnlock" TEXT,
		"Tier" TEXT,
		PRIMARY KEY(GovernmentType),
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (BonusType) REFERENCES GovernmentBonusNames(GovernmentBonusType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (GovernmentType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PolicyToUnlock) REFERENCES Policies(PolicyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Tier) REFERENCES GovernmentTiers(TierType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Government_SlotCounts" (
		"GovernmentType" TEXT NOT NULL,
		"GovernmentSlotType" TEXT NOT NULL,
		"NumSlots" INTEGER NOT NULL,
		PRIMARY KEY(GovernmentType, GovernmentSlotType),
		FOREIGN KEY (GovernmentType) REFERENCES Governments(GovernmentType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GovernmentSlotType) REFERENCES GovernmentSlots(GovernmentSlotType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernmentBonusNames" (
		"GovernmentBonusType" TEXT NOT NULL,
		PRIMARY KEY(GovernmentBonusType));

CREATE TABLE "GovernmentModifiers" (
		"GovernmentType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(GovernmentType, ModifierId),
		FOREIGN KEY (GovernmentType) REFERENCES Governments(GovernmentType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GovernmentSlots" (
		"GovernmentSlotType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"AllowsAnyPolicy" BOOLEAN NOT NULL CHECK (AllowsAnyPolicy IN (0,1)),
		PRIMARY KEY(GovernmentSlotType));

CREATE TABLE "GovernmentTiers" (
		"TierType" TEXT NOT NULL,
		"Sorting" INTEGER NOT NULL,
		PRIMARY KEY(TierType));

CREATE TABLE "GreatPersonClasses" (
		"GreatPersonClassType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"UnitType" TEXT NOT NULL,
		"DistrictType" TEXT NOT NULL,
		"MaxPlayerInstances" INTEGER,
		"PseudoYieldType" TEXT,
		"IconString" TEXT NOT NULL,
		"ActionIcon" TEXT NOT NULL,
		"AvailableInTimeline" BOOLEAN NOT NULL CHECK (AvailableInTimeline IN (0,1)) DEFAULT 1,
		"GenerateDuplicateIndividuals" BOOLEAN NOT NULL CHECK (GenerateDuplicateIndividuals IN (0,1)) DEFAULT 0,
		PRIMARY KEY(GreatPersonClassType),
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PseudoYieldType) REFERENCES PseudoYields(PseudoYieldType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonClassType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatPersonIndividuals" (
		"GreatPersonIndividualType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"GreatPersonClassType" TEXT NOT NULL,
		"EraType" TEXT NOT NULL,
		"ActionCharges" INTEGER NOT NULL,
		"ActionRequiresOwnedTile" BOOLEAN NOT NULL CHECK (ActionRequiresOwnedTile IN (0,1)) DEFAULT 1,
		"ActionRequiresUnownedTile" BOOLEAN NOT NULL CHECK (ActionRequiresUnownedTile IN (0,1)) DEFAULT 0,
		"ActionRequiresAdjacentMountain" BOOLEAN NOT NULL CHECK (ActionRequiresAdjacentMountain IN (0,1)) DEFAULT 0,
		"ActionRequiresAdjacentOwnedTile" BOOLEAN NOT NULL CHECK (ActionRequiresAdjacentOwnedTile IN (0,1)) DEFAULT 0,
		"ActionRequiresAdjacentBarbarianUnit" BOOLEAN NOT NULL CHECK (ActionRequiresAdjacentBarbarianUnit IN (0,1)) DEFAULT 0,
		"ActionRequiresOnOrAdjacentNaturalWonder" BOOLEAN NOT NULL CHECK (ActionRequiresOnOrAdjacentNaturalWonder IN (0,1)) DEFAULT 0,
		"ActionRequiresOnOrAdjacentFeatureType" TEXT,
		"ActionRequiresIncompleteWonder" BOOLEAN NOT NULL CHECK (ActionRequiresIncompleteWonder IN (0,1)) DEFAULT 0,
		"ActionRequiresIncompleteSpaceRaceProject" BOOLEAN NOT NULL CHECK (ActionRequiresIncompleteSpaceRaceProject IN (0,1)) DEFAULT 0,
		"ActionRequiresVisibleLuxury" BOOLEAN NOT NULL CHECK (ActionRequiresVisibleLuxury IN (0,1)) DEFAULT 0,
		"ActionRequiresNoMilitaryUnit" BOOLEAN NOT NULL CHECK (ActionRequiresNoMilitaryUnit IN (0,1)) DEFAULT 0,
		"ActionRequiresPlayerRelicSlot" BOOLEAN NOT NULL CHECK (ActionRequiresPlayerRelicSlot IN (0,1)) DEFAULT 0,
		"ActionRequiresMilitaryUnitDomain" TEXT,
		"ActionRequiresUnitMilitaryFormation" TEXT,
		"ActionRequiresNearbyUnitWithTagA" TEXT,
		"ActionRequiresNearbyUnitWithTagB" TEXT,
		"ActionRequiresLandMilitaryUnitWithinXTiles" INTEGER,
		"ActionRequiresEnemyMilitaryUnitWithinXTiles" INTEGER,
		"ActionRequiresCityGreatWorkObjectType" TEXT,
		"ActionRequiresCompletedDistrictType" TEXT,
		"ActionRequiresMissingBuildingType" TEXT,
		"ActionRequiresGoldCost" INTEGER,
		"ActionNameTextOverride" TEXT,
		"ActionEffectTextOverride" TEXT,
		"ActionEffectTileHighlighting" BOOLEAN NOT NULL CHECK (ActionEffectTileHighlighting IN (0,1)) DEFAULT 1,
		"BirthNameTextOverride" TEXT,
		"BirthEffectTextOverride" TEXT,
		"AreaHighlightRadius" INTEGER,
		"Gender" TEXT NOT NULL,
		"ActionRequiresEnemyTerritory" BOOLEAN NOT NULL CHECK (ActionRequiresEnemyTerritory IN (0,1)) DEFAULT 0,
		"ActionRequiresCityStateTerritory" BOOLEAN NOT NULL CHECK (ActionRequiresCityStateTerritory IN (0,1)) DEFAULT 0,
		"ActionRequiresNonHostileTerritory" BOOLEAN NOT NULL CHECK (ActionRequiresNonHostileTerritory IN (0,1)) DEFAULT 0,
		"ActionRequiresSuzerainTerritory" BOOLEAN NOT NULL CHECK (ActionRequiresSuzerainTerritory IN (0,1)) DEFAULT 0,
		"ActionRequiresUnitCanGainExperience" BOOLEAN NOT NULL CHECK (ActionRequiresUnitCanGainExperience IN (0,1)) DEFAULT 0,
		PRIMARY KEY(GreatPersonIndividualType),
		FOREIGN KEY (GreatPersonClassType) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (EraType) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ActionRequiresCompletedDistrictType) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ActionRequiresOnOrAdjacentFeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ActionRequiresCityGreatWorkObjectType) REFERENCES GreatWorkObjectTypes(GreatWorkObjectType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ActionRequiresMissingBuildingType) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonIndividualType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatPersonIndividualActionModifiers" (
		"GreatPersonIndividualType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		"AttachmentTargetType" TEXT NOT NULL DEFAULT "GREAT_PERSON_ACTION_ATTACHMENT_TARGET_PLAYER",
		PRIMARY KEY(GreatPersonIndividualType, ModifierId),
		FOREIGN KEY (GreatPersonIndividualType) REFERENCES GreatPersonIndividuals(GreatPersonIndividualType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatPersonIndividualBirthModifiers" (
		"GreatPersonIndividualType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(GreatPersonIndividualType, ModifierId),
		FOREIGN KEY (GreatPersonIndividualType) REFERENCES GreatPersonIndividuals(GreatPersonIndividualType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatPersonIndividualIconModifiers" (
		"GreatPersonIndividualType" TEXT NOT NULL UNIQUE,
		"OverrideUnitIcon" TEXT NOT NULL,
		PRIMARY KEY(GreatPersonIndividualType));

CREATE TABLE "GreatWorks" (
		"GreatWorkType" TEXT NOT NULL,
		"GreatWorkObjectType" TEXT NOT NULL,
		"GreatPersonIndividualType" TEXT,
		"Name" TEXT NOT NULL,
		"Audio" TEXT,
		"Image" TEXT,
		"Quote" TEXT,
		"Tourism" INTEGER NOT NULL DEFAULT 1,
		"EraType" TEXT,
		PRIMARY KEY(GreatWorkType),
		FOREIGN KEY (EraType) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonIndividualType) REFERENCES GreatPersonIndividuals(GreatPersonIndividualType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatWorkObjectType) REFERENCES GreatWorkObjectTypes(GreatWorkObjectType) ON DELETE RESTRICT ON UPDATE CASCADE);

CREATE TABLE "GreatWorks_ImprovementType" (
		"GreatWorkType" TEXT NOT NULL,
		"ImprovementType" TEXT,
		"ResourceType" TEXT,
		PRIMARY KEY(GreatWorkType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatWorkType) REFERENCES GreatWorks(GreatWorkType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatWork_ValidSubTypes" (
		"GreatWorkSlotType" TEXT NOT NULL,
		"GreatWorkObjectType" TEXT NOT NULL,
		PRIMARY KEY(GreatWorkSlotType, GreatWorkObjectType),
		FOREIGN KEY (GreatWorkObjectType) REFERENCES GreatWorkObjectTypes(GreatWorkObjectType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatWorkSlotType) REFERENCES GreatWorkSlotTypes(GreatWorkSlotType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatWork_YieldChanges" (
		"GreatWorkType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(GreatWorkType, YieldType),
		FOREIGN KEY (GreatWorkType) REFERENCES GreatWorks(GreatWorkType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatWorkModifiers" (
		"GreatWorkType" TEXT NOT NULL,
		"ModifierID" TEXT NOT NULL,
		PRIMARY KEY(GreatWorkType, ModifierID),
		FOREIGN KEY (GreatWorkType) REFERENCES GreatWorks(GreatWorkType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatWorkObjectTypes" (
		"GreatWorkObjectType" TEXT NOT NULL,
		"Value" INTEGER NOT NULL UNIQUE,
		"PseudoYieldType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"IconString" TEXT NOT NULL,
		PRIMARY KEY(GreatWorkObjectType),
		FOREIGN KEY (PseudoYieldType) REFERENCES PseudoYields(PseudoYieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "GreatWorkSlotTypes" (
		"GreatWorkSlotType" TEXT NOT NULL,
		PRIMARY KEY(GreatWorkSlotType));

CREATE TABLE "Happinesses" (
		"HappinessType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"MinimumAmenityScore" INTEGER,
		"MaximumAmenityScore" INTEGER,
		"GrowthModifier" REAL DEFAULT 1,
		"NonFoodYieldModifier" REAL DEFAULT 1,
		"RebellionPoints" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(HappinessType));

CREATE TABLE "HeroClasses" (
		"HeroClassType" TEXT NOT NULL,
		"Name" LocalizedText NOT NULL,
		"Description" LocalizedText NOT NULL,
		"UnitType" TEXT NOT NULL,
		"CreationProjectType" TEXT NOT NULL,
		"ArtifactGreatWorkType" TEXT,
		"EpicGreatWorkType" TEXT,
		"DiscoveryMinEraType" TEXT,
		PRIMARY KEY(HeroClassType),
		FOREIGN KEY (HeroClassType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ArtifactGreatWorkType) REFERENCES GreatWorks(GreatWorkType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (EpicGreatWorkType) REFERENCES GreatWorks(GreatWorkType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CreationProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (DiscoveryMinEraType) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "HeroClassProgressions" (
		"HeroClassType" TEXT NOT NULL,
		"EraType" TEXT NOT NULL,
		"CombatStrength" INTEGER,
		"RangedCombatStrength" INTEGER,
		"AbilityCharges" INTEGER,
		PRIMARY KEY(HeroClassType, EraType),
		FOREIGN KEY (HeroClassType) REFERENCES HeroClasses(HeroClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "HeroClassUnitCommands" (
		"HeroClassType" TEXT NOT NULL,
		"UnitCommandType" TEXT NOT NULL,
		"Passive" BOOLEAN CHECK (Passive IN (0,1)) DEFAULT 0,
		PRIMARY KEY(HeroClassType, UnitCommandType),
		FOREIGN KEY (UnitCommandType) REFERENCES UnitCommands(CommandType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (HeroClassType) REFERENCES HeroClasses(HeroClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "HistoricalAgendas" (
		"LeaderType" TEXT NOT NULL,
		"AgendaType" TEXT NOT NULL,
		PRIMARY KEY(LeaderType, AgendaType),
		FOREIGN KEY (AgendaType) REFERENCES Agendas(AgendaType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "HistoricRankings" (
		"HistoricLeader" TEXT,
		"Quote" TEXT,
		"Score" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(HistoricLeader));

CREATE TABLE "Improvements" (
		"ImprovementType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"BarbarianCamp" BOOLEAN NOT NULL CHECK (BarbarianCamp IN (0,1)) DEFAULT 0,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"Buildable" BOOLEAN NOT NULL CHECK (Buildable IN (0,1)) DEFAULT 0,
		"Description" TEXT,
		"RemoveOnEntry" BOOLEAN NOT NULL CHECK (RemoveOnEntry IN (0,1)) DEFAULT 0,
		"DispersalGold" INTEGER NOT NULL DEFAULT 0,
		"PlunderType" TEXT NOT NULL,
		"PlunderAmount" INTEGER NOT NULL DEFAULT 0,
		"Goody" BOOLEAN NOT NULL CHECK (Goody IN (0,1)) DEFAULT 0,
		"TilesPerGoody" INTEGER,
		"GoodyRange" INTEGER,
		"Icon" TEXT NOT NULL,
		"TraitType" TEXT,
		"Housing" INTEGER NOT NULL DEFAULT 0,
		"TilesRequired" INTEGER NOT NULL DEFAULT 1,
		"SameAdjacentValid" BOOLEAN NOT NULL CHECK (SameAdjacentValid IN (0,1)) DEFAULT 1,
		"RequiresRiver" INTEGER NOT NULL DEFAULT 0,
		"EnforceTerrain" BOOLEAN NOT NULL CHECK (EnforceTerrain IN (0,1)) DEFAULT 0,
		"BuildInLine" BOOLEAN NOT NULL CHECK (BuildInLine IN (0,1)) DEFAULT 0,
		"CanBuildOutsideTerritory" BOOLEAN NOT NULL CHECK (CanBuildOutsideTerritory IN (0,1)) DEFAULT 0,
		"BuildOnFrontier" BOOLEAN NOT NULL CHECK (BuildOnFrontier IN (0,1)) DEFAULT 0,
		"AirSlots" INTEGER NOT NULL DEFAULT 0,
		"DefenseModifier" INTEGER NOT NULL DEFAULT 0,
		"GrantFortification" INTEGER NOT NULL DEFAULT 0,
		"MinimumAppeal" INTEGER,
		"Coast" BOOLEAN NOT NULL CHECK (Coast IN (0,1)) DEFAULT 0,
		"YieldFromAppeal" TEXT,
		"WeaponSlots" INTEGER NOT NULL DEFAULT 0,
		"ReligiousUnitHealRate" INTEGER NOT NULL DEFAULT 0,
		"Appeal" INTEGER NOT NULL DEFAULT 0,
		"OnePerCity" BOOLEAN NOT NULL CHECK (OnePerCity IN (0,1)) DEFAULT 0,
		"YieldFromAppealPercent" INTEGER NOT NULL DEFAULT 100,
		"ValidAdjacentTerrainAmount" INTEGER NOT NULL DEFAULT 0,
		"Domain" TEXT NOT NULL DEFAULT "DOMAIN_LAND",
		"AdjacentSeaResource" BOOLEAN NOT NULL CHECK (AdjacentSeaResource IN (0,1)) DEFAULT 0,
		"RequiresAdjacentBonusOrLuxury" BOOLEAN NOT NULL CHECK (RequiresAdjacentBonusOrLuxury IN (0,1)) DEFAULT 0,
		"MovementChange" INTEGER NOT NULL DEFAULT 0,
		"Workable" BOOLEAN NOT NULL CHECK (Workable IN (0,1)) DEFAULT 1,
		"ImprovementOnRemove" TEXT,
		"GoodyNotify" BOOLEAN NOT NULL CHECK (GoodyNotify IN (0,1)) DEFAULT 1,
		"NoAdjacentSpecialtyDistrict" BOOLEAN NOT NULL CHECK (NoAdjacentSpecialtyDistrict IN (0,1)) DEFAULT 0,
		"RequiresAdjacentLuxury" BOOLEAN NOT NULL CHECK (RequiresAdjacentLuxury IN (0,1)) DEFAULT 0,
		"AdjacentToLand" BOOLEAN NOT NULL CHECK (AdjacentToLand IN (0,1)) DEFAULT 0,
		"Removable" BOOLEAN NOT NULL CHECK (Removable IN (0,1)) DEFAULT 1,
		"OnlyOpenBorders" BOOLEAN NOT NULL CHECK (OnlyOpenBorders IN (0,1)) DEFAULT 0,
		"Capturable" BOOLEAN NOT NULL CHECK (Capturable IN (0,1)) DEFAULT 1,
		PRIMARY KEY(ImprovementType),
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (YieldFromAppeal) REFERENCES Yields(YieldType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (ImprovementType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_Adjacencies" (
		"ImprovementType" TEXT NOT NULL,
		"YieldChangeId" TEXT NOT NULL,
		PRIMARY KEY(ImprovementType, YieldChangeId),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldChangeId) REFERENCES Adjacency_YieldChanges(ID) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_BonusYieldChanges" (
		"Id" INTEGER NOT NULL DEFAULT 0,
		"ImprovementType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"BonusYieldChange" INTEGER NOT NULL,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		PRIMARY KEY(Id, ImprovementType, YieldType),
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_InvalidAdjacentFeatures" (
		"ImprovementType" TEXT NOT NULL,
		"FeatureType" TEXT NOT NULL,
		PRIMARY KEY(ImprovementType, FeatureType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvements_MODE" (
		"ImprovementType" TEXT NOT NULL,
		"Industry" BOOLEAN NOT NULL CHECK (Industry IN (0,1)) DEFAULT 0,
		"Corporation" BOOLEAN NOT NULL CHECK (Corporation IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ImprovementType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_Tourism" (
		"ImprovementType" TEXT NOT NULL,
		"TourismSource" TEXT NOT NULL DEFAULT "NO_TOURISMSOURCE",
		"PrereqCivic" TEXT,
		"PrereqTech" TEXT,
		"ScalingFactor" INTEGER NOT NULL DEFAULT 100,
		PRIMARY KEY(ImprovementType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_ValidAdjacentResources" (
		"ImprovementType" TEXT NOT NULL,
		"ResourceType" TEXT NOT NULL,
		PRIMARY KEY(ImprovementType, ResourceType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_ValidAdjacentTerrains" (
		"ImprovementType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(ImprovementType, TerrainType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_ValidBuildUnits" (
		"ImprovementType" TEXT NOT NULL,
		"UnitType" TEXT NOT NULL,
		"ConsumesCharge" BOOLEAN NOT NULL CHECK (ConsumesCharge IN (0,1)) DEFAULT 1,
		"ValidRepairOnly" BOOLEAN NOT NULL CHECK (ValidRepairOnly IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ImprovementType, UnitType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_ValidFeatures" (
		"ImprovementType" TEXT NOT NULL,
		"FeatureType" TEXT NOT NULL,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		PRIMARY KEY(ImprovementType, FeatureType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_ValidResources" (
		"ImprovementType" TEXT NOT NULL,
		"ResourceType" TEXT NOT NULL,
		"MustRemoveFeature" BOOLEAN NOT NULL CHECK (MustRemoveFeature IN (0,1)) DEFAULT 1,
		PRIMARY KEY(ImprovementType, ResourceType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_ValidTerrains" (
		"ImprovementType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		PRIMARY KEY(ImprovementType, TerrainType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_YieldChanges" (
		"ImprovementType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(ImprovementType, YieldType),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Improvement_YieldsOutsideTerritories" (
		"ImprovementType" TEXT NOT NULL,
		PRIMARY KEY(ImprovementType));

CREATE TABLE "ImprovementModifiers" (
		"ImprovementType" TEXT NOT NULL,
		"ModifierID" TEXT NOT NULL,
		PRIMARY KEY(ImprovementType, ModifierID),
		FOREIGN KEY (ImprovementType) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "InterfaceModes" (
		"ModeType" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"Help" TEXT,
		"DisabledHelp" TEXT,
		"Icon" TEXT NOT NULL,
		"VisibleInUI" BOOLEAN NOT NULL CHECK (VisibleInUI IN (0,1)),
		"CursorType" TEXT NOT NULL,
		PRIMARY KEY(ModeType));

CREATE TABLE "Kinds" (
		"Kind" TEXT NOT NULL,
		"Hash" INTEGER NOT NULL UNIQUE DEFAULT 0,
		PRIMARY KEY(Kind));

CREATE TABLE "Leaders" (
		"LeaderType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"OperationList" TEXT,
		"IsBarbarianLeader" BOOLEAN NOT NULL CHECK (IsBarbarianLeader IN (0,1)) DEFAULT 0,
		"InheritFrom" TEXT,
		"SceneLayers" INTEGER NOT NULL DEFAULT 0,
		"Sex" TEXT NOT NULL DEFAULT "Male",
		"SameSexPercentage" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(LeaderType),
		FOREIGN KEY (OperationList) REFERENCES AiOperationLists(ListType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (InheritFrom) REFERENCES Leaders(LeaderType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (LeaderType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

-- Random bits of information about the leader.
CREATE TABLE "LeaderInfo" (
		"LeaderType" TEXT NOT NULL,
		"Header" TEXT NOT NULL,
		"Caption" TEXT NOT NULL,
		"SortIndex" INTEGER NOT NULL DEFAULT 100,
		PRIMARY KEY(LeaderType, Header),
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "LeaderQuotes" (
		"LeaderType" TEXT NOT NULL,
		"Quote" TEXT NOT NULL,
		"QuoteAudio" TEXT,
		PRIMARY KEY(LeaderType, Quote),
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "LeaderTraits" (
		"LeaderType" TEXT NOT NULL,
		"TraitType" TEXT NOT NULL,
		PRIMARY KEY(LeaderType, TraitType),
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (LeaderType) REFERENCES Leaders(LeaderType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Allows us to change the background in the loading screen based on which leader the player selected.
CREATE TABLE "LoadingInfo" (
		"LeaderType" TEXT NOT NULL,
		"ForegroundImage" TEXT,
		"BackgroundImage" TEXT,
		"EraText" TEXT,
		"LeaderText" TEXT,
		"PlayDawnOfManAudio" BOOLEAN NOT NULL CHECK (PlayDawnOfManAudio IN (0,1)) DEFAULT 1,
		"DawnOfManLeaderId" TEXT,
		"DawnOfManEraId" TEXT,
		PRIMARY KEY(LeaderType),
		FOREIGN KEY (LeaderType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "MajorStartingUnits" (
		"Unit" TEXT NOT NULL,
		"Era" TEXT NOT NULL,
		"District" TEXT NOT NULL DEFAULT "DISTRICT_CITY_CENTER",
		"Quantity" INTEGER NOT NULL DEFAULT 1,
		"NotStartTile" BOOLEAN NOT NULL CHECK (NotStartTile IN (0,1)) DEFAULT 0,
		"OnDistrictCreated" BOOLEAN NOT NULL CHECK (OnDistrictCreated IN (0,1)) DEFAULT 0,
		"AiOnly" BOOLEAN NOT NULL CHECK (AiOnly IN (0,1)) DEFAULT 0,
		"MinDifficulty" TEXT,
		"DifficultyDelta" REAL NOT NULL DEFAULT 0,
		PRIMARY KEY(Unit, Era, District, MinDifficulty),
		FOREIGN KEY (Era) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Unit) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MinDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (District) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Maps" (
		"MapSizeType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT,
		"DefaultPlayers" INTEGER NOT NULL DEFAULT 0,
		"FogTilesPerBarbarianCamp" INTEGER NOT NULL DEFAULT 0,
		"NumNaturalWonders" INTEGER NOT NULL DEFAULT 0,
		"UnitNameModifier" INTEGER NOT NULL DEFAULT 0,
		"TargetNumCities" INTEGER NOT NULL DEFAULT 0,
		"GridWidth" INTEGER NOT NULL DEFAULT 0,
		"GridHeight" INTEGER NOT NULL DEFAULT 0,
		"TerrainGrainChange" INTEGER NOT NULL DEFAULT 0,
		"FeatureGrainChange" INTEGER NOT NULL DEFAULT 0,
		"ResearchPercent" INTEGER NOT NULL DEFAULT 0,
		"NumCitiesUnhealthPercent" INTEGER NOT NULL DEFAULT 0,
		"NumCitiesPolicyCostMod" INTEGER NOT NULL DEFAULT 0,
		"NumCitiesTechCostMod" INTEGER NOT NULL DEFAULT 0,
		"EstimatedNumCities" INTEGER NOT NULL DEFAULT 0,
		"PlateValue" INTEGER NOT NULL DEFAULT 4,
		"Continents" INTEGER NOT NULL DEFAULT 1,
		PRIMARY KEY(MapSizeType));

CREATE TABLE "Map_GreatPersonClasses" (
		"MapSizeType" TEXT NOT NULL,
		"GreatPersonClassType" TEXT NOT NULL,
		"MaxWorldInstances" INTEGER,
		PRIMARY KEY(MapSizeType, GreatPersonClassType),
		FOREIGN KEY (MapSizeType) REFERENCES Maps(MapSizeType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonClassType) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "MapRainfalls" (
		"MapRainfallType" TEXT NOT NULL UNIQUE,
		"Name" TEXT,
		"Description" TEXT,
		"AverageAmountPerYear" INTEGER,
		"Scale" REAL,
		PRIMARY KEY(MapRainfallType));

CREATE TABLE "MapResourceDistributions" (
		"MapResourceDistributionType" TEXT NOT NULL UNIQUE,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"Scale" REAL,
		PRIMARY KEY(MapResourceDistributionType));

CREATE TABLE "MapSeaLevels" (
		"MapSeaLevelType" TEXT NOT NULL UNIQUE,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"Scale" REAL,
		PRIMARY KEY(MapSeaLevelType));

-- Defines custom positions for maps.
CREATE TABLE "MapStartPositions" (
		"Map" TEXT NOT NULL,
		"Plot" INTEGER NOT NULL,
		"Type" TEXT NOT NULL,
		"Value" TEXT,
		PRIMARY KEY(Map, Plot));

CREATE TABLE "MapTemperatures" (
		"MapTemperatureType" TEXT NOT NULL UNIQUE,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"AverageStartingTemperature" REAL,
		"Scale" REAL,
		PRIMARY KEY(MapTemperatureType));

-- World Age for map generation
CREATE TABLE "MapWorldAges" (
		"MapWorldAgeType" TEXT NOT NULL UNIQUE,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"YearsOld" REAL,
		"Scale" REAL,
		PRIMARY KEY(MapWorldAgeType));

CREATE TABLE "Modifiers" (
		"ModifierId" TEXT NOT NULL,
		"ModifierType" TEXT NOT NULL,
		"RunOnce" BOOLEAN NOT NULL CHECK (RunOnce IN (0,1)) DEFAULT 0,
		"NewOnly" BOOLEAN NOT NULL CHECK (NewOnly IN (0,1)) DEFAULT 0,
		"Permanent" BOOLEAN NOT NULL CHECK (Permanent IN (0,1)) DEFAULT 0,
		"Repeatable" BOOLEAN CHECK (Repeatable IN (0,1)) DEFAULT 0,
		"OwnerRequirementSetId" TEXT,
		"SubjectRequirementSetId" TEXT,
		"OwnerStackLimit" INTEGER,
		"SubjectStackLimit" INTEGER,
		PRIMARY KEY(ModifierId),
		FOREIGN KEY (OwnerRequirementSetId) REFERENCES RequirementSets(RequirementSetId) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (SubjectRequirementSetId) REFERENCES RequirementSets(RequirementSetId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ModifierArguments" (
		"ModifierId" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Type" TEXT NOT NULL DEFAULT "ARGTYPE_IDENTITY",
		"Value" TEXT NOT NULL,
		"Extra" TEXT,
		"SecondExtra" TEXT,
		PRIMARY KEY(ModifierId, Name),
		FOREIGN KEY (ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ModifierStrings" (
		"ModifierId" TEXT NOT NULL,
		"Context" TEXT NOT NULL,
		"Text" TEXT NOT NULL,
		PRIMARY KEY(ModifierId, Context),
		FOREIGN KEY (ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Months" (
		"MonthType" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		PRIMARY KEY(MonthType));

CREATE TABLE "MutuallyExclusiveBuildings" (
		"Building" TEXT NOT NULL,
		"MutuallyExclusiveBuilding" TEXT NOT NULL,
		PRIMARY KEY(Building, MutuallyExclusiveBuilding),
		FOREIGN KEY (Building) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MutuallyExclusiveBuilding) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "MutuallyExclusiveDistricts" (
		"District" TEXT NOT NULL,
		"MutuallyExclusiveDistrict" TEXT NOT NULL,
		PRIMARY KEY(District, MutuallyExclusiveDistrict),
		FOREIGN KEY (District) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MutuallyExclusiveDistrict) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "NodeDataDefinitions" (
		"DataName" TEXT NOT NULL,
		"DefnId" INTEGER NOT NULL,
		"DataType" TEXT NOT NULL,
		"NodeType" TEXT NOT NULL,
		"Required" BOOLEAN NOT NULL CHECK (Required IN (0,1)) DEFAULT 0,
		"RequiredGroup" BOOLEAN NOT NULL CHECK (RequiredGroup IN (0,1)) DEFAULT 0,
		"Output" BOOLEAN NOT NULL CHECK (Output IN (0,1)) DEFAULT 0,
		"Modified" BOOLEAN NOT NULL CHECK (Modified IN (0,1)) DEFAULT 0,
		"UserData" BOOLEAN NOT NULL CHECK (UserData IN (0,1)) DEFAULT 0,
		"Automatic" BOOLEAN NOT NULL CHECK (Automatic IN (0,1)) DEFAULT 0,
		"Tagged" BOOLEAN NOT NULL CHECK (Tagged IN (0,1)) DEFAULT 0,
		"EnumList" TEXT,
		"UniqueId" INTEGER NOT NULL,
		PRIMARY KEY(UniqueId),
		FOREIGN KEY (DataType) REFERENCES DataTypes(TypeName) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (NodeType) REFERENCES NodeDefinitions(NodeType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "NodeDefinitions" (
		"NodeType" TEXT NOT NULL,
		"NodeId" INTEGER NOT NULL UNIQUE,
		"ShapeId" INTEGER NOT NULL,
		"Description" TEXT NOT NULL,
		PRIMARY KEY(NodeType),
		FOREIGN KEY (ShapeId) REFERENCES ShapeDefinitions(ShapeId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Notifications" (
		"NotificationType" TEXT NOT NULL UNIQUE,
		"Message" TEXT,
		"Summary" TEXT,
		"SeverityType" TEXT,
		"ExpiresEndOfTurn" BOOLEAN NOT NULL CHECK (ExpiresEndOfTurn IN (0,1)) DEFAULT 1,
		"ExpiresEndOfNextTurn" BOOLEAN NOT NULL CHECK (ExpiresEndOfNextTurn IN (0,1)) DEFAULT 0,
		"SubType" TEXT,
		"AutoNotify" BOOLEAN NOT NULL CHECK (AutoNotify IN (0,1)) DEFAULT 0,
		"GroupType" TEXT,
		"Icon" TEXT,
		"AutoActivate" BOOLEAN NOT NULL CHECK (AutoActivate IN (0,1)) DEFAULT 0,
		"VisibleInUI" BOOLEAN NOT NULL CHECK (VisibleInUI IN (0,1)) DEFAULT 1,
		"ShowIconSinglePlayer" BOOLEAN NOT NULL CHECK (ShowIconSinglePlayer IN (0,1)) DEFAULT 1,
		PRIMARY KEY(NotificationType));

CREATE TABLE "ObsoletePolicies" (
		"PolicyType" TEXT NOT NULL,
		"ObsoletePolicy" TEXT,
		"RequiresAvailableGreatPersonClass" TEXT,
		PRIMARY KEY(PolicyType, ObsoletePolicy),
		FOREIGN KEY (PolicyType) REFERENCES Policies(PolicyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ObsoletePolicy) REFERENCES Policies(PolicyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (RequiresAvailableGreatPersonClass) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "OpTeamRequirements" (
		"TeamName" TEXT NOT NULL,
		"AiType" TEXT NOT NULL,
		"MinNumber" INTEGER,
		"MaxNumber" INTEGER,
		"MinPercentage" REAL NOT NULL DEFAULT 0,
		"MaxPercentage" REAL NOT NULL DEFAULT 1,
		"ReconsiderWhilePreparing" BOOLEAN NOT NULL CHECK (ReconsiderWhilePreparing IN (0,1)) DEFAULT 0,
		"AiTypeDependence" TEXT,
		PRIMARY KEY(TeamName, AiType),
		FOREIGN KEY (AiType) REFERENCES UnitAiTypes(AiType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TeamName) REFERENCES AiTeams(TeamName) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AiTypeDependence) REFERENCES UnitAiTypes(AiType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "PlotEvalConditions" (
		"ConditionType" TEXT NOT NULL,
		"Value" INTEGER NOT NULL,
		"PoorValue" INTEGER NOT NULL DEFAULT 0,
		"PoorTooltipString" TEXT,
		"GoodValue" INTEGER NOT NULL DEFAULT 0,
		"GoodTooltipString" TEXT,
		PRIMARY KEY(ConditionType));

CREATE TABLE "Policies" (
		"PolicyType" TEXT NOT NULL,
		"Description" TEXT,
		"PrereqCivic" TEXT,
		"PrereqTech" TEXT,
		"Name" TEXT NOT NULL,
		"GovernmentSlotType" TEXT NOT NULL,
		"RequiresGovernmentUnlock" BOOLEAN CHECK (RequiresGovernmentUnlock IN (0,1)),
		"ExplicitUnlock" BOOLEAN NOT NULL CHECK (ExplicitUnlock IN (0,1)) DEFAULT 0,
		PRIMARY KEY(PolicyType),
		FOREIGN KEY (GovernmentSlotType) REFERENCES GovernmentSlots(GovernmentSlotType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PolicyType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "PolicyModifiers" (
		"PolicyType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(PolicyType, ModifierId),
		FOREIGN KEY (PolicyType) REFERENCES Policies(PolicyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Projects" (
		"ProjectType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"ShortName" TEXT NOT NULL,
		"Description" TEXT,
		"PopupText" TEXT,
		"Cost" INTEGER NOT NULL,
		"CostProgressionModel" TEXT NOT NULL DEFAULT "NO_PROGRESSION_MODEL",
		"CostProgressionParam1" INTEGER NOT NULL DEFAULT 0,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"PrereqDistrict" TEXT,
		"RequiredBuilding" TEXT,
		"VisualBuildingType" TEXT,
		"SpaceRace" BOOLEAN NOT NULL CHECK (SpaceRace IN (0,1)) DEFAULT 0,
		"OuterDefenseRepair" BOOLEAN NOT NULL CHECK (OuterDefenseRepair IN (0,1)) DEFAULT 0,
		"MaxPlayerInstances" INTEGER,
		"AmenitiesWhileActive" INTEGER,
		"PrereqResource" TEXT,
		"AdvisorType" TEXT,
		"WMD" BOOLEAN NOT NULL CHECK (WMD IN (0,1)) DEFAULT 0,
		"UnlocksFromEffect" BOOLEAN NOT NULL CHECK (UnlocksFromEffect IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ProjectType),
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqDistrict) REFERENCES Districts(DistrictType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (VisualBuildingType) REFERENCES Buildings(BuildingType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqResource) REFERENCES Resources(ResourceType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (ProjectType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (RequiredBuilding) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Project_GreatPersonPoints" (
		"ProjectType" TEXT NOT NULL,
		"GreatPersonClassType" TEXT NOT NULL,
		"Points" INTEGER NOT NULL DEFAULT 0,
		"PointProgressionModel" TEXT NOT NULL DEFAULT "NO_PROGRESSION_MODEL",
		"PointProgressionParam1" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(ProjectType, GreatPersonClassType),
		FOREIGN KEY (ProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (GreatPersonClassType) REFERENCES GreatPersonClasses(GreatPersonClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Projects_MODE" (
		"ProjectType" TEXT NOT NULL,
		"PrereqImprovement" TEXT,
		"ResourceType" TEXT,
		PRIMARY KEY(ProjectType),
		FOREIGN KEY (ProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqImprovement) REFERENCES Improvements(ImprovementType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Project_YieldConversions" (
		"ProjectType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"PercentOfProductionRate" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(ProjectType, YieldType),
		FOREIGN KEY (ProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ProjectCompletionModifiers" (
		"ProjectType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(ProjectType, ModifierId),
		FOREIGN KEY (ProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ProjectPrereqs" (
		"ProjectType" TEXT NOT NULL,
		"PrereqProjectType" TEXT NOT NULL,
		"MinimumPlayerInstances" INTEGER NOT NULL,
		PRIMARY KEY(ProjectType, PrereqProjectType),
		FOREIGN KEY (ProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqProjectType) REFERENCES Projects(ProjectType) ON DELETE CASCADE ON UPDATE CASCADE);

-- Things that are kind of like yields, but can't be placed on plots. Mostly for AI use
CREATE TABLE "PseudoYields" (
		"PseudoYieldType" TEXT NOT NULL,
		"DefaultValue" REAL NOT NULL DEFAULT 1,
		PRIMARY KEY(PseudoYieldType));

CREATE TABLE "Quests" (
		"QuestType" TEXT NOT NULL UNIQUE,
		"Name" TEXT NOT NULL,
		"InstanceName" TEXT,
		"Description" TEXT NOT NULL,
		"InstanceDescription" TEXT,
		"Reward" TEXT NOT NULL,
		"InstanceReward" TEXT,
		"IconString" TEXT NOT NULL,
		PRIMARY KEY(QuestType),
		FOREIGN KEY (QuestType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "RandomAgendas" (
		"AgendaType" TEXT NOT NULL UNIQUE,
		"GameLimit" INTEGER NOT NULL DEFAULT -1,
		PRIMARY KEY(AgendaType),
		FOREIGN KEY (AgendaType) REFERENCES Agendas(AgendaType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Religions" (
		"ReligionType" TEXT NOT NULL UNIQUE,
		"Name" TEXT NOT NULL,
		"IconString" TEXT NOT NULL,
		"Pantheon" BOOLEAN NOT NULL CHECK (Pantheon IN (0,1)) DEFAULT 0,
		"RequiresCustomName" BOOLEAN NOT NULL CHECK (RequiresCustomName IN (0,1)) DEFAULT 0,
		"Color" TEXT NOT NULL,
		PRIMARY KEY(ReligionType),
		FOREIGN KEY (ReligionType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Requirements" (
		"RequirementId" TEXT NOT NULL,
		"RequirementType" TEXT NOT NULL,
		"Likeliness" INTEGER NOT NULL DEFAULT 0,
		"Impact" INTEGER NOT NULL DEFAULT 0,
		"Inverse" BOOLEAN NOT NULL CHECK (Inverse IN (0,1)) DEFAULT 0,
		"Reverse" BOOLEAN NOT NULL CHECK (Reverse IN (0,1)) DEFAULT 0,
		"Persistent" BOOLEAN NOT NULL CHECK (Persistent IN (0,1)) DEFAULT 0,
		"ProgressWeight" INTEGER NOT NULL DEFAULT 1,
		"Triggered" BOOLEAN NOT NULL CHECK (Triggered IN (0,1)) DEFAULT 0,
		PRIMARY KEY(RequirementId));

CREATE TABLE "RequirementArguments" (
		"RequirementId" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Type" TEXT NOT NULL DEFAULT "ARGTYPE_IDENTITY",
		"Value" TEXT NOT NULL,
		"Extra" TEXT,
		"SecondExtra" TEXT,
		PRIMARY KEY(RequirementId, Name),
		FOREIGN KEY (RequirementId) REFERENCES Requirements(RequirementId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "RequirementSetRequirements" (
		"RequirementSetId" TEXT NOT NULL,
		"RequirementId" TEXT NOT NULL,
		PRIMARY KEY(RequirementSetId, RequirementId),
		FOREIGN KEY (RequirementId) REFERENCES Requirements(RequirementId) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (RequirementSetId) REFERENCES RequirementSets(RequirementSetId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "RequirementSets" (
		"RequirementSetId" TEXT NOT NULL,
		"RequirementSetType" TEXT NOT NULL,
		PRIMARY KEY(RequirementSetId));

CREATE TABLE "RequirementStrings" (
		"RequirementId" TEXT NOT NULL,
		"Context" TEXT NOT NULL,
		"Text" TEXT NOT NULL,
		PRIMARY KEY(RequirementId, Context),
		FOREIGN KEY (RequirementId) REFERENCES Requirements(RequirementId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Resources" (
		"ResourceType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"ResourceClassType" TEXT NOT NULL,
		"Happiness" INTEGER NOT NULL DEFAULT 0,
		"NoRiver" BOOLEAN NOT NULL CHECK (NoRiver IN (0,1)) DEFAULT 0,
		"RequiresRiver" BOOLEAN NOT NULL CHECK (RequiresRiver IN (0,1)) DEFAULT 0,
		"Frequency" INTEGER NOT NULL DEFAULT 0,
		"Clumped" BOOLEAN NOT NULL CHECK (Clumped IN (0,1)) DEFAULT 0,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"PeakEra" TEXT NOT NULL DEFAULT "NO_ERA",
		"RevealedEra" INTEGER NOT NULL DEFAULT 1,
		"LakeEligible" BOOLEAN NOT NULL CHECK (LakeEligible IN (0,1)) DEFAULT 1,
		"AdjacentToLand" BOOLEAN NOT NULL CHECK (AdjacentToLand IN (0,1)) DEFAULT 0,
		"SeaFrequency" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(ResourceType),
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Resource_Conditions" (
		"ResourceType" TEXT NOT NULL,
		"UnlocksFromEffect" BOOLEAN NOT NULL CHECK (UnlocksFromEffect IN (0,1)) DEFAULT 0,
		PRIMARY KEY(ResourceType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Resource_Distribution" (
		"Continents" INTEGER NOT NULL,
		"Scarce" INTEGER NOT NULL,
		"Average" INTEGER NOT NULL,
		"Plentiful" INTEGER NOT NULL,
		"PercentAdjusted" INTEGER NOT NULL,
		PRIMARY KEY(Continents));

CREATE TABLE "Resource_Harvests" (
		"ResourceType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"Amount" INTEGER NOT NULL,
		"PrereqTech" TEXT,
		PRIMARY KEY(ResourceType, YieldType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET NULL ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Resource_SeaLuxuries" (
		"MapArgument" INTEGER NOT NULL DEFAULT 1,
		"Duel" INTEGER NOT NULL DEFAULT 0,
		"Tiny" INTEGER DEFAULT 0,
		"Small" INTEGER DEFAULT 0,
		"Standard" INTEGER DEFAULT 0,
		"Large" INTEGER DEFAULT 0,
		"Huge" INTEGER DEFAULT 0,
		PRIMARY KEY(MapArgument));

CREATE TABLE "Resource_SeaStrategics" (
		"MapArgument" INTEGER NOT NULL DEFAULT 1,
		"Duel" INTEGER NOT NULL DEFAULT 0,
		"Tiny" INTEGER DEFAULT 0,
		"Small" INTEGER DEFAULT 0,
		"Standard" INTEGER DEFAULT 0,
		"Large" INTEGER DEFAULT 0,
		"Huge" INTEGER DEFAULT 0,
		PRIMARY KEY(MapArgument));

CREATE TABLE "Resource_TradeRouteYields" (
		"ResourceType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(ResourceType, YieldType),
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Resource_ValidFeatures" (
		"ResourceType" TEXT NOT NULL,
		"FeatureType" TEXT NOT NULL,
		PRIMARY KEY(ResourceType, FeatureType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Resource_ValidTerrains" (
		"ResourceType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(ResourceType, TerrainType),
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Resource_YieldChanges" (
		"ResourceType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(ResourceType, YieldType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ResourceCorporations" (
		"ResourceType" TEXT NOT NULL,
		"ResourceEffect" TEXT,
		"ResourceEffectTExt" TEXT,
		PRIMARY KEY(ResourceType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "ResourceIndustries" (
		"ResourceType" TEXT NOT NULL,
		"ResourceEffect" TEXT,
		"ResourceEffectTExt" TEXT,
		PRIMARY KEY(ResourceType),
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Routes" (
		"RouteType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"MovementCost" REAL NOT NULL,
		"SupportsBridges" BOOLEAN NOT NULL CHECK (SupportsBridges IN (0,1)),
		"PlacementValue" INTEGER NOT NULL UNIQUE,
		"PlacementRequiresRoutePresent" BOOLEAN NOT NULL CHECK (PlacementRequiresRoutePresent IN (0,1)),
		"PlacementRequiresOwnedTile" BOOLEAN NOT NULL CHECK (PlacementRequiresOwnedTile IN (0,1)),
		"PrereqEra" TEXT,
		PRIMARY KEY(RouteType),
		FOREIGN KEY (PrereqEra) REFERENCES Eras(EraType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (RouteType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Route_ValidBuildUnits" (
		"RouteType" TEXT NOT NULL,
		"UnitType" TEXT NOT NULL,
		PRIMARY KEY(RouteType, UnitType),
		FOREIGN KEY (RouteType) REFERENCES Routes(RouteType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "SavingTypes" (
		"SavingType" TEXT NOT NULL,
		PRIMARY KEY(SavingType));

CREATE TABLE "ScenarioSpecificCommand" (
		"TraitName" TEXT NOT NULL DEFAULT "The leader or civ trait this command is hooked up to",
		"CommandName" TEXT NOT NULL,
		"TargetHeuristic" TEXT DEFAULT "The heuristic the AI uses to determine when to use this. Note that it will not, in general, understand its own cooldown if it is done in lua",
		PRIMARY KEY(TraitName, CommandName));

CREATE TABLE "ScoringCategories" (
		"CategoryType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Multiplier" REAL NOT NULL DEFAULT 1,
		PRIMARY KEY(CategoryType));

CREATE TABLE "ScoringLineItems" (
		"LineItemType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Category" TEXT NOT NULL,
		"Multiplier" REAL NOT NULL DEFAULT 1,
		"ScaleByCost" BOOLEAN NOT NULL CHECK (ScaleByCost IN (0,1)) DEFAULT 0,
		"Civics" BOOLEAN NOT NULL CHECK (Civics IN (0,1)) DEFAULT 0,
		"Cities" BOOLEAN NOT NULL CHECK (Cities IN (0,1)) DEFAULT 0,
		"Districts" BOOLEAN NOT NULL CHECK (Districts IN (0,1)) DEFAULT 0,
		"Population" BOOLEAN NOT NULL CHECK (Population IN (0,1)) DEFAULT 0,
		"GreatPeople" BOOLEAN NOT NULL CHECK (GreatPeople IN (0,1)) DEFAULT 0,
		"Techs" BOOLEAN NOT NULL CHECK (Techs IN (0,1)) DEFAULT 0,
		"Wonders" BOOLEAN NOT NULL CHECK (Wonders IN (0,1)) DEFAULT 0,
		"Religion" BOOLEAN NOT NULL CHECK (Religion IN (0,1)) DEFAULT 0,
		"Pillage" BOOLEAN NOT NULL CHECK (Pillage IN (0,1)) DEFAULT 0,
		"Trade" BOOLEAN NOT NULL CHECK (Trade IN (0,1)) DEFAULT 0,
		"GoldPerTurn" BOOLEAN NOT NULL CHECK (GoldPerTurn IN (0,1)) DEFAULT 0,
		"TieBreakerPriority" INTEGER NOT NULL,
		"ScoringScenario1" BOOLEAN NOT NULL CHECK (ScoringScenario1 IN (0,1)) DEFAULT 0,
		"ScoringScenario2" BOOLEAN NOT NULL CHECK (ScoringScenario2 IN (0,1)) DEFAULT 0,
		"ScoringScenario3" BOOLEAN NOT NULL CHECK (ScoringScenario3 IN (0,1)) DEFAULT 0,
		"EraScore" BOOLEAN NOT NULL CHECK (EraScore IN (0,1)) DEFAULT 0,
		"Converted" BOOLEAN NOT NULL CHECK (Converted IN (0,1)) DEFAULT 0,
		"Buildings" BOOLEAN NOT NULL CHECK (Buildings IN (0,1)) DEFAULT 0,
		PRIMARY KEY(LineItemType),
		FOREIGN KEY (Category) REFERENCES ScoringCategories(CategoryType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Seasons" (
		"SeasonType" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		PRIMARY KEY(SeasonType));

CREATE TABLE "SettlementPreferences" (
		"PreferenceType" TEXT,
		PRIMARY KEY(PreferenceType));

CREATE TABLE "ShapeDefinitions" (
		"ShapeName" TEXT NOT NULL UNIQUE,
		"ShapeId" INTEGER NOT NULL UNIQUE,
		"MinChildren" INTEGER NOT NULL DEFAULT 0,
		"MaxChildren" INTEGER NOT NULL DEFAULT 0,
		"Description" TEXT NOT NULL,
		PRIMARY KEY(ShapeId));

CREATE TABLE "StartBiasFeatures" (
		"CivilizationType" TEXT NOT NULL,
		"FeatureType" TEXT NOT NULL,
		"Tier" INTEGER NOT NULL DEFAULT -1,
		PRIMARY KEY(CivilizationType, FeatureType),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (FeatureType) REFERENCES Features(FeatureType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartBiasResources" (
		"CivilizationType" TEXT NOT NULL,
		"ResourceType" TEXT NOT NULL,
		"Tier" INTEGER NOT NULL DEFAULT -1,
		PRIMARY KEY(CivilizationType, ResourceType),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ResourceType) REFERENCES Resources(ResourceType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartBiasRivers" (
		"CivilizationType" TEXT NOT NULL,
		"Tier" INTEGER NOT NULL DEFAULT -1,
		PRIMARY KEY(CivilizationType),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartBiasTerrains" (
		"CivilizationType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		"Tier" INTEGER NOT NULL DEFAULT -1,
		PRIMARY KEY(CivilizationType, TerrainType),
		FOREIGN KEY (CivilizationType) REFERENCES Civilizations(CivilizationType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartEras" (
		"EraType" TEXT NOT NULL,
		"Gold" INTEGER NOT NULL DEFAULT 0,
		"Faith" INTEGER NOT NULL DEFAULT 0,
		"FirstTurnCivicChange" BOOLEAN NOT NULL CHECK (FirstTurnCivicChange IN (0,1)) DEFAULT 0,
		"StartingPopulationCapital" INTEGER NOT NULL DEFAULT 1,
		"StartingPopulationOtherCities" INTEGER NOT NULL DEFAULT 1,
		"GrowthRate" INTEGER NOT NULL DEFAULT 0,
		"ProductionRate" INTEGER NOT NULL DEFAULT 0,
		"DistrictProductionRate" INTEGER NOT NULL DEFAULT 0,
		"StartingMeleeStrengthMajor" INTEGER NOT NULL DEFAULT 0,
		"StartingMeleeStrengthMinor" INTEGER NOT NULL DEFAULT 0,
		"ObsoleteReligion" BOOLEAN NOT NULL CHECK (ObsoleteReligion IN (0,1)) DEFAULT 0,
		"Tiles" INTEGER NOT NULL DEFAULT 0,
		"Year" INTEGER NOT NULL,
		"IgnoreGoodyHutTurn" BOOLEAN NOT NULL CHECK (IgnoreGoodyHutTurn IN (0,1)) DEFAULT 0,
		"StartingRangedStrengthMajor" INTEGER NOT NULL DEFAULT 0,
		"StartingRangedStrengthMinor" INTEGER NOT NULL DEFAULT 0,
		"StartingAmenitiesCapital" INTEGER NOT NULL DEFAULT 0,
		"StartingHousingCapital" INTEGER NOT NULL DEFAULT 0,
		"StartingAmenitiesOtherCities" INTEGER NOT NULL DEFAULT 0,
		"StartingHousingOtherCities" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(EraType),
		FOREIGN KEY (EraType) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartingBoostedCivics" (
		"Civic" TEXT NOT NULL DEFAULT "NO_CIVIC",
		"Era" TEXT NOT NULL,
		PRIMARY KEY(Civic, Era),
		FOREIGN KEY (Era) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Civic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartingBoostedTechnologies" (
		"Technology" TEXT NOT NULL DEFAULT "NO_TECHNOLOGY",
		"Era" TEXT NOT NULL,
		PRIMARY KEY(Technology, Era),
		FOREIGN KEY (Era) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Technology) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartingBuildings" (
		"Building" TEXT NOT NULL,
		"Era" TEXT NOT NULL,
		"District" TEXT,
		"MinorOnly" BOOLEAN NOT NULL CHECK (MinorOnly IN (0,1)) DEFAULT 0,
		"MinDifficulty" TEXT,
		PRIMARY KEY(Building, Era, District, MinDifficulty),
		FOREIGN KEY (Era) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Building) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (District) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (MinDifficulty) REFERENCES Difficulties(DifficultyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartingCivics" (
		"Civic" TEXT NOT NULL DEFAULT "NO_CIVIC",
		"Era" TEXT NOT NULL,
		PRIMARY KEY(Civic, Era),
		FOREIGN KEY (Era) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Civic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "StartingGovernments" (
		"Government" TEXT NOT NULL DEFAULT "NO_GOVERNMENT",
		"Era" TEXT NOT NULL,
		"Change" BOOLEAN NOT NULL CHECK (Change IN (0,1)) DEFAULT 0,
		PRIMARY KEY(Government, Era),
		FOREIGN KEY (Era) REFERENCES Eras(EraType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Government) REFERENCES Governments(GovernmentType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Strategies" (
		"StrategyType" TEXT NOT NULL,
		"VictoryType" TEXT,
		"NumConditionsNeeded" INTEGER NOT NULL DEFAULT 1,
		PRIMARY KEY(StrategyType),
		FOREIGN KEY (VictoryType) REFERENCES Victories(VictoryType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Strategy_Priorities" (
		"StrategyType" TEXT NOT NULL,
		"ListType" TEXT NOT NULL,
		PRIMARY KEY(StrategyType, ListType),
		FOREIGN KEY (StrategyType) REFERENCES Strategies(StrategyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ListType) REFERENCES AiListTypes(ListType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Strategy_YieldPriorities" (
		"StrategyType" TEXT,
		"YieldType" TEXT,
		"PseudoYieldType" TEXT,
		"PercentageDelta" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(StrategyType, YieldType, PseudoYieldType),
		FOREIGN KEY (StrategyType) REFERENCES Strategies(StrategyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PseudoYieldType) REFERENCES PseudoYields(PseudoYieldType) ON DELETE CASCADE ON UPDATE CASCADE);

-- These are conditions the AI must satisfy to TRY to achieve this victory
CREATE TABLE "StrategyConditions" (
		"StrategyType" TEXT,
		"ConditionFunction" TEXT,
		"StringValue" TEXT,
		"ThresholdValue" INTEGER NOT NULL DEFAULT 0,
		"Forbidden" BOOLEAN NOT NULL CHECK (Forbidden IN (0,1)) DEFAULT 0,
		"Disqualifier" BOOLEAN NOT NULL CHECK (Disqualifier IN (0,1)) DEFAULT 0,
		"Exclusive" BOOLEAN NOT NULL CHECK (Exclusive IN (0,1)) DEFAULT 0,
		PRIMARY KEY(StrategyType, ConditionFunction, Exclusive),
		FOREIGN KEY (StrategyType) REFERENCES Strategies(StrategyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Tags" (
		"Tag" TEXT NOT NULL,
		"Vocabulary" TEXT NOT NULL,
		PRIMARY KEY(Tag),
		FOREIGN KEY (Vocabulary) REFERENCES Vocabularies(Vocabulary) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TargetTypes" (
		"TargetType" TEXT NOT NULL,
		PRIMARY KEY(TargetType));

CREATE TABLE "Technologies" (
		"TechnologyType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Cost" INTEGER NOT NULL,
		"Repeatable" BOOLEAN NOT NULL CHECK (Repeatable IN (0,1)) DEFAULT 0,
		"EmbarkUnitType" TEXT,
		"EmbarkAll" BOOLEAN NOT NULL CHECK (EmbarkAll IN (0,1)) DEFAULT 0,
		"Description" TEXT,
		"EraType" TEXT NOT NULL,
		"Critical" BOOLEAN NOT NULL CHECK (Critical IN (0,1)) DEFAULT 0,
		"BarbarianFree" BOOLEAN NOT NULL CHECK (BarbarianFree IN (0,1)) DEFAULT 0,
		"UITreeRow" INTEGER DEFAULT 0,
		"AdvisorType" TEXT,
		PRIMARY KEY(TechnologyType),
		FOREIGN KEY (EraType) REFERENCES Eras(EraType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (EmbarkUnitType) REFERENCES Units(UnitType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (TechnologyType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Technologies_XP2" (
		"TechnologyType" TEXT NOT NULL,
		"RandomPrereqs" BOOLEAN NOT NULL CHECK (RandomPrereqs IN (0,1)) DEFAULT 0,
		"HiddenUntilPrereqComplete" BOOLEAN NOT NULL CHECK (HiddenUntilPrereqComplete IN (0,1)) DEFAULT 0,
		PRIMARY KEY(TechnologyType),
		FOREIGN KEY (TechnologyType) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TechnologyModifiers" (
		"TechnologyType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(TechnologyType, ModifierId),
		FOREIGN KEY (TechnologyType) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TechnologyPrereqs" (
		"Technology" TEXT NOT NULL,
		"PrereqTech" TEXT NOT NULL,
		PRIMARY KEY(Technology, PrereqTech),
		FOREIGN KEY (Technology) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TechnologyQuotes" (
		"TechnologyType" TEXT NOT NULL,
		"Quote" TEXT NOT NULL,
		"QuoteAudio" TEXT,
		PRIMARY KEY(TechnologyType, Quote),
		FOREIGN KEY (TechnologyType) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TechnologyRandomCosts" (
		"TechnologyType" TEXT NOT NULL,
		"Cost" INTEGER NOT NULL,
		PRIMARY KEY(TechnologyType, Cost),
		FOREIGN KEY (TechnologyType) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Terrains" (
		"TerrainType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Mountain" BOOLEAN NOT NULL CHECK (Mountain IN (0,1)) DEFAULT 0,
		"Hills" BOOLEAN NOT NULL CHECK (Hills IN (0,1)) DEFAULT 0,
		"Water" BOOLEAN NOT NULL CHECK (Water IN (0,1)) DEFAULT 0,
		"InfluenceCost" INTEGER NOT NULL,
		"MovementCost" INTEGER NOT NULL,
		"ShallowWater" BOOLEAN NOT NULL CHECK (ShallowWater IN (0,1)) DEFAULT 0,
		"SightModifier" INTEGER NOT NULL DEFAULT 0,
		"SightThroughModifier" INTEGER NOT NULL DEFAULT 0,
		"Impassable" BOOLEAN NOT NULL CHECK (Impassable IN (0,1)) DEFAULT 0,
		"DefenseModifier" INTEGER NOT NULL DEFAULT 0,
		"Appeal" INTEGER NOT NULL DEFAULT 0,
		"AntiquityPriority" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(TerrainType));

CREATE TABLE "Terrain_YieldChanges" (
		"TerrainType" TEXT NOT NULL,
		"YieldType" TEXT NOT NULL,
		"YieldChange" INTEGER NOT NULL,
		PRIMARY KEY(TerrainType, YieldType),
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (YieldType) REFERENCES Yields(YieldType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TerrainClasses" (
		"TerrainClassType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		PRIMARY KEY(TerrainClassType));

CREATE TABLE "TerrainClass_Terrains" (
		"TerrainClassType" TEXT NOT NULL,
		"TerrainType" TEXT NOT NULL,
		PRIMARY KEY(TerrainClassType, TerrainType),
		FOREIGN KEY (TerrainType) REFERENCES Terrains(TerrainType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TerrainClassType) REFERENCES TerrainClasses(TerrainClassType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Traits" (
		"TraitType" TEXT NOT NULL,
		"Name" LocalizedText,
		"Description" LocalizedText,
		"InternalOnly" BOOLEAN NOT NULL CHECK (InternalOnly IN (0,1)) DEFAULT 0,
		PRIMARY KEY(TraitType),
		FOREIGN KEY (TraitType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TraitModifiers" (
		"TraitType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(TraitType, ModifierId),
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TreeData" (
		"DefnId" INTEGER NOT NULL,
		"NodeId" INTEGER NOT NULL,
		"TreeName" TEXT NOT NULL,
		"Tag" TEXT,
		"DefaultData" TEXT,
		"ParentTag" TEXT,
		"UniqueId" INTEGER NOT NULL,
		PRIMARY KEY(UniqueId),
		FOREIGN KEY (TreeName) REFERENCES BehaviorTrees(TreeName) ON DELETE CASCADE ON UPDATE CASCADE);

-- A list of behavior trees (or operations) that can be triggered by specific AI Events
CREATE TABLE "TriggeredBehaviorTrees" (
		"TriggerType" TEXT NOT NULL,
		"TreeName" TEXT NOT NULL,
		"OperationName" TEXT,
		"AIEvent" TEXT NOT NULL,
		"Priority" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(TriggerType),
		FOREIGN KEY (TreeName) REFERENCES BehaviorTrees(TreeName) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AIEvent) REFERENCES AiEvents(EventType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TurnPhases" (
		"ID" INTEGER,
		"TurnPhaseType" TEXT NOT NULL,
		"PhaseOrder" INTEGER NOT NULL,
		"TurnMode" TEXT NOT NULL,
		"ActiveSegmentType" TEXT NOT NULL,
		"InactiveSegmentType" TEXT,
		PRIMARY KEY(ID),
		FOREIGN KEY (ActiveSegmentType) REFERENCES TurnSegments(TurnSegmentType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (InactiveSegmentType) REFERENCES TurnSegments(TurnSegmentType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TurnSegments" (
		"TurnSegmentType" TEXT NOT NULL,
		"Name" TEXT,
		"Sound" TEXT,
		"AllowStrategicCommands" BOOLEAN NOT NULL CHECK (AllowStrategicCommands IN (0,1)) DEFAULT 0,
		"AllowTacticalCommands" BOOLEAN NOT NULL CHECK (AllowTacticalCommands IN (0,1)) DEFAULT 0,
		"TimeLimit_Base" INTEGER NOT NULL DEFAULT 0,
		"TimeLimit_PerCity" INTEGER NOT NULL DEFAULT 0,
		"TimeLimit_PerUnit" INTEGER NOT NULL DEFAULT 0,
		"AllowTurnUnready" BOOLEAN NOT NULL CHECK (AllowTurnUnready IN (0,1)) DEFAULT 1,
		PRIMARY KEY(TurnSegmentType));

CREATE TABLE "TurnTimers" (
		"TurnTimerType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		PRIMARY KEY(TurnTimerType));

CREATE TABLE "Types" (
		"Type" TEXT NOT NULL,
		"Hash" INTEGER NOT NULL UNIQUE DEFAULT 0,
		"Kind" TEXT NOT NULL,
		PRIMARY KEY(Type),
		FOREIGN KEY (Kind) REFERENCES Kinds(Kind) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TypeProperties" (
		"Type" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Value" TEXT NOT NULL,
		"PropertyType" TEXT NOT NULL DEFAULT "PROPERTYTYPE_IDENTITY",
		PRIMARY KEY(Type, Name),
		FOREIGN KEY (Type) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "TypeTags" (
		"Type" TEXT NOT NULL,
		"Tag" TEXT NOT NULL,
		PRIMARY KEY(Type, Tag),
		FOREIGN KEY (Type) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Tag) REFERENCES Tags(Tag) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Units" (
		"UnitType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"BaseSightRange" INTEGER NOT NULL,
		"BaseMoves" INTEGER NOT NULL,
		"Combat" INTEGER NOT NULL DEFAULT 0,
		"RangedCombat" INTEGER NOT NULL DEFAULT 0,
		"Range" INTEGER NOT NULL DEFAULT 0,
		"Bombard" INTEGER NOT NULL DEFAULT 0,
		"Domain" TEXT NOT NULL,
		"FormationClass" TEXT NOT NULL,
		"Cost" INTEGER NOT NULL,
		"PopulationCost" INTEGER,
		"FoundCity" BOOLEAN NOT NULL CHECK (FoundCity IN (0,1)) DEFAULT 0,
		"FoundReligion" BOOLEAN NOT NULL CHECK (FoundReligion IN (0,1)) DEFAULT 0,
		"MakeTradeRoute" BOOLEAN NOT NULL CHECK (MakeTradeRoute IN (0,1)) DEFAULT 0,
		"EvangelizeBelief" BOOLEAN NOT NULL CHECK (EvangelizeBelief IN (0,1)) DEFAULT 0,
		"LaunchInquisition" BOOLEAN NOT NULL CHECK (LaunchInquisition IN (0,1)) DEFAULT 0,
		"RequiresInquisition" BOOLEAN NOT NULL CHECK (RequiresInquisition IN (0,1)) DEFAULT 0,
		"BuildCharges" INTEGER NOT NULL DEFAULT 0,
		"ReligiousStrength" INTEGER NOT NULL DEFAULT 0,
		"ReligionEvictPercent" INTEGER NOT NULL DEFAULT 0,
		"SpreadCharges" INTEGER NOT NULL DEFAULT 0,
		"ReligiousHealCharges" INTEGER NOT NULL DEFAULT 0,
		"ExtractsArtifacts" BOOLEAN NOT NULL CHECK (ExtractsArtifacts IN (0,1)) DEFAULT 0,
		"Description" TEXT,
		"Flavor" TEXT,
		"CanCapture" BOOLEAN NOT NULL CHECK (CanCapture IN (0,1)) DEFAULT 1,
		"CanRetreatWhenCaptured" BOOLEAN NOT NULL CHECK (CanRetreatWhenCaptured IN (0,1)) DEFAULT 0,
		"TraitType" TEXT,
		"AllowBarbarians" BOOLEAN NOT NULL CHECK (AllowBarbarians IN (0,1)) DEFAULT 0,
		"CostProgressionModel" TEXT NOT NULL DEFAULT "NO_COST_PROGRESSION",
		"CostProgressionParam1" INTEGER NOT NULL DEFAULT 0,
		"PromotionClass" TEXT,
		"InitialLevel" INTEGER NOT NULL DEFAULT 1,
		"NumRandomChoices" INTEGER NOT NULL DEFAULT 0,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"PrereqDistrict" TEXT,
		"PrereqPopulation" INTEGER,
		"LeaderType" TEXT,
		"CanTrain" BOOLEAN NOT NULL CHECK (CanTrain IN (0,1)) DEFAULT 1,
		"StrategicResource" TEXT,
		"PurchaseYield" TEXT,
		"MustPurchase" BOOLEAN NOT NULL CHECK (MustPurchase IN (0,1)) DEFAULT 0,
		"Maintenance" INTEGER NOT NULL DEFAULT 0,
		"Stackable" BOOLEAN NOT NULL CHECK (Stackable IN (0,1)) DEFAULT 0,
		"AirSlots" INTEGER NOT NULL DEFAULT 0,
		"CanTargetAir" BOOLEAN NOT NULL CHECK (CanTargetAir IN (0,1)) DEFAULT 0,
		"PseudoYieldType" TEXT,
		"ZoneOfControl" BOOLEAN NOT NULL CHECK (ZoneOfControl IN (0,1)) DEFAULT 0,
		"AntiAirCombat" INTEGER NOT NULL DEFAULT 0,
		"Spy" BOOLEAN NOT NULL CHECK (Spy IN (0,1)) DEFAULT 0,
		"WMDCapable" BOOLEAN NOT NULL CHECK (WMDCapable IN (0,1)) DEFAULT 0,
		"ParkCharges" INTEGER NOT NULL DEFAULT 0,
		"IgnoreMoves" BOOLEAN NOT NULL CHECK (IgnoreMoves IN (0,1)) DEFAULT 0,
		"TeamVisibility" BOOLEAN NOT NULL CHECK (TeamVisibility IN (0,1)) DEFAULT 0,
		"ObsoleteTech" TEXT,
		"ObsoleteCivic" TEXT,
		"MandatoryObsoleteTech" TEXT,
		"MandatoryObsoleteCivic" TEXT,
		"AdvisorType" TEXT,
		"EnabledByReligion" BOOLEAN NOT NULL CHECK (EnabledByReligion IN (0,1)) DEFAULT 0,
		"TrackReligion" BOOLEAN NOT NULL CHECK (TrackReligion IN (0,1)) DEFAULT 0,
		"DisasterCharges" INTEGER NOT NULL DEFAULT 0,
		"UseMaxMeleeTrainedStrength" BOOLEAN NOT NULL CHECK (UseMaxMeleeTrainedStrength IN (0,1)) DEFAULT 0,
		"ImmediatelyName" BOOLEAN NOT NULL CHECK (ImmediatelyName IN (0,1)) DEFAULT 0,
		"CanEarnExperience" BOOLEAN NOT NULL CHECK (CanEarnExperience IN (0,1)) DEFAULT 1,
		PRIMARY KEY(UnitType),
		FOREIGN KEY (Flavor) REFERENCES Flavors(FlavorType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (TraitType) REFERENCES Traits(TraitType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (StrategicResource) REFERENCES Resources(ResourceType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PurchaseYield) REFERENCES Yields(YieldType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqDistrict) REFERENCES Districts(DistrictType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PromotionClass) REFERENCES UnitPromotionClasses(PromotionClassType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PseudoYieldType) REFERENCES PseudoYields(PseudoYieldType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (UnitType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PurchaseYield) REFERENCES Yields(YieldType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (ObsoleteCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (MandatoryObsoleteCivic) REFERENCES Civics(CivicType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (MandatoryObsoleteTech) REFERENCES Technologies(TechnologyType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT,
		FOREIGN KEY (ObsoleteTech) REFERENCES Technologies(TechnologyType) ON DELETE SET DEFAULT ON UPDATE SET DEFAULT);

CREATE TABLE "Unit_BuildingPrereqs" (
		"Unit" TEXT NOT NULL,
		"PrereqBuilding" TEXT NOT NULL,
		"NumSupported" INTEGER NOT NULL DEFAULT -1,
		PRIMARY KEY(Unit, PrereqBuilding),
		FOREIGN KEY (Unit) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqBuilding) REFERENCES Buildings(BuildingType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Units_MODE" (
		"UnitType" TEXT NOT NULL,
		"ActionCharges" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(UnitType),
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Unit_RebellionTags" (
		"Tag" TEXT NOT NULL,
		"RebellionLevel" INTEGER NOT NULL,
		"NumCreated" INTEGER NOT NULL DEFAULT 1,
		"ForbiddenTag" TEXT,
		PRIMARY KEY(Tag, RebellionLevel));

CREATE TABLE "UnitAbilities" (
		"UnitAbilityType" TEXT NOT NULL,
		"Name" LocalizedText,
		"Description" LocalizedText,
		"Inactive" BOOLEAN NOT NULL CHECK (Inactive IN (0,1)) DEFAULT 0,
		"ShowFloatTextWhenEarned" BOOLEAN NOT NULL CHECK (ShowFloatTextWhenEarned IN (0,1)) DEFAULT 0,
		"Permanent" BOOLEAN NOT NULL CHECK (Permanent IN (0,1)) DEFAULT 1,
		PRIMARY KEY(UnitAbilityType));

CREATE TABLE "UnitAbilityModifiers" (
		"UnitAbilityType" TEXT NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(UnitAbilityType, ModifierId),
		FOREIGN KEY (UnitAbilityType) REFERENCES UnitAbilities(UnitAbilityType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitAiInfos" (
		"UnitType" TEXT NOT NULL,
		"AiType" TEXT NOT NULL,
		PRIMARY KEY(UnitType, AiType),
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (AiType) REFERENCES UnitAiTypes(AiType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitAiTypes" (
		"AiType" TEXT NOT NULL,
		"TypeValue" INTEGER,
		"Priority" BOOLEAN CHECK (Priority IN (0,1)) DEFAULT 0,
		PRIMARY KEY(AiType));

CREATE TABLE "UnitCaptures" (
		"CapturedUnitType" TEXT NOT NULL,
		"BecomesUnitType" TEXT NOT NULL,
		PRIMARY KEY(CapturedUnitType, BecomesUnitType),
		FOREIGN KEY (CapturedUnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (BecomesUnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitCommands" (
		"CommandType" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"Help" TEXT,
		"DisabledHelp" TEXT,
		"Icon" TEXT NOT NULL,
		"Sound" TEXT,
		"VisibleInUI" BOOLEAN NOT NULL CHECK (VisibleInUI IN (0,1)),
		"HoldCycling" BOOLEAN NOT NULL CHECK (HoldCycling IN (0,1)) DEFAULT 0,
		"CategoryInUI" TEXT,
		"InterfaceMode" TEXT,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"MaxEra" INTEGER NOT NULL DEFAULT -1,
		"HotkeyId" TEXT,
		PRIMARY KEY(CommandType),
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitFormationClasses" (
		"FormationClassType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		PRIMARY KEY(FormationClassType));

CREATE TABLE "UnitNames" (
		"ID" INTEGER NOT NULL,
		"NameType" TEXT NOT NULL,
		"TextKey" TEXT NOT NULL,
		PRIMARY KEY(ID));

CREATE TABLE "UnitOperations" (
		"OperationType" TEXT NOT NULL,
		"Description" TEXT NOT NULL,
		"Help" TEXT,
		"DisabledHelp" TEXT,
		"Icon" TEXT NOT NULL,
		"Sound" TEXT,
		"VisibleInUI" BOOLEAN NOT NULL CHECK (VisibleInUI IN (0,1)),
		"HoldCycling" BOOLEAN NOT NULL CHECK (HoldCycling IN (0,1)) DEFAULT 0,
		"CategoryInUI" TEXT,
		"InterfaceMode" TEXT,
		"PrereqTech" TEXT,
		"PrereqCivic" TEXT,
		"Turns" INTEGER NOT NULL DEFAULT 0,
		"BaseProbability" INTEGER NOT NULL DEFAULT 0,
		"LevelProbChange" INTEGER NOT NULL DEFAULT 0,
		"EnemyProbChange" INTEGER NOT NULL DEFAULT 0,
		"EnemyLevelProbChange" INTEGER NOT NULL DEFAULT 0,
		"TargetDistrict" TEXT,
		"HotkeyId" TEXT,
		"Offensive" BOOLEAN NOT NULL CHECK (Offensive IN (0,1)) DEFAULT 0,
		PRIMARY KEY(OperationType),
		FOREIGN KEY (PrereqTech) REFERENCES Technologies(TechnologyType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (PrereqCivic) REFERENCES Civics(CivicType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (TargetDistrict) REFERENCES Districts(DistrictType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitPromotions" (
		"UnitPromotionType" TEXT NOT NULL,
		"Name" LocalizedText NOT NULL,
		"Description" LocalizedText NOT NULL,
		"Level" INTEGER NOT NULL,
		"Specialization" TEXT,
		"PromotionClass" TEXT,
		"Column" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(UnitPromotionType),
		FOREIGN KEY (PromotionClass) REFERENCES UnitPromotionClasses(PromotionClassType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (UnitPromotionType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitPromotionClasses" (
		"PromotionClassType" TEXT NOT NULL,
		"Name" LocalizedText NOT NULL,
		PRIMARY KEY(PromotionClassType),
		FOREIGN KEY (PromotionClassType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitPromotionModifiers" (
		"UnitPromotionType" INTEGER NOT NULL,
		"ModifierId" TEXT NOT NULL,
		PRIMARY KEY(UnitPromotionType, ModifierId),
		FOREIGN KEY (UnitPromotionType) REFERENCES UnitPromotions(UnitPromotionType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitPromotionPrereqs" (
		"UnitPromotion" TEXT NOT NULL,
		"PrereqUnitPromotion" TEXT NOT NULL,
		PRIMARY KEY(UnitPromotion, PrereqUnitPromotion),
		FOREIGN KEY (PrereqUnitPromotion) REFERENCES UnitPromotions(UnitPromotionType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (UnitPromotion) REFERENCES UnitPromotions(UnitPromotionType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitReplaces" (
		"CivUniqueUnitType" TEXT NOT NULL,
		"ReplacesUnitType" TEXT NOT NULL,
		PRIMARY KEY(CivUniqueUnitType),
		FOREIGN KEY (ReplacesUnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (CivUniqueUnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Units_Presentation" (
		"UnitType" TEXT NOT NULL,
		"UIFlagOffset" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(UnitType),
		FOREIGN KEY (UnitType) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "UnitUpgrades" (
		"Unit" TEXT NOT NULL UNIQUE,
		"UpgradeUnit" TEXT NOT NULL,
		PRIMARY KEY(Unit),
		FOREIGN KEY (UpgradeUnit) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE,
		FOREIGN KEY (Unit) REFERENCES Units(UnitType) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Victories" (
		"VictoryType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"Blurb" TEXT NOT NULL,
		"RequirementSetId" TEXT NOT NULL,
		"EnabledByDefault" BOOLEAN NOT NULL CHECK (EnabledByDefault IN (0,1)) DEFAULT 1,
		"Description" TEXT,
		"Icon" TEXT,
		"OneMoreTurn" BOOLEAN CHECK (OneMoreTurn IN (0,1)) DEFAULT 1,
		"CriticalPercentage" INTEGER NOT NULL DEFAULT 90,
		"RequiresMultipleTeams" BOOLEAN NOT NULL CHECK (RequiresMultipleTeams IN (0,1)) DEFAULT 0,
		PRIMARY KEY(VictoryType),
		FOREIGN KEY (VictoryType) REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE);

CREATE TABLE "Visibilities" (
		"VisibilityType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"RevealAgendas" BOOLEAN NOT NULL CHECK (RevealAgendas IN (0,1)) DEFAULT 0,
		PRIMARY KEY(VisibilityType));

CREATE TABLE "Vocabularies" (
		"Vocabulary" TEXT NOT NULL,
		PRIMARY KEY(Vocabulary));

-- Types of wars
CREATE TABLE "Wars" (
		"WarType" TEXT NOT NULL,
		"Name" TEXT,
		"Description" TEXT,
		PRIMARY KEY(WarType));

CREATE TABLE "WMDs" (
		"WeaponType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"BlastRadius" INTEGER NOT NULL DEFAULT 1,
		"FalloutDuration" INTEGER NOT NULL DEFAULT 0,
		"AffectPopulation" BOOLEAN NOT NULL CHECK (AffectPopulation IN (0,1)) DEFAULT 0,
		"AffectImprovements" BOOLEAN NOT NULL CHECK (AffectImprovements IN (0,1)) DEFAULT 0,
		"AffectBuildings" BOOLEAN NOT NULL CHECK (AffectBuildings IN (0,1)) DEFAULT 0,
		"AffectUnits" BOOLEAN NOT NULL CHECK (AffectUnits IN (0,1)) DEFAULT 0,
		"AffectResources" BOOLEAN NOT NULL CHECK (AffectResources IN (0,1)) DEFAULT 0,
		"AffectRoutes" BOOLEAN NOT NULL CHECK (AffectRoutes IN (0,1)) DEFAULT 0,
		"ICBMStrikeRange" INTEGER NOT NULL DEFAULT 0,
		"Maintenance" INTEGER NOT NULL DEFAULT 0,
		PRIMARY KEY(WeaponType));

CREATE TABLE "Yields" (
		"YieldType" TEXT NOT NULL,
		"Name" TEXT NOT NULL,
		"IconString" TEXT NOT NULL,
		"OccupiedCityChange" REAL NOT NULL DEFAULT 0,
		"DefaultValue" REAL NOT NULL DEFAULT 1,
		PRIMARY KEY(YieldType));


-- Navigation Properties (if any)
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join Adjacency_YieldChanges as T2 on T2.AdjacentDistrict = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "FeatureReference", "Features", 0,"SELECT T1.rowid from Features as T1 inner join Adjacency_YieldChanges as T2 on T2.AdjacentFeature = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Adjacency_YieldChanges as T2 on T2.AdjacentImprovement = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "ObsoleteCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Adjacency_YieldChanges as T2 on T2.ObsoleteCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "ObsoleteTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Adjacency_YieldChanges as T2 on T2.ObsoleteTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Adjacency_YieldChanges as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Adjacency_YieldChanges as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "TerrainReference", "Terrains", 0,"SELECT T1.rowid from Terrains as T1 inner join Adjacency_YieldChanges as T2 on T2.AdjacentTerrain = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacency_YieldChanges", "YieldTypeReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Adjacency_YieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Adjacent_AppealYieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Adjacent_AppealYieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Agendas", "FirstExclusions", "Agendas", 1,"SELECT T1.rowid from Agendas as T1 inner join ExclusiveAgendas as T2 on T2.AgendaTwo = T1.AgendaType inner join Agendas as T3 on T3.AgendaType = T2.AgendaOne where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Agendas", "RandomAgendaCollection", "RandomAgendas", 1,"SELECT T1.rowid from RandomAgendas as T1 inner join Agendas as T2 on T2.AgendaType = T1.AgendaType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Agendas", "SecondExclusions", "Agendas", 1,"SELECT T1.rowid from Agendas as T1 inner join ExclusiveAgendas as T2 on T2.AgendaOne = T1.AgendaType inner join Agendas as T3 on T3.AgendaType = T2.AgendaTwo where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Agendas", "TraitCollection", "Traits", 1,"SELECT T1.rowid from Traits as T1 inner join AgendaTraits as T2 on T2.TraitType = T1.TraitType inner join Agendas as T3 on T3.AgendaType = T2.AgendaType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AgendaPreferredLeaders", "LeaderReference", "Leaders", 0,"SELECT T1.rowid from Leaders as T1 inner join AgendaPreferredLeaders as T2 on T2.LeaderType = T1.LeaderType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AgendaPreferredLeaders", "RandomAgendaReference", "RandomAgendas", 0,"SELECT T1.rowid from RandomAgendas as T1 inner join AgendaPreferredLeaders as T2 on T2.AgendaType = T1.AgendaType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AiBuildSpecializations", "PriorityReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join AiBuildSpecializations as T2 on T2.PrioritizationYield = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AiBuildSpecializations", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join AiBuildSpecializations as T2 on T2.BuildingYield = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AiFavoredItems", "MaxDifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join AiFavoredItems as T2 on T2.MaxDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AiFavoredItems", "MinDifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join AiFavoredItems as T2 on T2.MinDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AiLists", "MaxDifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join AiLists as T2 on T2.MaxDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("AiLists", "MinDifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join AiLists as T2 on T2.MinDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianAttackForces", "MaxDifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join BarbarianAttackForces as T2 on T2.MaxTargetDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianAttackForces", "MinDifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join BarbarianAttackForces as T2 on T2.MinTargetDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianTribes", "AttackCollection", "BarbarianAttackForces", 1,"SELECT T1.rowid from BarbarianAttackForces as T1 inner join BarbarianTribeForces as T2 on T2.AttackForceType = T1.AttackForceType inner join BarbarianTribes as T3 on T3.TribeType = T2.TribeType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianTribes", "RequiredResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join BarbarianTribes as T2 on T2.RequiredResource = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianTribes", "TribeNames", "BarbarianTribeNames", 1,"SELECT T1.rowid from BarbarianTribeNames as T1 inner join BarbarianTribes as T2 on T2.TribeType = T1.TribeType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianTribe_MapConditions", "MapConditionSetTypeReference", "BarbarianTribe_MapConditionSets", 0,"SELECT T1.rowid from BarbarianTribe_MapConditionSets as T1 inner join BarbarianTribe_MapConditions as T2 on T2.MapConditionSetType = T1.MapConditionSetType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianTribe_MapConditionSets", "TribeTypeReference", "BarbarianTribes", 0,"SELECT T1.rowid from BarbarianTribes as T1 inner join BarbarianTribe_MapConditionSets as T2 on T2.TribeType = T1.TribeType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianTribeNames", "AttackCollection", "BarbarianAttackForces", 1,"SELECT T1.rowid from BarbarianAttackForces as T1 inner join BarbarianTribeForces as T2 on T2.AttackForceType = T1.AttackForceType inner join BarbarianTribeNames as T3 on T3.TribeNameType = T2.SpecificTribeType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BarbarianTribeNames", "TribeTypeReference", "BarbarianTribes", 0,"SELECT T1.rowid from BarbarianTribes as T1 inner join BarbarianTribeNames as T2 on T2.TribeType = T1.TribeType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BehaviorTrees", "TriggerCollection", "TriggeredBehaviorTrees", 1,"SELECT T1.rowid from TriggeredBehaviorTrees as T1 inner join BehaviorTrees as T2 on T2.TreeName = T1.TreeName where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Beliefs", "BeliefClassTypeReference", "BeliefClasses", 0,"SELECT T1.rowid from BeliefClasses as T1 inner join Beliefs as T2 on T2.BeliefClassType = T1.BeliefClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BonusMinorStartingUnits", "DifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join BonusMinorStartingUnits as T2 on T2.MinDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BonusMinorStartingUnits", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join BonusMinorStartingUnits as T2 on T2.Era = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BonusMinorStartingUnits", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join BonusMinorStartingUnits as T2 on T2.Unit = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "BoostingCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Boosts as T2 on T2.BoostingCivicType = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "BoostingTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Boosts as T2 on T2.BoostingTechType = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "BoostReference", "BoostNames", 0,"SELECT T1.rowid from BoostNames as T1 inner join Boosts as T2 on T2.BoostClass = T1.BoostType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "BuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join Boosts as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "CivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Boosts as T2 on T2.CivicType = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join Boosts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "GovernmentTierReference", "GovernmentTiers", 0,"SELECT T1.rowid from GovernmentTiers as T1 inner join Boosts as T2 on T2.GovernmentTierType = T1.TierType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Boosts as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "ResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join Boosts as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "TechnologyReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Boosts as T2 on T2.TechnologyType = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "Unit1Reference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join Boosts as T2 on T2.Unit1Type = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Boosts", "Unit2Reference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join Boosts as T2 on T2.Unit2Type = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BoostHandlers", "BoostTypeReference", "BoostNames", 0,"SELECT T1.rowid from BoostNames as T1 inner join BoostHandlers as T2 on T2.TechBoostType = T1.BoostType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "AdjacentDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join Buildings as T2 on T2.AdjacentDistrict = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "AdjacentImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Buildings as T2 on T2.AdjacentImprovement = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "AdjacentResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join Buildings as T2 on T2.AdjacentResource = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "CitizenYieldChangesReference", "Building_CitizenYieldChanges", 1,"SELECT T1.rowid from Building_CitizenYieldChanges as T1 inner join Buildings as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "CityAdjacentTerrainReference", "Terrains", 0,"SELECT T1.rowid from Terrains as T1 inner join Buildings as T2 on T2.CityAdjacentTerrain = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "DependentBuildingCollection", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join BuildingPrereqs as T2 on T2.Building = T1.BuildingType inner join Buildings as T3 on T3.BuildingType = T2.PrereqBuilding where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "GreatPersonPointsReference", "Building_GreatPersonPoints", 1,"SELECT T1.rowid from Building_GreatPersonPoints as T1 inner join Buildings as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "GreatWorkCollection", "Building_GreatWorks", 1,"SELECT T1.rowid from Building_GreatWorks as T1 inner join Buildings as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "MutuallyExclusiveBuildingReference", "MutuallyExclusiveBuildings", 1,"SELECT T1.rowid from MutuallyExclusiveBuildings as T1 inner join Buildings as T2 on T2.BuildingType = T1.Building where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "PrereqBuildingCollection", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join BuildingPrereqs as T2 on T2.PrereqBuilding = T1.BuildingType inner join Buildings as T3 on T3.BuildingType = T2.Building where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Buildings as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "PrereqDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join Buildings as T2 on T2.PrereqDistrict = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Buildings as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "PurchaseYieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Buildings as T2 on T2.PurchaseYield = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "ReplacedByCollection", "BuildingReplaces", 1,"SELECT T1.rowid from BuildingReplaces as T1 inner join Buildings as T2 on T2.BuildingType = T1.ReplacesBuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "ReplacesCollection", "BuildingReplaces", 1,"SELECT T1.rowid from BuildingReplaces as T1 inner join Buildings as T2 on T2.BuildingType = T1.CivUniqueBuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "RequiredFeatures", "Features", 1,"SELECT T1.rowid from Features as T1 inner join Building_RequiredFeatures as T2 on T2.FeatureType = T1.FeatureType inner join Buildings as T3 on T3.BuildingType = T2.BuildingType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "StartingBuildingCollection", "StartingBuildings", 1,"SELECT T1.rowid from StartingBuildings as T1 inner join Buildings as T2 on T2.BuildingType = T1.Building where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join Buildings as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "UnitsPermittedCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Unit_BuildingPrereqs as T2 on T2.Unit = T1.UnitType inner join Buildings as T3 on T3.BuildingType = T2.PrereqBuilding where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "ValidFeatures", "Features", 1,"SELECT T1.rowid from Features as T1 inner join Building_ValidFeatures as T2 on T2.FeatureType = T1.FeatureType inner join Buildings as T3 on T3.BuildingType = T2.BuildingType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "ValidTerrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join Building_ValidTerrains as T2 on T2.TerrainType = T1.TerrainType inner join Buildings as T3 on T3.BuildingType = T2.BuildingType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "YieldChanges", "Building_YieldChanges", 1,"SELECT T1.rowid from Building_YieldChanges as T1 inner join Buildings as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "YieldDistrictCopyReference", "Building_YieldDistrictCopies", 1,"SELECT T1.rowid from Building_YieldDistrictCopies as T1 inner join Buildings as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Buildings", "YieldsPerEra", "Building_YieldsPerEra", 1,"SELECT T1.rowid from Building_YieldsPerEra as T1 inner join Buildings as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_CitizenYieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Building_CitizenYieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_GreatPersonPoints", "BuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join Building_GreatPersonPoints as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_GreatPersonPoints", "GreatPersonClassReference", "GreatPersonClasses", 0,"SELECT T1.rowid from GreatPersonClasses as T1 inner join Building_GreatPersonPoints as T2 on T2.GreatPersonClassType = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_GreatWorks", "ValidObjectTypes", "GreatWorkObjectTypes", 1,"SELECT T1.rowid from GreatWorkObjectTypes as T1 inner join GreatWork_ValidSubTypes as T2 on T2.GreatWorkObjectType = T1.GreatWorkObjectType inner join GreatWorkSlotTypes as T3 on T3.GreatWorkSlotType = T2.GreatWorkSlotType inner join Building_GreatWorks as T4 on T4.GreatWorkSlotType = T3.GreatWorkSlotType where T4.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_YieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Building_YieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_YieldDistrictCopies", "BuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join Building_YieldDistrictCopies as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_YieldDistrictCopies", "NewYieldTypeReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Building_YieldDistrictCopies as T2 on T2.NewYieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Building_YieldDistrictCopies", "OldYieldTypeReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Building_YieldDistrictCopies as T2 on T2.OldYieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BuildingConditions", "BuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join BuildingConditions as T2 on T2.BuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BuildingPrereqs", "BuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join BuildingPrereqs as T2 on T2.Building = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BuildingPrereqs", "PrereqBuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join BuildingPrereqs as T2 on T2.PrereqBuilding = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BuildingReplaces", "BaseBuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join BuildingReplaces as T2 on T2.ReplacesBuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("BuildingReplaces", "ReplacementBuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join BuildingReplaces as T2 on T2.CivUniqueBuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "BoostCollectionRef", "Boosts", 1,"SELECT T1.rowid from Boosts as T1 inner join Civics as T2 on T2.CivicType = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "BuildingCollectionReference", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join Civics as T2 on T2.CivicType = T1.PrereqCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "DistrictCollectionReference", "Districts", 1,"SELECT T1.rowid from Districts as T1 inner join Civics as T2 on T2.CivicType = T1.PrereqCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Civics as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "GovernmentCollection", "Governments", 1,"SELECT T1.rowid from Governments as T1 inner join Civics as T2 on T2.CivicType = T1.PrereqCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "ImprovementTourismCollection", "Improvement_Tourism", 1,"SELECT T1.rowid from Improvement_Tourism as T1 inner join Civics as T2 on T2.CivicType = T1.PrereqCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "MandatoryObsoleteCivicCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Civics as T2 on T2.CivicType = T1.MandatoryObsoleteCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "ObsoleteCivicCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Civics as T2 on T2.CivicType = T1.ObsoleteCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "PolicyCollection", "Policies", 1,"SELECT T1.rowid from Policies as T1 inner join Civics as T2 on T2.CivicType = T1.PrereqCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "PrereqCivicCollection", "CivicPrereqs", 1,"SELECT T1.rowid from CivicPrereqs as T1 inner join Civics as T2 on T2.CivicType = T1.Civic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "StartingCivicCollection", "StartingCivics", 1,"SELECT T1.rowid from StartingCivics as T1 inner join Civics as T2 on T2.CivicType = T1.Civic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civics", "UnitCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Civics as T2 on T2.CivicType = T1.PrereqCivic where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CivicPrereqs", "CivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join CivicPrereqs as T2 on T2.Civic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CivicPrereqs", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join CivicPrereqs as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CivicRandomCosts", "CivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join CivicRandomCosts as T2 on T2.CivicType = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "CitizenNameCollection", "CivilizationCitizenNames", 1,"SELECT T1.rowid from CivilizationCitizenNames as T1 inner join Civilizations as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "CityNameCollection", "CityNames", 1,"SELECT T1.rowid from CityNames as T1 inner join Civilizations as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "ReligionCollection", "Religions", 1,"SELECT T1.rowid from Religions as T1 inner join FavoredReligions as T2 on T2.ReligionType = T1.ReligionType inner join Civilizations as T3 on T3.CivilizationType = T2.CivilizationType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "StartBiasFeatureCollection", "StartBiasFeatures", 1,"SELECT T1.rowid from StartBiasFeatures as T1 inner join Civilizations as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "StartBiasResourceCollection", "StartBiasResources", 1,"SELECT T1.rowid from StartBiasResources as T1 inner join Civilizations as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "StartBiasRiverCollection", "StartBiasRivers", 1,"SELECT T1.rowid from StartBiasRivers as T1 inner join Civilizations as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "StartBiasTerrainCollection", "StartBiasTerrains", 1,"SELECT T1.rowid from StartBiasTerrains as T1 inner join Civilizations as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Civilizations", "TraitCollection", "Traits", 1,"SELECT T1.rowid from Traits as T1 inner join CivilizationTraits as T2 on T2.TraitType = T1.TraitType inner join Civilizations as T3 on T3.CivilizationType = T2.CivilizationType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("CivilizationLevels", "DiplomaticStartCollection", "DiplomaticStartStates", 1,"SELECT T1.rowid from DiplomaticStartStates as T1 inner join CivilizationLevels as T2 on T2.CivilizationLevelType = T1.PlayerCivLevel where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions", "InitiatorObsoleteCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join DiplomaticActions as T2 on T2.InitiatorObsoleteCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions", "InitiatorPrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join DiplomaticActions as T2 on T2.InitiatorPrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions", "InitiatorPrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join DiplomaticActions as T2 on T2.InitiatorPrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions", "TargetPrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join DiplomaticActions as T2 on T2.TargetPrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions", "TargetPrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join DiplomaticActions as T2 on T2.TargetPrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticActions", "ValidStates", "DiplomaticStates", 1,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticStateActions as T2 on T2.StateType = T1.StateType inner join DiplomaticActions as T3 on T3.DiplomaticActionType = T2.DiplomaticActionType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStartStates", "DiplomaticStateReference", "DiplomaticStates", 0,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticStartStates as T2 on T2.DiplomaticStateType = T1.StateType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStartStates", "OpponentCivLevelReference", "CivilizationLevels", 0,"SELECT T1.rowid from CivilizationLevels as T1 inner join DiplomaticStartStates as T2 on T2.OpponentCivLevel = T1.CivilizationLevelType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStartStates", "PlayerCivLevelReference", "CivilizationLevels", 0,"SELECT T1.rowid from CivilizationLevels as T1 inner join DiplomaticStartStates as T2 on T2.PlayerCivLevel = T1.CivilizationLevelType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStates", "TransitionActionCollection", "DiplomaticStateActions", 1,"SELECT T1.rowid from DiplomaticStateActions as T1 inner join DiplomaticStates as T2 on T2.StateType = T1.TransitionToState where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStates", "TransitionsOut", "DiplomaticStateTransitions", 1,"SELECT T1.rowid from DiplomaticStateTransitions as T1 inner join DiplomaticStates as T2 on T2.StateType = T1.BaseState where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStates", "ValidActions", "DiplomaticStateActions", 1,"SELECT T1.rowid from DiplomaticStateActions as T1 inner join DiplomaticStates as T2 on T2.StateType = T1.StateType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStateActions", "DiplomaticActionReference", "DiplomaticActions", 0,"SELECT T1.rowid from DiplomaticActions as T1 inner join DiplomaticStateActions as T2 on T2.DiplomaticActionType = T1.DiplomaticActionType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStateActions", "TransitionStateReference", "DiplomaticStates", 0,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticStateActions as T2 on T2.TransitionToState = T1.StateType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStateTransitions", "BaseStateReference", "DiplomaticStates", 0,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticStateTransitions as T2 on T2.BaseState = T1.StateType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticStateTransitions", "TransitionStateReference", "DiplomaticStates", 0,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticStateTransitions as T2 on T2.TransitionState = T1.StateType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticTriggers", "RequiredStateCollection", "DiplomaticStates", 1,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticTriggers_RequiredStates as T2 on T2.RequiredState = T1.StateType inner join DiplomaticTriggers as T3 on T3.TriggerType = T2.TriggerType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticTriggeredTransitions", "CivLevelReference", "CivilizationLevels", 0,"SELECT T1.rowid from CivilizationLevels as T1 inner join DiplomaticTriggeredTransitions as T2 on T2.CivilizationLevel = T1.CivilizationLevelType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticTriggeredTransitions", "OpponentCivLevelReference", "CivilizationLevels", 0,"SELECT T1.rowid from CivilizationLevels as T1 inner join DiplomaticTriggeredTransitions as T2 on T2.OpponentCivilizationLevel = T1.CivilizationLevelType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticTriggeredTransitions", "TransitionStateReference", "DiplomaticStates", 0,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticTriggeredTransitions as T2 on T2.TransitionState = T1.StateType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticTriggeredTransitions", "TriggerReference", "DiplomaticTriggers", 0,"SELECT T1.rowid from DiplomaticTriggers as T1 inner join DiplomaticTriggeredTransitions as T2 on T2.TriggerType = T1.TriggerType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticTriggers_RequiredStates", "StateReference", "DiplomaticStates", 0,"SELECT T1.rowid from DiplomaticStates as T1 inner join DiplomaticTriggers_RequiredStates as T2 on T2.RequiredState = T1.StateType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticVisibilitySources", "GreatPersonIndividualReference", "GreatPersonIndividuals", 0,"SELECT T1.rowid from GreatPersonIndividuals as T1 inner join DiplomaticVisibilitySources as T2 on T2.GreatPersonIndividualType = T1.GreatPersonIndividualType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticVisibilitySources", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join DiplomaticVisibilitySources as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DiplomaticVisibilitySources", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join DiplomaticVisibilitySources as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "AdjacencyAppealYieldChanges", "Adjacent_AppealYieldChanges", 1,"SELECT T1.rowid from Adjacent_AppealYieldChanges as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "AdjacencyYieldChanges", "District_Adjacencies", 1,"SELECT T1.rowid from District_Adjacencies as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "AppealHousingChangeReference", "AppealHousingChanges", 1,"SELECT T1.rowid from AppealHousingChanges as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "BuildingCollectionReference", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join Districts as T2 on T2.DistrictType = T1.PrereqDistrict where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "CitizenGreatPersonPointsReference", "District_CitizenGreatPersonPoints", 1,"SELECT T1.rowid from District_CitizenGreatPersonPoints as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "CitizenYieldChangesReference", "District_CitizenYieldChanges", 1,"SELECT T1.rowid from District_CitizenYieldChanges as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "ExclusionReference", "ExcludedDistricts", 1,"SELECT T1.rowid from ExcludedDistricts as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "GreatPersonPointsReference", "District_GreatPersonPoints", 1,"SELECT T1.rowid from District_GreatPersonPoints as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "MutuallyExclusiveDistrictReference", "MutuallyExclusiveDistricts", 1,"SELECT T1.rowid from MutuallyExclusiveDistricts as T1 inner join Districts as T2 on T2.DistrictType = T1.District where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Districts as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Districts as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "ProjectCollection", "Projects", 1,"SELECT T1.rowid from Projects as T1 inner join Districts as T2 on T2.DistrictType = T1.PrereqDistrict where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "ReplacedByCollection", "DistrictReplaces", 1,"SELECT T1.rowid from DistrictReplaces as T1 inner join Districts as T2 on T2.DistrictType = T1.ReplacesDistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "ReplacesCollection", "DistrictReplaces", 1,"SELECT T1.rowid from DistrictReplaces as T1 inner join Districts as T2 on T2.DistrictType = T1.CivUniqueDistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "RequiredFeatures", "Features", 1,"SELECT T1.rowid from Features as T1 inner join District_RequiredFeatures as T2 on T2.FeatureType = T1.FeatureType inner join Districts as T3 on T3.DistrictType = T2.DistrictType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "StartingBuildingCollection", "StartingBuildings", 1,"SELECT T1.rowid from StartingBuildings as T1 inner join Districts as T2 on T2.DistrictType = T1.District where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "TradeRouteYieldChanges", "District_TradeRouteYields", 1,"SELECT T1.rowid from District_TradeRouteYields as T1 inner join Districts as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join Districts as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Districts", "ValidTerrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join District_ValidTerrains as T2 on T2.TerrainType = T1.TerrainType inner join Districts as T3 on T3.DistrictType = T2.DistrictType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_Adjacencies", "YieldChangeReference", "Adjacency_YieldChanges", 0,"SELECT T1.rowid from Adjacency_YieldChanges as T1 inner join District_Adjacencies as T2 on T2.YieldChangeId = T1.ID where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_CitizenGreatPersonPoints", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join District_CitizenGreatPersonPoints as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_CitizenGreatPersonPoints", "GreatPersonClassReference", "GreatPersonClasses", 0,"SELECT T1.rowid from GreatPersonClasses as T1 inner join District_CitizenGreatPersonPoints as T2 on T2.GreatPersonClassType = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_CitizenYieldChanges", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join District_CitizenYieldChanges as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_CitizenYieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join District_CitizenYieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_GreatPersonPoints", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join District_GreatPersonPoints as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_GreatPersonPoints", "GreatPersonClassReference", "GreatPersonClasses", 0,"SELECT T1.rowid from GreatPersonClasses as T1 inner join District_GreatPersonPoints as T2 on T2.GreatPersonClassType = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_TradeRouteYields", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join District_TradeRouteYields as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("District_TradeRouteYields", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join District_TradeRouteYields as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DistrictReplaces", "BaseDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join DistrictReplaces as T2 on T2.ReplacesDistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("DistrictReplaces", "ReplacementDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join DistrictReplaces as T2 on T2.CivUniqueDistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "BonusMinorStartingUnitCollection", "BonusMinorStartingUnits", 1,"SELECT T1.rowid from BonusMinorStartingUnits as T1 inner join Eras as T2 on T2.EraType = T1.Era where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "CivicCollectionReference", "Civics", 1,"SELECT T1.rowid from Civics as T1 inner join Eras as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "MajorStartingUnitCollection", "MajorStartingUnits", 1,"SELECT T1.rowid from MajorStartingUnits as T1 inner join Eras as T2 on T2.EraType = T1.Era where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "StartingBuildingCollection", "StartingBuildings", 1,"SELECT T1.rowid from StartingBuildings as T1 inner join Eras as T2 on T2.EraType = T1.Era where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "StartingCivicBoostedCollection", "StartingBoostedCivics", 1,"SELECT T1.rowid from StartingBoostedCivics as T1 inner join Eras as T2 on T2.EraType = T1.Era where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "StartingCivicCollection", "StartingCivics", 1,"SELECT T1.rowid from StartingCivics as T1 inner join Eras as T2 on T2.EraType = T1.Era where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "StartingEraCollection", "StartEras", 1,"SELECT T1.rowid from StartEras as T1 inner join Eras as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "StartingGovernmentCollection", "StartingGovernments", 1,"SELECT T1.rowid from StartingGovernments as T1 inner join Eras as T2 on T2.EraType = T1.Era where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "StartingTechnologyBoostedCollection", "StartingBoostedTechnologies", 1,"SELECT T1.rowid from StartingBoostedTechnologies as T1 inner join Eras as T2 on T2.EraType = T1.Era where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Eras", "TechCollectionReference", "Technologies", 1,"SELECT T1.rowid from Technologies as T1 inner join Eras as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ExcludedAdjacencies", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join ExcludedAdjacencies as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ExcludedDistricts", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join ExcludedDistricts as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ExcludedGreatPersonClasses", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join ExcludedGreatPersonClasses as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ExclusiveAgendas", "AgendaOneReference", "Agendas", 0,"SELECT T1.rowid from Agendas as T1 inner join ExclusiveAgendas as T2 on T2.AgendaOne = T1.AgendaType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ExclusiveAgendas", "AgendaTwoReference", "Agendas", 0,"SELECT T1.rowid from Agendas as T1 inner join ExclusiveAgendas as T2 on T2.AgendaTwo = T1.AgendaType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "AddCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Features as T2 on T2.AddCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "AdjacentFeatures", "Features", 1,"SELECT T1.rowid from Features as T1 inner join Feature_AdjacentFeatures as T2 on T2.FeatureTypeAdjacent = T1.FeatureType inner join Features as T3 on T3.FeatureType = T2.FeatureType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "AdjacentTerrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join Feature_AdjacentTerrains as T2 on T2.TerrainType = T1.TerrainType inner join Features as T3 on T3.FeatureType = T2.FeatureType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "AdjacentYields", "Feature_AdjacentYields", 1,"SELECT T1.rowid from Feature_AdjacentYields as T1 inner join Features as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "FeatureRemoveCollection", "Feature_Removes", 1,"SELECT T1.rowid from Feature_Removes as T1 inner join Features as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "NotAdjacentTerrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join Feature_NotAdjacentTerrains as T2 on T2.TerrainType = T1.TerrainType inner join Features as T3 on T3.FeatureType = T2.FeatureType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "NotNearFeatures", "Features", 1,"SELECT T1.rowid from Features as T1 inner join Feature_NotNearFeatures as T2 on T2.FeatureTypeAvoid = T1.FeatureType inner join Features as T3 on T3.FeatureType = T2.FeatureType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "RemoveTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Features as T2 on T2.RemoveTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "StartBiasFeatureCollection", "StartBiasFeatures", 1,"SELECT T1.rowid from StartBiasFeatures as T1 inner join Features as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "UnitMovements", "Feature_UnitMovements", 1,"SELECT T1.rowid from Feature_UnitMovements as T1 inner join Features as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "ValidTerrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join Feature_ValidTerrains as T2 on T2.TerrainType = T1.TerrainType inner join Features as T3 on T3.FeatureType = T2.FeatureType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Features", "YieldChanges", "Feature_YieldChanges", 1,"SELECT T1.rowid from Feature_YieldChanges as T1 inner join Features as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Feature_AdjacentYields", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Feature_AdjacentYields as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Feature_Removes", "FeatureReference", "Features", 0,"SELECT T1.rowid from Features as T1 inner join Feature_Removes as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Feature_Removes", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Feature_Removes as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Feature_YieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Feature_YieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GameSpeeds", "GameSpeedScalingCollection", "GameSpeed_Scalings", 1,"SELECT T1.rowid from GameSpeed_Scalings as T1 inner join GameSpeeds as T2 on T2.GameSpeedType = T1.GameSpeedType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GameSpeeds", "GameSpeedTurnCollection", "GameSpeed_Turns", 1,"SELECT T1.rowid from GameSpeed_Turns as T1 inner join GameSpeeds as T2 on T2.GameSpeedType = T1.GameSpeedType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GameSpeed_Scalings", "GameSpeedDurationCollection", "GameSpeed_Durations", 1,"SELECT T1.rowid from GameSpeed_Durations as T1 inner join GameSpeed_Scalings as T2 on T2.GameSpeedScalingType = T1.GameSpeedScalingType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GameSpeed_Turns", "GameSpeedReference", "GameSpeeds", 0,"SELECT T1.rowid from GameSpeeds as T1 inner join GameSpeed_Turns as T2 on T2.GameSpeedType = T1.GameSpeedType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GoodyHuts", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join GoodyHuts as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GoodyHuts", "SubTypeGoodyHutCollection", "GoodyHutSubTypes", 1,"SELECT T1.rowid from GoodyHutSubTypes as T1 inner join GoodyHuts as T2 on T2.GoodyHutType = T1.GoodyHut where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Governments", "GovernmentSlotsReference", "Government_SlotCounts", 1,"SELECT T1.rowid from Government_SlotCounts as T1 inner join Governments as T2 on T2.GovernmentType = T1.GovernmentType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Governments", "PolicyToUnlockReference", "Policies", 0,"SELECT T1.rowid from Policies as T1 inner join Governments as T2 on T2.PolicyToUnlock = T1.PolicyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Governments", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Governments as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Governments", "StartingGovernmentCollection", "StartingGovernments", 1,"SELECT T1.rowid from StartingGovernments as T1 inner join Governments as T2 on T2.GovernmentType = T1.Government where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Government_SlotCounts", "GovernmentReference", "Governments", 0,"SELECT T1.rowid from Governments as T1 inner join Government_SlotCounts as T2 on T2.GovernmentType = T1.GovernmentType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Government_SlotCounts", "SlotReference", "GovernmentSlots", 0,"SELECT T1.rowid from GovernmentSlots as T1 inner join Government_SlotCounts as T2 on T2.GovernmentSlotType = T1.GovernmentSlotType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GovernmentTiers", "GovernmentsOfTier", "Governments", 1,"SELECT T1.rowid from Governments as T1 inner join GovernmentTiers as T2 on T2.TierType = T1.Tier where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonClasses", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join GreatPersonClasses as T2 on T2.DistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonClasses", "ExclusionReference", "ExcludedGreatPersonClasses", 1,"SELECT T1.rowid from ExcludedGreatPersonClasses as T1 inner join GreatPersonClasses as T2 on T2.GreatPersonClassType = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonClasses", "PseudoYieldReference", "PseudoYields", 0,"SELECT T1.rowid from PseudoYields as T1 inner join GreatPersonClasses as T2 on T2.PseudoYieldType = T1.PseudoYieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonClasses", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join GreatPersonClasses as T2 on T2.UnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonIndividuals", "ActionRequiresCityGreatWorkObjectTypeReference", "GreatWorkObjectTypes", 0,"SELECT T1.rowid from GreatWorkObjectTypes as T1 inner join GreatPersonIndividuals as T2 on T2.ActionRequiresCityGreatWorkObjectType = T1.GreatWorkObjectType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonIndividuals", "ActionRequiresCompletedDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join GreatPersonIndividuals as T2 on T2.ActionRequiresCompletedDistrictType = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonIndividuals", "ActionRequiresMissingBuildingTypeReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join GreatPersonIndividuals as T2 on T2.ActionRequiresMissingBuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonIndividuals", "ActionRequiresOnOrAdjacentFeatureTypeReference", "Features", 0,"SELECT T1.rowid from Features as T1 inner join GreatPersonIndividuals as T2 on T2.ActionRequiresOnOrAdjacentFeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonIndividuals", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join GreatPersonIndividuals as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonIndividuals", "GreatPersonClassReference", "GreatPersonClasses", 0,"SELECT T1.rowid from GreatPersonClasses as T1 inner join GreatPersonIndividuals as T2 on T2.GreatPersonClassType = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatPersonIndividuals", "GreatWorkCollection", "GreatWorks", 1,"SELECT T1.rowid from GreatWorks as T1 inner join GreatPersonIndividuals as T2 on T2.GreatPersonIndividualType = T1.GreatPersonIndividualType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWorks", "BuildingCollection", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join Building_GreatWorks as T2 on T2.BuildingType = T1.BuildingType inner join GreatWorkSlotTypes as T3 on T3.GreatWorkSlotType = T2.GreatWorkSlotType inner join GreatWork_ValidSubTypes as T4 on T4.GreatWorkSlotType = T3.GreatWorkSlotType inner join GreatWorkObjectTypes as T5 on T5.GreatWorkObjectType = T4.GreatWorkObjectType inner join GreatWorks as T6 on T6.GreatWorkObjectType = T5.GreatWorkObjectType where T6.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWorks", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join GreatWorks as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWorks", "GreatPersonReference", "GreatPersonIndividuals", 0,"SELECT T1.rowid from GreatPersonIndividuals as T1 inner join GreatWorks as T2 on T2.GreatPersonIndividualType = T1.GreatPersonIndividualType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWorks", "GreatWorkObjectReference", "GreatWorkObjectTypes", 0,"SELECT T1.rowid from GreatWorkObjectTypes as T1 inner join GreatWorks as T2 on T2.GreatWorkObjectType = T1.GreatWorkObjectType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWorks", "YieldChanges", "GreatWork_YieldChanges", 1,"SELECT T1.rowid from GreatWork_YieldChanges as T1 inner join GreatWorks as T2 on T2.GreatWorkType = T1.GreatWorkType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWork_ValidSubTypes", "ObjectReference", "GreatWorkObjectTypes", 0,"SELECT T1.rowid from GreatWorkObjectTypes as T1 inner join GreatWork_ValidSubTypes as T2 on T2.GreatWorkObjectType = T1.GreatWorkObjectType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWork_ValidSubTypes", "SlotReference", "GreatWorkSlotTypes", 0,"SELECT T1.rowid from GreatWorkSlotTypes as T1 inner join GreatWork_ValidSubTypes as T2 on T2.GreatWorkSlotType = T1.GreatWorkSlotType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWork_YieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join GreatWork_YieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWorkObjectTypes", "BuildingCollection", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join Building_GreatWorks as T2 on T2.BuildingType = T1.BuildingType inner join GreatWorkSlotTypes as T3 on T3.GreatWorkSlotType = T2.GreatWorkSlotType inner join GreatWork_ValidSubTypes as T4 on T4.GreatWorkSlotType = T3.GreatWorkSlotType inner join GreatWorkObjectTypes as T5 on T5.GreatWorkObjectType = T4.GreatWorkObjectType where T5.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("GreatWorkObjectTypes", "PseudoYieldReference", "PseudoYields", 0,"SELECT T1.rowid from PseudoYields as T1 inner join GreatWorkObjectTypes as T2 on T2.PseudoYieldType = T1.PseudoYieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("HeroClasses", "DiscoveryMinEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join HeroClasses as T2 on T2.DiscoveryMinEraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("HeroClasses", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join HeroClasses as T2 on T2.UnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("HeroClassProgressions", "HeroClassReference", "HeroClasses", 0,"SELECT T1.rowid from HeroClasses as T1 inner join HeroClassProgressions as T2 on T2.HeroClassType = T1.HeroClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("HeroClassUnitCommands", "HeroClassReference", "HeroClasses", 0,"SELECT T1.rowid from HeroClasses as T1 inner join HeroClassUnitCommands as T2 on T2.HeroClassType = T1.HeroClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("HeroClassUnitCommands", "UnitCommandReference", "UnitCommands", 0,"SELECT T1.rowid from UnitCommands as T1 inner join HeroClassUnitCommands as T2 on T2.UnitCommandType = T1.CommandType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "AdjacencyYieldChanges", "Improvement_Adjacencies", 1,"SELECT T1.rowid from Improvement_Adjacencies as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "BonusYieldChanges", "Improvement_BonusYieldChanges", 1,"SELECT T1.rowid from Improvement_BonusYieldChanges as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "InvalidAdjacentFeature", "Improvement_InvalidAdjacentFeatures", 1,"SELECT T1.rowid from Improvement_InvalidAdjacentFeatures as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Improvements as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Improvements as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "TourismCollection", "Improvement_Tourism", 1,"SELECT T1.rowid from Improvement_Tourism as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join Improvements as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "ValidAdjacentResources", "Improvement_ValidAdjacentResources", 1,"SELECT T1.rowid from Improvement_ValidAdjacentResources as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "ValidAdjacentTerrains", "Improvement_ValidAdjacentTerrains", 1,"SELECT T1.rowid from Improvement_ValidAdjacentTerrains as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "ValidBuildUnits", "Improvement_ValidBuildUnits", 1,"SELECT T1.rowid from Improvement_ValidBuildUnits as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "ValidFeatures", "Features", 1,"SELECT T1.rowid from Features as T1 inner join Improvement_ValidFeatures as T2 on T2.FeatureType = T1.FeatureType inner join Improvements as T3 on T3.ImprovementType = T2.ImprovementType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "ValidResources", "Improvement_ValidResources", 1,"SELECT T1.rowid from Improvement_ValidResources as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "ValidTerrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join Improvement_ValidTerrains as T2 on T2.TerrainType = T1.TerrainType inner join Improvements as T3 on T3.ImprovementType = T2.ImprovementType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "YieldChanges", "Improvement_YieldChanges", 1,"SELECT T1.rowid from Improvement_YieldChanges as T1 inner join Improvements as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvements", "YieldFromAppealReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Improvements as T2 on T2.YieldFromAppeal = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_Adjacencies", "YieldChangeReference", "Adjacency_YieldChanges", 0,"SELECT T1.rowid from Adjacency_YieldChanges as T1 inner join Improvement_Adjacencies as T2 on T2.YieldChangeId = T1.ID where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_BonusYieldChanges", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_BonusYieldChanges as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_BonusYieldChanges", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Improvement_BonusYieldChanges as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_BonusYieldChanges", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Improvement_BonusYieldChanges as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_BonusYieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Improvement_BonusYieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_InvalidAdjacentFeatures", "FeatureReference", "Features", 0,"SELECT T1.rowid from Features as T1 inner join Improvement_InvalidAdjacentFeatures as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_InvalidAdjacentFeatures", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_InvalidAdjacentFeatures as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_Tourism", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_Tourism as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_Tourism", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Improvement_Tourism as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_Tourism", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Improvement_Tourism as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidAdjacentResources", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_ValidAdjacentResources as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidAdjacentResources", "ResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join Improvement_ValidAdjacentResources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidAdjacentTerrains", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_ValidAdjacentTerrains as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidAdjacentTerrains", "TerrainReference", "Terrains", 0,"SELECT T1.rowid from Terrains as T1 inner join Improvement_ValidAdjacentTerrains as T2 on T2.TerrainType = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidBuildUnits", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join Improvement_ValidBuildUnits as T2 on T2.UnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidFeatures", "FeatureReference", "Features", 0,"SELECT T1.rowid from Features as T1 inner join Improvement_ValidFeatures as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidFeatures", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Improvement_ValidFeatures as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidFeatures", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Improvement_ValidFeatures as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidResources", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_ValidResources as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidResources", "ResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join Improvement_ValidResources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidTerrains", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_ValidTerrains as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidTerrains", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Improvement_ValidTerrains as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidTerrains", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Improvement_ValidTerrains as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_ValidTerrains", "TerrainReference", "Terrains", 0,"SELECT T1.rowid from Terrains as T1 inner join Improvement_ValidTerrains as T2 on T2.TerrainType = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_YieldChanges", "ImprovementReference", "Improvements", 0,"SELECT T1.rowid from Improvements as T1 inner join Improvement_YieldChanges as T2 on T2.ImprovementType = T1.ImprovementType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Improvement_YieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Improvement_YieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Leaders", "CivilizationCollection", "Civilizations", 1,"SELECT T1.rowid from Civilizations as T1 inner join CivilizationLeaders as T2 on T2.CivilizationType = T1.CivilizationType inner join Leaders as T3 on T3.LeaderType = T2.LeaderType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Leaders", "InheritLeaderReference", "Leaders", 0,"SELECT T1.rowid from Leaders as T1 inner join Leaders as T2 on T2.InheritFrom = T1.LeaderType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Leaders", "PreferredAgendaCollection", "AgendaPreferredLeaders", 1,"SELECT T1.rowid from AgendaPreferredLeaders as T1 inner join Leaders as T2 on T2.LeaderType = T1.LeaderType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Leaders", "ReligionCollection", "Religions", 1,"SELECT T1.rowid from Religions as T1 inner join FavoredReligions as T2 on T2.ReligionType = T1.ReligionType inner join Leaders as T3 on T3.LeaderType = T2.LeaderType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Leaders", "TraitCollection", "Traits", 1,"SELECT T1.rowid from Traits as T1 inner join LeaderTraits as T2 on T2.TraitType = T1.TraitType inner join Leaders as T3 on T3.LeaderType = T2.LeaderType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("MajorStartingUnits", "DifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join MajorStartingUnits as T2 on T2.MinDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("MajorStartingUnits", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join MajorStartingUnits as T2 on T2.Era = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("MajorStartingUnits", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join MajorStartingUnits as T2 on T2.Unit = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Maps", "GreatPersonClassesReference", "Map_GreatPersonClasses", 1,"SELECT T1.rowid from Map_GreatPersonClasses as T1 inner join Maps as T2 on T2.MapSizeType = T1.MapSizeType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Map_GreatPersonClasses", "GreatPersonClassReference", "GreatPersonClasses", 0,"SELECT T1.rowid from GreatPersonClasses as T1 inner join Map_GreatPersonClasses as T2 on T2.GreatPersonClassType = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Map_GreatPersonClasses", "MapSizeReference", "Maps", 0,"SELECT T1.rowid from Maps as T1 inner join Map_GreatPersonClasses as T2 on T2.MapSizeType = T1.MapSizeType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("MutuallyExclusiveBuildings", "BuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join MutuallyExclusiveBuildings as T2 on T2.Building = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("MutuallyExclusiveBuildings", "MutuallyExclusiveBuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join MutuallyExclusiveBuildings as T2 on T2.MutuallyExclusiveBuilding = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("MutuallyExclusiveDistricts", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join MutuallyExclusiveDistricts as T2 on T2.District = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("MutuallyExclusiveDistricts", "MutuallyExclusiveDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join MutuallyExclusiveDistricts as T2 on T2.MutuallyExclusiveDistrict = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ObsoletePolicies", "ObsoletePolicyReference", "Policies", 0,"SELECT T1.rowid from Policies as T1 inner join ObsoletePolicies as T2 on T2.ObsoletePolicy = T1.PolicyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ObsoletePolicies", "PolicyReference", "Policies", 0,"SELECT T1.rowid from Policies as T1 inner join ObsoletePolicies as T2 on T2.PolicyType = T1.PolicyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ObsoletePolicies", "RequiresAvailableGreatPersonClassReference", "GreatPersonClasses", 0,"SELECT T1.rowid from GreatPersonClasses as T1 inner join ObsoletePolicies as T2 on T2.RequiresAvailableGreatPersonClass = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("OpTeamRequirements", "AiTypeDependenceReference", "UnitAiTypes", 0,"SELECT T1.rowid from UnitAiTypes as T1 inner join OpTeamRequirements as T2 on T2.AiTypeDependence = T1.AiType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Policies", "PolicyModifiers", "PolicyModifiers", 1,"SELECT T1.rowid from PolicyModifiers as T1 inner join Policies as T2 on T2.PolicyType = T1.PolicyType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Policies", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Policies as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Policies", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Policies as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Policies", "SlotReference", "GovernmentSlots", 0,"SELECT T1.rowid from GovernmentSlots as T1 inner join Policies as T2 on T2.GovernmentSlotType = T1.GovernmentSlotType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "AntecedantProjectCollectionReference", "ProjectPrereqs", 1,"SELECT T1.rowid from ProjectPrereqs as T1 inner join Projects as T2 on T2.ProjectType = T1.PrereqProjectType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "GreatPersonPointsReference", "Project_GreatPersonPoints", 1,"SELECT T1.rowid from Project_GreatPersonPoints as T1 inner join Projects as T2 on T2.ProjectType = T1.ProjectType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Projects as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "PrereqDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join Projects as T2 on T2.PrereqDistrict = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "PrereqProjectCollectionReference", "ProjectPrereqs", 1,"SELECT T1.rowid from ProjectPrereqs as T1 inner join Projects as T2 on T2.ProjectType = T1.ProjectType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "PrereqResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join Projects as T2 on T2.PrereqResource = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Projects as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "RequiredBuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join Projects as T2 on T2.RequiredBuilding = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "VisualBuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join Projects as T2 on T2.VisualBuildingType = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Projects", "YieldConversionsCollectionReference", "Project_YieldConversions", 1,"SELECT T1.rowid from Project_YieldConversions as T1 inner join Projects as T2 on T2.ProjectType = T1.ProjectType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Project_GreatPersonPoints", "GreatPersonClassReference", "GreatPersonClasses", 0,"SELECT T1.rowid from GreatPersonClasses as T1 inner join Project_GreatPersonPoints as T2 on T2.GreatPersonClassType = T1.GreatPersonClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Project_GreatPersonPoints", "ProjectReference", "Projects", 0,"SELECT T1.rowid from Projects as T1 inner join Project_GreatPersonPoints as T2 on T2.ProjectType = T1.ProjectType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Project_YieldConversions", "ProjectReference", "Projects", 0,"SELECT T1.rowid from Projects as T1 inner join Project_YieldConversions as T2 on T2.ProjectType = T1.ProjectType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Project_YieldConversions", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Project_YieldConversions as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ProjectPrereqs", "PrereqProjectReference", "Projects", 0,"SELECT T1.rowid from Projects as T1 inner join ProjectPrereqs as T2 on T2.PrereqProjectType = T1.ProjectType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ProjectPrereqs", "ProjectReference", "Projects", 0,"SELECT T1.rowid from Projects as T1 inner join ProjectPrereqs as T2 on T2.ProjectType = T1.ProjectType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("RandomAgendas", "AgendaReference", "Agendas", 0,"SELECT T1.rowid from Agendas as T1 inner join RandomAgendas as T2 on T2.AgendaType = T1.AgendaType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("RandomAgendas", "LeaderCollection", "Leaders", 1,"SELECT T1.rowid from Leaders as T1 inner join AgendaPreferredLeaders as T2 on T2.LeaderType = T1.LeaderType inner join RandomAgendas as T3 on T3.AgendaType = T2.AgendaType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "Harvests", "Resource_Harvests", 1,"SELECT T1.rowid from Resource_Harvests as T1 inner join Resources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "ImprovementAdjacentResourceCollection", "Improvement_ValidAdjacentResources", 1,"SELECT T1.rowid from Improvement_ValidAdjacentResources as T1 inner join Resources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "ImprovementCollection", "Improvement_ValidResources", 1,"SELECT T1.rowid from Improvement_ValidResources as T1 inner join Resources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Resources as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Resources as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "ResourceProjectCollection", "Projects", 1,"SELECT T1.rowid from Projects as T1 inner join Resources as T2 on T2.ResourceType = T1.PrereqResource where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "StartBiasResourceCollection", "StartBiasResources", 1,"SELECT T1.rowid from StartBiasResources as T1 inner join Resources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "StrategicUnitCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Resources as T2 on T2.ResourceType = T1.StrategicResource where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "TradeRouteYieldChanges", "Resource_TradeRouteYields", 1,"SELECT T1.rowid from Resource_TradeRouteYields as T1 inner join Resources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "ValidTerrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join Resource_ValidTerrains as T2 on T2.TerrainType = T1.TerrainType inner join Resources as T3 on T3.ResourceType = T2.ResourceType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resources", "YieldChangeCollection", "Resource_YieldChanges", 1,"SELECT T1.rowid from Resource_YieldChanges as T1 inner join Resources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resource_Conditions", "ResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join Resource_Conditions as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resource_Harvests", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Resource_Harvests as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resource_Harvests", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Resource_Harvests as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resource_TradeRouteYields", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Resource_TradeRouteYields as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Resource_YieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Resource_YieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Routes", "PrereqEraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Routes as T2 on T2.PrereqEra = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Routes", "ValidBuildUnits", "Route_ValidBuildUnits", 1,"SELECT T1.rowid from Route_ValidBuildUnits as T1 inner join Routes as T2 on T2.RouteType = T1.RouteType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Route_ValidBuildUnits", "RouteReference", "Routes", 0,"SELECT T1.rowid from Routes as T1 inner join Route_ValidBuildUnits as T2 on T2.RouteType = T1.RouteType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Route_ValidBuildUnits", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join Route_ValidBuildUnits as T2 on T2.UnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ScoringCategories", "ScoringLineItemCollection", "ScoringLineItems", 1,"SELECT T1.rowid from ScoringLineItems as T1 inner join ScoringCategories as T2 on T2.CategoryType = T1.Category where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("ScoringLineItems", "CategoryReference", "ScoringCategories", 0,"SELECT T1.rowid from ScoringCategories as T1 inner join ScoringLineItems as T2 on T2.Category = T1.CategoryType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartBiasFeatures", "CivilizationReference", "Civilizations", 0,"SELECT T1.rowid from Civilizations as T1 inner join StartBiasFeatures as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartBiasFeatures", "FeatureReference", "Features", 0,"SELECT T1.rowid from Features as T1 inner join StartBiasFeatures as T2 on T2.FeatureType = T1.FeatureType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartBiasResources", "CivilizationReference", "Civilizations", 0,"SELECT T1.rowid from Civilizations as T1 inner join StartBiasResources as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartBiasResources", "ResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join StartBiasResources as T2 on T2.ResourceType = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartBiasRivers", "CivilizationReference", "Civilizations", 0,"SELECT T1.rowid from Civilizations as T1 inner join StartBiasRivers as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartBiasTerrains", "CivilizationReference", "Civilizations", 0,"SELECT T1.rowid from Civilizations as T1 inner join StartBiasTerrains as T2 on T2.CivilizationType = T1.CivilizationType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartBiasTerrains", "TerrainReference", "Terrains", 0,"SELECT T1.rowid from Terrains as T1 inner join StartBiasTerrains as T2 on T2.TerrainType = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartEras", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join StartEras as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBoostedCivics", "CivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join StartingBoostedCivics as T2 on T2.Civic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBoostedCivics", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join StartingBoostedCivics as T2 on T2.Era = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBoostedTechnologies", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join StartingBoostedTechnologies as T2 on T2.Era = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBoostedTechnologies", "TechnologyReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join StartingBoostedTechnologies as T2 on T2.Technology = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBuildings", "BuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join StartingBuildings as T2 on T2.Building = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBuildings", "DifficultyReference", "Difficulties", 0,"SELECT T1.rowid from Difficulties as T1 inner join StartingBuildings as T2 on T2.MinDifficulty = T1.DifficultyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBuildings", "DistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join StartingBuildings as T2 on T2.District = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingBuildings", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join StartingBuildings as T2 on T2.Era = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingCivics", "CivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join StartingCivics as T2 on T2.Civic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingCivics", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join StartingCivics as T2 on T2.Era = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingGovernments", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join StartingGovernments as T2 on T2.Era = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StartingGovernments", "GovernmentReference", "Governments", 0,"SELECT T1.rowid from Governments as T1 inner join StartingGovernments as T2 on T2.Government = T1.GovernmentType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Strategies", "ConditionCollection", "StrategyConditions", 1,"SELECT T1.rowid from StrategyConditions as T1 inner join Strategies as T2 on T2.StrategyType = T1.StrategyType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Strategies", "PriorityCollection", "Strategy_Priorities", 1,"SELECT T1.rowid from Strategy_Priorities as T1 inner join Strategies as T2 on T2.StrategyType = T1.StrategyType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Strategies", "VictoryReference", "Victories", 0,"SELECT T1.rowid from Victories as T1 inner join Strategies as T2 on T2.VictoryType = T1.VictoryType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Strategies", "YieldCollection", "Strategy_YieldPriorities", 1,"SELECT T1.rowid from Strategy_YieldPriorities as T1 inner join Strategies as T2 on T2.StrategyType = T1.StrategyType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Strategy_YieldPriorities", "PseudoYieldReference", "PseudoYields", 0,"SELECT T1.rowid from PseudoYields as T1 inner join Strategy_YieldPriorities as T2 on T2.PseudoYieldType = T1.PseudoYieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Strategy_YieldPriorities", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Strategy_YieldPriorities as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("StrategyConditions", "StrategyReference", "Strategies", 0,"SELECT T1.rowid from Strategies as T1 inner join StrategyConditions as T2 on T2.StrategyType = T1.StrategyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "BoostCollectionReference", "Boosts", 1,"SELECT T1.rowid from Boosts as T1 inner join Technologies as T2 on T2.TechnologyType = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "BuildingCollectionReference", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join Technologies as T2 on T2.TechnologyType = T1.PrereqTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "DistrictCollectionReference", "Districts", 1,"SELECT T1.rowid from Districts as T1 inner join Technologies as T2 on T2.TechnologyType = T1.PrereqTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "EmbarkUnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join Technologies as T2 on T2.EmbarkUnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "EraReference", "Eras", 0,"SELECT T1.rowid from Eras as T1 inner join Technologies as T2 on T2.EraType = T1.EraType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "ImprovementCollection", "Improvements", 1,"SELECT T1.rowid from Improvements as T1 inner join Technologies as T2 on T2.TechnologyType = T1.PrereqTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "ImprovementTourismCollection", "Improvement_Tourism", 1,"SELECT T1.rowid from Improvement_Tourism as T1 inner join Technologies as T2 on T2.TechnologyType = T1.PrereqTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "MandatoryObsoleteTechCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Technologies as T2 on T2.TechnologyType = T1.MandatoryObsoleteTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "ObsoleteTechCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Technologies as T2 on T2.TechnologyType = T1.ObsoleteTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "PolicyCollection", "Policies", 1,"SELECT T1.rowid from Policies as T1 inner join Technologies as T2 on T2.TechnologyType = T1.PrereqTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "PrereqTechCollection", "TechnologyPrereqs", 1,"SELECT T1.rowid from TechnologyPrereqs as T1 inner join Technologies as T2 on T2.TechnologyType = T1.Technology where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "ProjectCollection", "Projects", 1,"SELECT T1.rowid from Projects as T1 inner join Technologies as T2 on T2.TechnologyType = T1.PrereqTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Technologies", "UnitCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join Technologies as T2 on T2.TechnologyType = T1.PrereqTech where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TechnologyPrereqs", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join TechnologyPrereqs as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TechnologyPrereqs", "TechnologyReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join TechnologyPrereqs as T2 on T2.Technology = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TechnologyRandomCosts", "TechnologyReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join TechnologyRandomCosts as T2 on T2.TechnologyType = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Terrains", "ImprovementAdjacentTerrainCollection", "Improvement_ValidAdjacentTerrains", 1,"SELECT T1.rowid from Improvement_ValidAdjacentTerrains as T1 inner join Terrains as T2 on T2.TerrainType = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Terrains", "ImprovementCollection", "Improvement_ValidTerrains", 1,"SELECT T1.rowid from Improvement_ValidTerrains as T1 inner join Terrains as T2 on T2.TerrainType = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Terrains", "StartBiasTerrainCollection", "StartBiasTerrains", 1,"SELECT T1.rowid from StartBiasTerrains as T1 inner join Terrains as T2 on T2.TerrainType = T1.TerrainType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Terrains", "TerrainClasses", "TerrainClasses", 1,"SELECT T1.rowid from TerrainClasses as T1 inner join TerrainClass_Terrains as T2 on T2.TerrainClassType = T1.TerrainClassType inner join Terrains as T3 on T3.TerrainType = T2.TerrainType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Terrains", "ValidResources", "Resources", 1,"SELECT T1.rowid from Resources as T1 inner join Resource_ValidTerrains as T2 on T2.ResourceType = T1.ResourceType inner join Terrains as T3 on T3.TerrainType = T2.TerrainType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Terrain_YieldChanges", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Terrain_YieldChanges as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TerrainClasses", "Terrains", "Terrains", 1,"SELECT T1.rowid from Terrains as T1 inner join TerrainClass_Terrains as T2 on T2.TerrainType = T1.TerrainType inner join TerrainClasses as T3 on T3.TerrainClassType = T2.TerrainClassType where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Traits", "ModifierCollection", "TraitModifiers", 1,"SELECT T1.rowid from TraitModifiers as T1 inner join Traits as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TriggeredBehaviorTrees", "EventReference", "AiEvents", 0,"SELECT T1.rowid from AiEvents as T1 inner join TriggeredBehaviorTrees as T2 on T2.AIEvent = T1.EventType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TriggeredBehaviorTrees", "TreeReference", "BehaviorTrees", 0,"SELECT T1.rowid from BehaviorTrees as T1 inner join TriggeredBehaviorTrees as T2 on T2.TreeName = T1.TreeName where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TurnPhases", "ActiveSegment", "TurnSegments", 0,"SELECT T1.rowid from TurnSegments as T1 inner join TurnPhases as T2 on T2.ActiveSegmentType = T1.TurnSegmentType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("TurnPhases", "InactiveSegment", "TurnSegments", 0,"SELECT T1.rowid from TurnSegments as T1 inner join TurnPhases as T2 on T2.InactiveSegmentType = T1.TurnSegmentType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "AiInfoCollection", "UnitAiInfos", 1,"SELECT T1.rowid from UnitAiInfos as T1 inner join Units as T2 on T2.UnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "BaseUnitCollection", "UnitUpgrades", 1,"SELECT T1.rowid from UnitUpgrades as T1 inner join Units as T2 on T2.UnitType = T1.UpgradeUnit where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "BonusMinorStartingUnitCollection", "BonusMinorStartingUnits", 1,"SELECT T1.rowid from BonusMinorStartingUnits as T1 inner join Units as T2 on T2.UnitType = T1.Unit where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "CaptureCollection", "UnitCaptures", 1,"SELECT T1.rowid from UnitCaptures as T1 inner join Units as T2 on T2.UnitType = T1.CapturedUnitType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "MajorStartingUnitCollection", "MajorStartingUnits", 1,"SELECT T1.rowid from MajorStartingUnits as T1 inner join Units as T2 on T2.UnitType = T1.Unit where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "MandatoryObsoleteCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Units as T2 on T2.MandatoryObsoleteCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "MandatoryObsoleteTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Units as T2 on T2.MandatoryObsoleteTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "ObsoleteCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Units as T2 on T2.ObsoleteCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "ObsoleteTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Units as T2 on T2.ObsoleteTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "PrereqBuildingCollection", "Buildings", 1,"SELECT T1.rowid from Buildings as T1 inner join Unit_BuildingPrereqs as T2 on T2.PrereqBuilding = T1.BuildingType inner join Units as T3 on T3.UnitType = T2.Unit where T3.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join Units as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "PrereqDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join Units as T2 on T2.PrereqDistrict = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join Units as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "PromotionClassReference", "UnitPromotionClasses", 0,"SELECT T1.rowid from UnitPromotionClasses as T1 inner join Units as T2 on T2.PromotionClass = T1.PromotionClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "PseudoYieldReference", "PseudoYields", 0,"SELECT T1.rowid from PseudoYields as T1 inner join Units as T2 on T2.PseudoYieldType = T1.PseudoYieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "ReplacedByCollection", "UnitReplaces", 1,"SELECT T1.rowid from UnitReplaces as T1 inner join Units as T2 on T2.UnitType = T1.ReplacesUnitType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "ReplacesCollection", "UnitReplaces", 1,"SELECT T1.rowid from UnitReplaces as T1 inner join Units as T2 on T2.UnitType = T1.CivUniqueUnitType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "StrategicResourceReference", "Resources", 0,"SELECT T1.rowid from Resources as T1 inner join Units as T2 on T2.StrategicResource = T1.ResourceType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "TraitReference", "Traits", 0,"SELECT T1.rowid from Traits as T1 inner join Units as T2 on T2.TraitType = T1.TraitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "UpgradeUnitCollection", "UnitUpgrades", 1,"SELECT T1.rowid from UnitUpgrades as T1 inner join Units as T2 on T2.UnitType = T1.Unit where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Units", "YieldReference", "Yields", 0,"SELECT T1.rowid from Yields as T1 inner join Units as T2 on T2.PurchaseYield = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Unit_BuildingPrereqs", "PrereqBuildingReference", "Buildings", 0,"SELECT T1.rowid from Buildings as T1 inner join Unit_BuildingPrereqs as T2 on T2.PrereqBuilding = T1.BuildingType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Unit_BuildingPrereqs", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join Unit_BuildingPrereqs as T2 on T2.Unit = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitAbilities", "UnitAbilityModifierCollection", "UnitAbilityModifiers", 1,"SELECT T1.rowid from UnitAbilityModifiers as T1 inner join UnitAbilities as T2 on T2.UnitAbilityType = T1.UnitAbilityType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitAiInfos", "UnitAiTypeReference", "UnitAiTypes", 0,"SELECT T1.rowid from UnitAiTypes as T1 inner join UnitAiInfos as T2 on T2.AiType = T1.AiType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitCaptures", "BecomeUnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join UnitCaptures as T2 on T2.BecomesUnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitCommands", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join UnitCommands as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitCommands", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join UnitCommands as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitOperations", "PrereqCivicReference", "Civics", 0,"SELECT T1.rowid from Civics as T1 inner join UnitOperations as T2 on T2.PrereqCivic = T1.CivicType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitOperations", "PrereqTechReference", "Technologies", 0,"SELECT T1.rowid from Technologies as T1 inner join UnitOperations as T2 on T2.PrereqTech = T1.TechnologyType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitOperations", "TargetDistrictReference", "Districts", 0,"SELECT T1.rowid from Districts as T1 inner join UnitOperations as T2 on T2.TargetDistrict = T1.DistrictType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitPromotions", "PrereqUnitPromotionCollection", "UnitPromotionPrereqs", 1,"SELECT T1.rowid from UnitPromotionPrereqs as T1 inner join UnitPromotions as T2 on T2.UnitPromotionType = T1.UnitPromotion where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitPromotions", "PromotionClassReference", "UnitPromotionClasses", 0,"SELECT T1.rowid from UnitPromotionClasses as T1 inner join UnitPromotions as T2 on T2.PromotionClass = T1.PromotionClassType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitPromotionClasses", "PromotionCollection", "UnitPromotions", 1,"SELECT T1.rowid from UnitPromotions as T1 inner join UnitPromotionClasses as T2 on T2.PromotionClassType = T1.PromotionClass where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitPromotionClasses", "UnitCollection", "Units", 1,"SELECT T1.rowid from Units as T1 inner join UnitPromotionClasses as T2 on T2.PromotionClassType = T1.PromotionClass where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitPromotionPrereqs", "PrereqUnitPromotionReference", "UnitPromotions", 0,"SELECT T1.rowid from UnitPromotions as T1 inner join UnitPromotionPrereqs as T2 on T2.PrereqUnitPromotion = T1.UnitPromotionType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitPromotionPrereqs", "UnitPromotionReference", "UnitPromotions", 0,"SELECT T1.rowid from UnitPromotions as T1 inner join UnitPromotionPrereqs as T2 on T2.UnitPromotion = T1.UnitPromotionType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitReplaces", "BaseUnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join UnitReplaces as T2 on T2.ReplacesUnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitReplaces", "ReplacementUnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join UnitReplaces as T2 on T2.CivUniqueUnitType = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitUpgrades", "UnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join UnitUpgrades as T2 on T2.Unit = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("UnitUpgrades", "UpgradeUnitReference", "Units", 0,"SELECT T1.rowid from Units as T1 inner join UnitUpgrades as T2 on T2.UpgradeUnit = T1.UnitType where T2.rowid = ? ORDER BY T1.rowid ASC LIMIT 1");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Yields", "FeatureChange_Refs", "Feature_YieldChanges", 1,"SELECT T1.rowid from Feature_YieldChanges as T1 inner join Yields as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Yields", "ImprovementChange_Refs", "Improvement_BonusYieldChanges", 1,"SELECT T1.rowid from Improvement_BonusYieldChanges as T1 inner join Yields as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Yields", "ResourceChange_Refs", "Resource_YieldChanges", 1,"SELECT T1.rowid from Resource_YieldChanges as T1 inner join Yields as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC");
INSERT INTO NavigationProperties("BaseTable", "PropertyName", "TargetTable", "IsCollection", "Query") VALUES("Yields", "TerrainChange_Refs", "Terrain_YieldChanges", 1,"SELECT T1.rowid from Terrain_YieldChanges as T1 inner join Yields as T2 on T2.YieldType = T1.YieldType where T2.rowid = ? ORDER BY T1.rowid ASC");
