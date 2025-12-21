------------------------------------------------------------------------------
--	FILE:	 WBImport.lua
--	AUTHOR:  
--	PURPOSE: World Builder map import helper
------------------------------------------------------------------------------
--	Copyright (c) 2018 Firaxis Games, Inc. All rights reserved.
------------------------------------------------------------------------------

include "MapEnums"
include "MapUtilities"

-- Input a Hash; Export width, height, and wrapX
function GetMapInitData(MapSize)
	local Width: number, Height: number = WorldBuilder.MapManager():GetDimensionsFromTiled();
	local WrapX = true;

	return {Width = Width, Height = Height, WrapX = WrapX,}
end

-------------------------------------------------------------------------------
function GenerateMap()
    WorldBuilder.MapManager():LoadPlotsFromTiled();

	AreaBuilder.Recalculate();
-- this hangs on some test imported maps
--	TerrainBuilder.AnalyzeChokepoints();
end

