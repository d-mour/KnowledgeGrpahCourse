----------------------------
-- Civ 6 Enumerated Types --
----------------------------
--
-- PLOT_TYPE
--
-- Civ 4 and 5 had separate types for Plots (water, hills, land, mountain) and Terrain (grassland, plains, tundra).  But once map generation was complete and the game
-- commenced there was no longer a need for the distinction between the two.  For Civ 6 we are going to still generate the map in these two passes.  However inside the
-- game we will store the data as a single type (Terrain).  We therefore need a new intermediate data type (PLOT_TYPE) just for map generation.  This data is stored using
-- the enumeration below
function GetGameInfoIndex(table_name, type_name) 
	local index;
	local table = GameInfo[table_name];
	if(table) then
		local t = table[type_name];
		if(t) then
			index = t.Index;
		end
	end

	return index;
end

-- These are internal to the map generator code, it is ok they are hard-coded.
g_PLOT_TYPE_NONE		= -1;
g_PLOT_TYPE_MOUNTAIN	= 0;
g_PLOT_TYPE_HILLS		= 1;
g_PLOT_TYPE_LAND		= 2;
g_PLOT_TYPE_OCEAN		= 3;

-- These come from the database.  Get the runtime index values.
g_TERRAIN_TYPE_NONE					= -1;
g_TERRAIN_TYPE_GRASS				= GetGameInfoIndex("Terrains", "TERRAIN_GRASS");
g_TERRAIN_TYPE_GRASS_HILLS			= GetGameInfoIndex("Terrains", "TERRAIN_GRASS_HILLS");
g_TERRAIN_TYPE_GRASS_MOUNTAIN		= GetGameInfoIndex("Terrains", "TERRAIN_GRASS_MOUNTAIN");
g_TERRAIN_TYPE_PLAINS				= GetGameInfoIndex("Terrains", "TERRAIN_PLAINS");
g_TERRAIN_TYPE_PLAINS_HILLS			= GetGameInfoIndex("Terrains", "TERRAIN_PLAINS_HILLS");
g_TERRAIN_TYPE_PLAINS_MOUNTAIN		= GetGameInfoIndex("Terrains", "TERRAIN_PLAINS_MOUNTAIN");
g_TERRAIN_TYPE_DESERT				= GetGameInfoIndex("Terrains", "TERRAIN_DESERT");
g_TERRAIN_TYPE_DESERT_HILLS			= GetGameInfoIndex("Terrains", "TERRAIN_DESERT_HILLS");
g_TERRAIN_TYPE_DESERT_MOUNTAIN		= GetGameInfoIndex("Terrains", "TERRAIN_DESERT_MOUNTAIN");
g_TERRAIN_TYPE_TUNDRA				= GetGameInfoIndex("Terrains", "TERRAIN_TUNDRA");
g_TERRAIN_TYPE_TUNDRA_HILLS			= GetGameInfoIndex("Terrains", "TERRAIN_TUNDRA_HILLS");
g_TERRAIN_TYPE_TUNDRA_MOUNTAIN		= GetGameInfoIndex("Terrains", "TERRAIN_TUNDRA_MOUNTAIN");
g_TERRAIN_TYPE_SNOW					= GetGameInfoIndex("Terrains", "TERRAIN_SNOW");
g_TERRAIN_TYPE_SNOW_HILLS			= GetGameInfoIndex("Terrains", "TERRAIN_SNOW_HILLS");
g_TERRAIN_TYPE_SNOW_MOUNTAIN		= GetGameInfoIndex("Terrains", "TERRAIN_SNOW_MOUNTAIN");
g_TERRAIN_TYPE_COAST				= GetGameInfoIndex("Terrains", "TERRAIN_COAST");
g_TERRAIN_TYPE_OCEAN				= GetGameInfoIndex("Terrains", "TERRAIN_OCEAN");

-- We are stil going to make an assumption about the ordering if the TerrainTypes, relative to the 'base' type.  
-- This may change, probably to a lookup table to avoid database ordering dependencies.
g_TERRAIN_BASE_TO_HILLS_DELTA		= 1;
g_TERRAIN_BASE_TO_MOUNTAIN_DELTA	= 2;

g_FEATURE_NONE						= -1;
g_FEATURE_FLOODPLAINS				= GetGameInfoIndex("Features", "FEATURE_FLOODPLAINS");
g_FEATURE_ICE						= GetGameInfoIndex("Features", "FEATURE_ICE");
g_FEATURE_JUNGLE					= GetGameInfoIndex("Features", "FEATURE_JUNGLE");
g_FEATURE_FOREST					= GetGameInfoIndex("Features", "FEATURE_FOREST");
g_FEATURE_OASIS						= GetGameInfoIndex("Features", "FEATURE_OASIS");
g_FEATURE_MARSH						= GetGameInfoIndex("Features", "FEATURE_MARSH");

g_FEATURE_BARRIER_REEF				= GetGameInfoIndex("Features", "FEATURE_BARRIER_REEF");
g_FEATURE_CLIFFS_DOVER				= GetGameInfoIndex("Features", "FEATURE_CLIFFS_DOVER");
g_FEATURE_CRATER_LAKE				= GetGameInfoIndex("Features", "FEATURE_CRATER_LAKE");
g_FEATURE_DEAD_SEA					= GetGameInfoIndex("Features", "FEATURE_DEAD_SEA");
g_FEATURE_EVEREST					= GetGameInfoIndex("Features", "FEATURE_EVEREST");
g_FEATURE_GALAPAGOS					= GetGameInfoIndex("Features", "FEATURE_GALAPAGOS");
g_FEATURE_KILIMANJARO				= GetGameInfoIndex("Features", "FEATURE_KILIMANJARO");
g_FEATURE_PANTANAL					= GetGameInfoIndex("Features", "FEATURE_PANTANAL");
g_FEATURE_PIOPIOTAHI				= GetGameInfoIndex("Features", "FEATURE_PIOPIOTAHI");
g_FEATURE_TORRES_DEL_PAINE			= GetGameInfoIndex("Features", "FEATURE_TORRES_DEL_PAINE");
g_FEATURE_TSINGY					= GetGameInfoIndex("Features", "FEATURE_TSINGY");
g_FEATURE_YOSEMITE					= GetGameInfoIndex("Features", "FEATURE_YOSEMITE");

g_YIELD_FOOD						= GetGameInfoIndex("Yields", "YIELD_FOOD");
g_YIELD_PRODUCTION					= GetGameInfoIndex("Yields", "YIELD_PRODUCTION");
g_YIELD_GOLD						= GetGameInfoIndex("Yields", "YIELD_GOLD");
g_YIELD_SCIENCE						= GetGameInfoIndex("Yields", "YIELD_SCIENCE");
g_YIELD_CULTURE						= GetGameInfoIndex("Yields", "YIELD_CULTURE");
g_YIELD_FAITH						= GetGameInfoIndex("Yields", "YIELD_FAITH");

DirectionTypes = {
		DIRECTION_NORTHEAST = 0,
		DIRECTION_EAST = 1,
		DIRECTION_SOUTHEAST = 2,
		DIRECTION_SOUTHWEST = 3,
		DIRECTION_WEST= 4,
		DIRECTION_NORTHWEST = 5,
		NUM_DIRECTION_TYPES = 6,
};

