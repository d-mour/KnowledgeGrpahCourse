------------------------------------------------------------------------------
--	FILE:	 Pangaea.lua
--	AUTHOR:  
--	PURPOSE: Base game script - Simulates a Pan-Earth Supercontinent.
------------------------------------------------------------------------------
--	Copyright (c) 2014 Firaxis Games, Inc. All rights reserved.
------------------------------------------------------------------------------

include "MapEnums"
include "MapUtilities"

local g_iW, g_iH;
local g_iFlags = {};
local g_continentsFrac = nil;
local g_iNumTotalLandTiles = 0; 

------------------------------------------------------------------------------
-- The application side will call GetMapScriptInfo directly to request
-- information about the map script.
------------------------------------------------------------------------------
function GetMapScriptInfo()
	local world_age, temperature, rainfall, sea_level, resources = GetCoreMapOptions()
	return {
		Name = "TXT_KEY_MAP_WORLDBUILDER",
		Description = "TXT_KEY_MAP_WORLDBUILDER_HELP",
		IsAdvancedMap = 0,
		IconIndex = 0,
		SortIndex = 2,
		CustomOptions = {world_age, temperature, rainfall, sea_level, resources},
	};
end

-------------------------------------------------------------------------------
function GenerateMap()
	print("Generating WorldBuilder Map");

	-- Set globals
	g_iW, g_iH = Map.GetGridSize();

	-- Set everything to OCEAN
	for i = 0, (g_iW * g_iH) - 1, 1 do
		local pPlot = Map.GetPlotByIndex(i);
		TerrainBuilder.SetTerrainType(pPlot, g_TERRAIN_TYPE_OCEAN);
	end

	AreaBuilder.Recalculate();
	TerrainBuilder.AnalyzeChokepoints();
	TerrainBuilder.StampContinents();

end

