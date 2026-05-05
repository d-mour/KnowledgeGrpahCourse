------------------------------------------------------------------------------
--	FILE:	 Mirror.lua
--	AUTHOR:  
--	PURPOSE: Base game script - Four-quadrant mirrored map ideal for balanced multiplayer.
------------------------------------------------------------------------------
--	Copyright (c) 2014 Firaxis Games, Inc. All rights reserved.
------------------------------------------------------------------------------

include "MapEnums"
include "MapUtilities"
include "MountainsCliffs"
include "RiversLakes"
include "FeatureGenerator"
include "TerrainGenerator"
include "NaturalWonderGenerator"
include "ResourceGenerator"
include "AssignStartingPlots"

local g_iW, g_iH;
local g_iFlags = {};
local g_continentsFrac = nil;
local g_iNumTotalLandTiles = 0; 
local g_QuadrantRivers = {};
local g_NumNonMirroredRivers = 0;
local g_MinorCandidatesTried = 0;
local g_plotTypes = {};
local g_terrainTypes = {};
-------------------------------------------------------------------------------
function GenerateMap()
	print("Generating Mirror Map");
	local pPlot;

	-- Set globals
	g_iW, g_iH = Map.GetGridSize();
	g_iFlags = TerrainBuilder.GetFractalFlags();
	local temperature = MapConfiguration.GetValue("temperature"); -- Default setting is Temperate.
	if temperature == 4 then
		temperature  =  1 + TerrainBuilder.GetRandomNumber(3, "Random Temperature- Lua");
	end
	
	GeneratePlotTypes();
	g_terrainTypes = GenerateTerrainTypes(g_plotTypes, g_iW, g_iH, g_iFlags, true, temperature);

	for i = 0, (g_iW * g_iH) - 1, 1 do
		pPlot = Map.GetPlotByIndex(i);
		if (g_plotTypes[i] == g_PLOT_TYPE_HILLS) then
			g_terrainTypes[i] = g_terrainTypes[i] + 1;
		end
	end

	local iQuadrantToMirror = ComputeQuadrantToMirror();
	ClearTargetQuadrants(iQuadrantToMirror);
	DoMirroring(iQuadrantToMirror);

	local iNumContinents = #GameInfo.Continents;
	local iContinent1 = TerrainBuilder.GetRandomNumber(iNumContinents, "Mirror - Continent #1");
	local iContinent2 = TerrainBuilder.GetRandomNumber(iNumContinents, "Mirror - Continent #2");
	if (iContinent1 == iContinent2) then
		iContinent2 = iContinent1 + 1;
		if (iContinent2 == iNumContinents) then
			iContinent2 = 0;
		end
	end
	for i = 0, (g_iW * g_iH) - 1, 1 do
		pPlot = Map.GetPlotByIndex(i);
		TerrainBuilder.SetTerrainType(pPlot, g_terrainTypes[i]);
		if (pPlot:GetX() <= (g_iW / 2)) then
			TerrainBuilder.SetContinentType(pPlot, iContinent1);
		else
			TerrainBuilder.SetContinentType(pPlot, iContinent2);
		end
	end

	AreaBuilder.Recalculate();
	TerrainBuilder.AnalyzeChokepoints();
	local biggest_area = Areas.FindBiggestArea(false);
	print("After Adding Hills: ", biggest_area:GetPlotCount());

	-- River generation is affected by plot types, originating from highlands and preferring to traverse lowlands.
	AddMirroredRivers();
	
	-- Lakes would interfere with rivers, causing them to stop and not reach the ocean, if placed any sooner.
	local numLargeLakes = math.ceil(GameInfo.Maps[Map.GetMapSize()].Continents * 1.5);
	AddMirroredLakes(numLargeLakes);

	AddFeatures();

    AddCenteredNaturalWonder();
	
	print("Adding cliffs");
	AddCliffs(g_plotTypes, g_terrainTypes);
	
	resourcesConfig = MapConfiguration.GetValue("resources");
	local startConfig = MapConfiguration.GetValue("start");-- Get the start config
	local args = {
		iWaterLux = 2,
		resources = resourcesConfig,
		START_CONFIG = startConfig,
	}
	local resGen = ResourceGenerator.Create(args);

	print("Creating start plot database.");
	-- START_MIN_Y and START_MAX_Y is the percent of the map ignored for major civs' starting positions.
	local args = {
		MIN_MAJOR_CIV_FERTILITY = 300,
		MIN_MINOR_CIV_FERTILITY = 50, 
		MIN_BARBARIAN_FERTILITY = 1,
		START_MIN_Y = 15,
		START_MAX_Y = 15,
		START_CONFIG = startConfig,
		LAND = true,
		IGNORESTARTBIAS = false,
		STARTALLONLAND = true,
	};

	if (startConfig == 1) then
		args.IGNORESTARTBIAS = true;
	end	
	local start_plot_database = AssignStartingPlots.Create(args);
	if (startConfig == 1) then
		MirrorStartPositions(start_plot_database);
		RedoMinorStartPositions(start_plot_database);
	end

	local GoodyGen = AddGoodies(g_iW, g_iH);
end

-------------------------------------------------------------------------------
function GeneratePlotTypes()
	print("Generating Plot Types");

	local sea_level_low = 53;
	local sea_level_normal = 58;
	local sea_level_high = 63;
	local world_age_new = 5;
	local world_age_normal = 3;
	local world_age_old = 2;

	local grain_amount = 3;
	local adjust_plates = 1.3;
	local shift_plot_types = true;
	local tectonic_islands = true;
	local hills_ridge_flags = g_iFlags;
	local peaks_ridge_flags = g_iFlags;
	local has_center_rift = false;
	
	--	local world_age
	local world_age = MapConfiguration.GetValue("world_age");
	if (world_age == 1) then
		world_age = world_age_new;
	elseif (world_age == 2) then
		world_age = world_age_normal;
	elseif (world_age == 3) then
		world_age = world_age_old;
	else
		world_age = 2 + TerrainBuilder.GetRandomNumber(4, "Random World Age - Lua");
	end

	--	local sea_level
    local sea_level = MapConfiguration.GetValue("sea_level");
	local water_percent;
	if sea_level == 1 then -- Low Sea Level
		water_percent = sea_level_low
	elseif sea_level == 2 then -- Normal Sea Level
		water_percent =sea_level_normal
	elseif sea_level == 3 then -- High Sea Level
		water_percent = sea_level_high
	else
		water_percent = TerrainBuilder.GetRandomNumber(sea_level_high - sea_level_low, "Random Sea Level - Lua") + sea_level_low + 1; 
	end

	-- Generate continental fractal layer and examine the largest landmass. Reject
	-- the result until the largest landmass occupies 84% or more of the total land.
	local done = false;
	local iAttempts = 0;
	local iWaterThreshold, biggest_area, iNumBiggestAreaTiles, iBiggestID;
	while done == false do
		local grain_dice = TerrainBuilder.GetRandomNumber(7, "Continental Grain roll - LUA Pangea");
		if grain_dice < 4 then
			grain_dice = 1;
		else
			grain_dice = 2;
		end
		local rift_dice = TerrainBuilder.GetRandomNumber(3, "Rift Grain roll - LUA Pangea");
		if rift_dice < 1 then
			rift_dice = -1;
		end
		
		g_continentsFrac = nil;
		InitFractal{continent_grain = grain_dice, rift_grain = rift_dice};
		iWaterThreshold = g_continentsFrac:GetHeight(water_percent);
		
		g_iNumTotalLandTiles = 0;
		for x = 0, g_iW - 1 do
			for y = 0, g_iH - 1 do
				local i = y * g_iW + x;
				local val = g_continentsFrac:GetHeight(x, y);
				local pPlot = Map.GetPlotByIndex(i);
				if(val <= iWaterThreshold) then
					g_plotTypes[i] = g_PLOT_TYPE_OCEAN;
					TerrainBuilder.SetTerrainType(pPlot, g_TERRAIN_TYPE_OCEAN);  -- temporary setting so can calculate areas
				else
					g_plotTypes[i] = g_PLOT_TYPE_LAND;
					TerrainBuilder.SetTerrainType(pPlot, g_TERRAIN_TYPE_DESERT);  -- temporary setting so can calculate areas
					g_iNumTotalLandTiles = g_iNumTotalLandTiles + 1;
				end
			end
		end
		
		AreaBuilder.Recalculate();
		local biggest_area = Areas.FindBiggestArea(false);
		iNumBiggestAreaTiles = biggest_area:GetPlotCount();
		
		-- Now test the biggest landmass to see if it is large enough.
		if iNumBiggestAreaTiles >= g_iNumTotalLandTiles * 0.84 then
			done = true;
			iBiggestID = biggest_area:GetID();
		end
		iAttempts = iAttempts + 1;
		
		-- Printout for debug use only
		-- print("-"); print("--- Pangea landmass generation, Attempt#", iAttempts, "---");
		-- print("- This attempt successful: ", done);
		-- print("- Total Land Plots in world:", g_iNumTotalLandTiles);
		-- print("- Land Plots belonging to biggest landmass:", iNumBiggestAreaTiles);
		-- print("- Percentage of land belonging to Pangaea: ", 100 * iNumBiggestAreaTiles / g_iNumTotalLandTiles);
		-- print("- Continent Grain for this attempt: ", grain_dice);
		-- print("- Rift Grain for this attempt: ", rift_dice);
		-- print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -");
		-- print(".");
	end
	
	local args = {};
	args.world_age = world_age;
	args.iW = g_iW;
	args.iH = g_iH
	args.iFlags = g_iFlags;
	args.blendRidge = 10;
	args.blendFract = 1;
	args.extra_mountains = 4;
	g_plotTypes = ApplyTectonics(args, g_plotTypes);
	
	-- Now shift everything toward one of the poles, to reduce how much jungles tend to dominate this script.
	local shift_dice = TerrainBuilder.GetRandomNumber(2, "Shift direction - LUA Pangaea");
	local iStartRow, iNumRowsToShift;
	local bFoundPangaea, bDoShift = false, false;
	if shift_dice == 1 then
		-- Shift North
		for y = g_iH - 2, 1, -1 do
			for x = 0, g_iW - 1 do
				local i = y * g_iW + x;
				if g_plotTypes[i] == g_PLOT_TYPE_HILLS or g_plotTypes[i] == g_PLOT_TYPE_LAND then
					local plot = Map.GetPlot(x, y);
					local iAreaID = plot:GetArea();
					if iAreaID == iBiggestID then
						bFoundPangaea = true;
						iStartRow = y + 1;
						if iStartRow < iNumPlotsY - 4 then -- Enough rows of water space to do a shift.
							bDoShift = true;
						end
						break
					end
				end
			end
			-- Check to see if we've found the Pangaea.
			if bFoundPangaea == true then
				break
			end
		end
	else
		-- Shift South
		for y = 1, g_iH - 2 do
			for x = 0, g_iW- 1 do
				local i = y * g_iW + x;
				if g_plotTypes[i] == g_PLOT_TYPE_HILLS or g_plotTypes[i] == g_PLOT_TYPE_LAND then
					local plot = Map.GetPlot(x, y);
					local iAreaID = plot:GetArea();
					if iAreaID == iBiggestID then
						bFoundPangaea = true;
						iStartRow = y - 1;
						if iStartRow > 3 then -- Enough rows of water space to do a shift.
							bDoShift = true;
						end
						break
					end
				end
			end
			-- Check to see if we've found the Pangaea.
			if bFoundPangaea == true then
				break
			end
		end
	end
	if bDoShift == true then
		if shift_dice == 1 then -- Shift North
			local iRowsDifference = g_iH - iStartRow - 2;
			local iRowsInPlay = math.floor(iRowsDifference * 0.7);
			local iRowsBase = math.ceil(iRowsDifference * 0.3);
			local rows_dice = TerrainBuilder.GetRandomNumber(iRowsInPlay, "Number of Rows to Shift - LUA Pangaea");
			local iNumRows = math.min(iRowsDifference - 1, iRowsBase + rows_dice);
			local iNumEvenRows = 2 * math.floor(iNumRows / 2); -- MUST be an even number or we risk breaking a 1-tile isthmus and splitting the Pangaea.
			local iNumRowsToShift = math.max(2, iNumEvenRows);
			--print("-"); print("Shifting lands northward by this many plots: ", iNumRowsToShift); print("-");
			-- Process from top down.
			for y = (g_iH - 1) - iNumRowsToShift, 0, -1 do
				for x = 0, g_iW - 1 do
					local sourcePlotIndex = y * g_iW + x + 1;
					local destPlotIndex = (y + iNumRowsToShift) * g_iW + x + 1;
					g_plotTypes[destPlotIndex] = g_plotTypes[sourcePlotIndex]
				end
			end
			for y = 0, iNumRowsToShift - 1 do
				for x = 0, g_iW - 1 do
					local i = y * g_iW + x + 1;
					g_plotTypes[i] = g_PLOT_TYPE_OCEAN;
				end
			end
		else -- Shift South
			local iRowsDifference = iStartRow - 1;
			local iRowsInPlay = math.floor(iRowsDifference * 0.7);
			local iRowsBase = math.ceil(iRowsDifference * 0.3);
			local rows_dice = TerrainBuilder.GetRandomNumber(iRowsInPlay, "Number of Rows to Shift - LUA Pangaea");
			local iNumRows = math.min(iRowsDifference - 1, iRowsBase + rows_dice);
			local iNumEvenRows = 2 * math.floor(iNumRows / 2); -- MUST be an even number or we risk breaking a 1-tile isthmus and splitting the Pangaea.
			local iNumRowsToShift = math.max(2, iNumEvenRows);
			--print("-"); print("Shifting lands southward by this many plots: ", iNumRowsToShift); print("-");
			-- Process from bottom up.
			for y = 0, (g_iH - 1) - iNumRowsToShift do
				for x = 0, g_iW - 1 do
					local sourcePlotIndex = (y + iNumRowsToShift) * g_iW + x + 1;
					local destPlotIndex = y * g_iW + x + 1;
					g_plotTypes[destPlotIndex] = g_plotTypes[sourcePlotIndex]
				end
			end
			for y = g_iH - iNumRowsToShift, g_iH - 1 do
				for x = 0, g_iW - 1 do
					local i = y * g_iW + x + 1;
					g_plotTypes[i] = g_PLOT_TYPE_OCEAN;
				end
			end
		end
	end
end

function InitFractal(args)

	if(args == nil) then args = {}; end

	local continent_grain = args.continent_grain or 2;
	local rift_grain = args.rift_grain or -1; -- Default no rifts. Set grain to between 1 and 3 to add rifts. - Bob
	local invert_heights = args.invert_heights or false;
	local polar = args.polar or true;
	local ridge_flags = args.ridge_flags or g_iFlags;

	local fracFlags = {};
	
	if(invert_heights) then
		fracFlags.FRAC_INVERT_HEIGHTS = true;
	end
	
	if(polar) then
		fracFlags.FRAC_POLAR = true;
	end
	
	if(rift_grain > 0 and rift_grain < 4) then
		local riftsFrac = Fractal.Create(g_iW, g_iH, rift_grain, {}, 6, 5);
		g_continentsFrac = Fractal.CreateRifts(g_iW, g_iH, continent_grain, fracFlags, riftsFrac, 6, 5);
	else
		g_continentsFrac = Fractal.Create(g_iW, g_iH, continent_grain, fracFlags, 6, 5);	
	end

	-- Use Brian's tectonics method to weave ridgelines in to the continental fractal.
	-- Without fractal variation, the tectonics come out too regular.
	--
	--[[ "The principle of the RidgeBuilder code is a modified Voronoi diagram. I 
	added some minor randomness and the slope might be a little tricky. It was 
	intended as a 'whole world' modifier to the fractal class. You can modify 
	the number of plates, but that is about it." ]]-- Brian Wade - May 23, 2009
	--
	local MapSizeTypes = {};
	for row in GameInfo.Maps() do
		MapSizeTypes[row.MapSizeType] = row.PlateValue;
	end
	local sizekey = Map.GetMapSize();

	local numPlates = MapSizeTypes[sizekey] or 4

	-- Blend a bit of ridge into the fractal.
	-- This will do things like roughen the coastlines and build inland seas. - Brian

	g_continentsFrac:BuildRidges(numPlates, {}, 1, 2);
end

function AddFeatures()
	print("Adding Features");

	-- Get Rainfall setting input by user.
	local rainfall = MapConfiguration.GetValue("rainfall");
	if rainfall == 4 then
		rainfall = 1 + TerrainBuilder.GetRandomNumber(3, "Random Rainfall - Lua");
	end
	
	local args = {rainfall = rainfall}
	local featuregen = FeatureGenerator.Create(args);

	featuregen:AddFeatures();
end

function ComputeQuadrantToMirror()
	print("Calling ComputeQuadrantToMirror");
	local iReturnValue = 0;

	local iSWcount = 0;
	for y = 0, (g_iH/2 - 1) do
		for x = 0, (g_iW/2 - 1) do
			local i = y * g_iW + x;
			if (g_plotTypes[i] ~= g_PLOT_TYPE_OCEAN) then
				iSWcount = iSWcount + 1;
			end
		end
	end
	local iSEcount = 0;
	for y = 0, (g_iH/2 - 1) do
		for x = g_iW/2, (g_iW - 1) do
			local i = y * g_iW + x;
			if (g_plotTypes[i] ~= g_PLOT_TYPE_OCEAN) then
				iSEcount = iSEcount + 1;
			end
		end
	end
	local iNWcount = 0;
	for y = g_iH/2, (g_iH - 1) do
		for x = 0, (g_iW/2 - 1) do
			local i = y * g_iW + x;
			if (g_plotTypes[i] ~= g_PLOT_TYPE_OCEAN) then
				iNWcount = iNWcount + 1;
			end
		end
	end
	local iNEcount = 0;
	for y = g_iH/2, (g_iH - 1) do
		for x = g_iW/2, (g_iW - 1) do
			local i = y * g_iW + x;
			if (g_plotTypes[i] ~= g_PLOT_TYPE_OCEAN) then
				iNEcount = iNEcount + 1;
			end
		end
	end
	print ("iSWcount: " .. tostring(iSWcount));
	print ("iSEcount: " .. tostring(iSEcount));
	print ("iNWcount: " .. tostring(iNWcount));
	print ("iNEcount: " .. tostring(iNEcount));

	local allQuadrants = {};
	local quadrantData = {};
	quadrantData.Count = iSWcount;
	quadrantData.ReturnValue = 0;
	table.insert(allQuadrants, quadrantData);

	local quadrantData = {};
	quadrantData.Count = iSEcount;
	quadrantData.ReturnValue = 1;
	table.insert(allQuadrants, quadrantData);

	local quadrantData = {};
	quadrantData.Count = iNWcount;
	quadrantData.ReturnValue = 2;
	table.insert(allQuadrants, quadrantData);

	local quadrantData = {};
	quadrantData.Count = iNEcount;
	quadrantData.ReturnValue = 3;
	table.insert(allQuadrants, quadrantData);
	table.sort (allQuadrants, function(a, b) return a.Count > b.Count; end);

	-- The second largest landmass seems best
	iReturnValue = allQuadrants[2].ReturnValue;
	print ("iReturnValue: " .. tostring(iReturnValue));

	return iReturnValue;
end

function ClearTargetQuadrants(iQuadrantToMirror)

	print ("Clearing all but quadrant: " .. tostring(iQuadrantToMirror));

	if (iQuadrantToMirror ~= 0) then
		ClearOneQuadrant(0, 0);
	end
	if (iQuadrantToMirror ~= 1) then
		ClearOneQuadrant(g_iW/2, 0);
	end
	if (iQuadrantToMirror ~= 2) then
		ClearOneQuadrant(0, g_iH/2);
	end
	if (iQuadrantToMirror ~= 3) then
		ClearOneQuadrant(g_iW/2, g_iH/2);
	end
end

function ClearOneQuadrant(iXOffset, iYOffset)
	for y = iYOffset, (iYOffset + g_iH/2 - 1) do
		for x = iXOffset, (iXOffset + g_iW/2 - 1) do
			local i = y * g_iW + x;
			g_plotTypes[i] = g_PLOT_TYPE_OCEAN;
		end
	end
end

function DoMirroring(iQuadrantToMirror)

	print ("Mirroring quadrant: " .. tostring(iQuadrantToMirror));

	local iXOffset = 0;
	local iYOffset = 0;

	if (iQuadrantToMirror == 0) then
		iXOffset = 0;
		iYOffset = 0;
	elseif (iQuadrantToMirror == 1) then
		iXOffset = g_iW/2;
	elseif (iQuadrantToMirror == 2) then
		iYOffset = g_iH/2;
	else
		iXOffset = g_iW/2;
		iYOffset = g_iH/2;
	end

	for y = iYOffset, (iYOffset + g_iH/2 - 1) do
		for x = iXOffset, (iXOffset + g_iW/2 - 1) do
			local originalPlotType = g_plotTypes[y * g_iW + x];
			local originalTerrain = g_terrainTypes[y * g_iW + x];

			local targetPlot1 = y * g_iW + (g_iW - x - 1);              -- Flip x only
			local targetPlot2 = (g_iH - y - 1) * g_iW + x;              -- Flip y only
			local targetPlot3 = (g_iH - y - 1) * g_iW + (g_iW - x - 1); -- Flip both

			g_plotTypes[targetPlot1] = originalPlotType;
			g_plotTypes[targetPlot2] = originalPlotType;
			g_plotTypes[targetPlot3] = originalPlotType;
			g_terrainTypes[targetPlot1] = originalTerrain;
			g_terrainTypes[targetPlot2] = originalTerrain;
			g_terrainTypes[targetPlot3] = originalTerrain;
		end
	end

	for iY = 0, g_iH - 1 do
		for iX = 0, g_iW - 1 do
			local index = (iY * g_iW) + iX;
			if (g_plotTypes[index] == g_PLOT_TYPE_OCEAN and g_terrainTypes[index] ~= g_TERRAIN_TYPE_COAST) then
				if (IsAdjacentToLand(g_plotTypes, iX, iY)) then
					print ("Converting Index to Coast: " .. tostring(index));
					g_terrainTypes[index] = g_TERRAIN_TYPE_COAST;
				end
			end
		end
	end
end

function AddMirroredRivers()

	print("Map Generation - Adding Mirrored Rivers");
	
	GenerateQuadrantRivers(0);
	print ("Quadrant 0 River Edges: " .. tostring(#g_QuadrantRivers));

	GenerateQuadrantRivers(1);
	print ("Quadrants 0 and 1 River Edges: " .. tostring(#g_QuadrantRivers));

	TransposeRivers(0, 3);
	TransposeRivers(1, 2);

end

function GenerateQuadrantRivers(iQuadrant)

	local riverSourceRangeDefault = 2;
	local seaWaterRangeDefault = 3;
	local plotsPerRiverEdge = 3;
	local iXOffset = iQuadrant * (g_iW / 2);
	
	local passConditions = {
		function(plot)
			return (plot:IsHills() or plot:IsMountain());
		end,
		
		function(plot)
			return (not plot:IsCoastalLand());
		end,
		
		function(plot)
			local area = plot:GetArea();
			return (plot:IsHills() or plot:IsMountain()) and (#g_QuadrantRivers < ((area:GetPlotCount() / plotsPerRiverEdge) + 1) * (iQuadrant + 1) / 4);
		end,
	}
	
	for iPass, passCondition in ipairs(passConditions) do

		-- print ("----------> iPass: " .. tostring(iPass));
					
		if (iPass <= 2) then
			riverSourceRange = riverSourceRangeDefault;
			seaWaterRange = seaWaterRangeDefault;
		else
			riverSourceRange = (riverSourceRangeDefault / 2);
			seaWaterRange = (seaWaterRangeDefault / 2);
		end
			
		local iW, iH = Map.GetGridSize();

		for y = riverSourceRangeDefault, (g_iH/2 - 1 - riverSourceRangeDefault) do
			for x = iXOffset + riverSourceRangeDefault, iXOffset + (g_iW/2 - 1 - riverSourceRangeDefault) do
				plot = Map.GetPlotByIndex(y * g_iW + x);
				if(not plot:IsWater()) then
					if(passCondition(plot)) then
						if (not Map.FindWater(plot, riverSourceRange, true)) then
							if (not Map.FindWater(plot, seaWaterRange, false)) then
								local inlandCorner = TerrainBuilder.GetInlandCorner(plot);
								if(inlandCorner) then
									if (iQuadrant == 0) then
										DoRiver(inlandCorner, FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST, FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST, nil, iQuadrant);
										g_NumNonMirroredRivers = g_NumNonMirroredRivers + 1;
									else
										DoRiver(inlandCorner, FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST, FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST, nil, iQuadrant);
										g_NumNonMirroredRivers = g_NumNonMirroredRivers + 1;
									end
								end
							end
						end
					end			
				end
			end
		end
	end		
end

nextRiverID = 0;
_rivers = {};
function DoRiver(startPlot, thisFlowDirection, originalFlowDirection, riverID, iQuadrant)
	
	thisFlowDirection = thisFlowDirection or FlowDirectionTypes.NO_FLOWDIRECTION;
	originalFlowDirection = originalFlowDirection or FlowDirectionTypes.NO_FLOWDIRECTION;

	if (riverID == nil) then
		riverID = nextRiverID;
		nextRiverID = nextRiverID + 1;
	end

	local otherRiverID = _rivers[startPlot]
	if (otherRiverID ~= nil and otherRiverID ~= riverID and originalFlowDirection == FlowDirectionTypes.NO_FLOWDIRECTION) then
		return; -- Another river already exists here; can't branch off of an existing river!
	end

	local riverPlot;
	
	local bestFlowDirection = FlowDirectionTypes.NO_FLOWDIRECTION;
	if (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_NORTH) then
	
		riverPlot = startPlot;
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetWOfRiver(riverPlot, true, thisFlowDirection, riverID);
		-- print ("NORTH: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		AddRiverRow (riverID, riverPlot, thisFlowDirection, "WOf", iQuadrant);
		riverPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_NORTHEAST);

		if (riverPlot == nil or riverPlot:IsWater() or riverPlot:IsNEOfRiver() or riverPlot:IsNWOfRiver()) then
			return;
		end

	elseif (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_NORTHEAST) then
	
		riverPlot = startPlot;
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetNWOfRiver(riverPlot, true, thisFlowDirection, riverID);
		AddRiverRow (riverID, riverPlot, thisFlowDirection, "NWOf", iQuadrant);
		-- print ("NE: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		-- riverPlot does not change

		local adjacentPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_EAST);
		if (adjacentPlot == nil or adjacentPlot:IsWater() or riverPlot:IsWOfRiver() or adjacentPlot:IsNEOfRiver()) then
			return;
		end
	
	elseif (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST) then
	
		riverPlot = Map.GetAdjacentPlot(startPlot:GetX(), startPlot:GetY(), DirectionTypes.DIRECTION_EAST);
		if (riverPlot == nil) then
			return;
		end
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetNEOfRiver(riverPlot, true, thisFlowDirection, riverID);
		AddRiverRow (riverID, riverPlot, thisFlowDirection, "NEOf", iQuadrant);
		-- print ("SE: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		-- riverPlot does not change

		local adjacentPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_SOUTHEAST);
		if (adjacentPlot == nil or adjacentPlot:IsWater() or riverPlot:IsNWOfRiver()) then
			return;
		end
		local adjacentPlot2 = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_SOUTHWEST);
		if (adjacentPlot2 == nil or adjacentPlot2:IsWOfRiver()) then
			return;
		end
	
	elseif (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_SOUTH) then
	
		riverPlot = Map.GetAdjacentPlot(startPlot:GetX(), startPlot:GetY(), DirectionTypes.DIRECTION_SOUTHWEST);
		if (riverPlot == nil) then
			return;
		end		
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetWOfRiver(riverPlot, true, thisFlowDirection, riverID);
		AddRiverRow (riverID, riverPlot, thisFlowDirection, "WOf", iQuadrant);
		-- print ("SOUTH: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		-- riverPlot does not change

		local adjacentPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_SOUTHEAST);
		if (adjacentPlot == nil or adjacentPlot:IsWater() or riverPlot:IsNWOfRiver()) then
			return;
		end
		local adjacentPlot2 = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_EAST);
		if (adjacentPlot2 == nil or adjacentPlot2:IsNEOfRiver()) then
			return;
		end
			
	elseif (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST) then

		riverPlot = startPlot;
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetNWOfRiver(riverPlot, true, thisFlowDirection, riverID);
		AddRiverRow (riverID, riverPlot, thisFlowDirection, "NWOf", iQuadrant);
		-- print ("SW: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		-- riverPlot does not change

		local adjacentPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_SOUTHWEST);
		if (adjacentPlot == nil or adjacentPlot:IsWater() or adjacentPlot:IsWOfRiver() or riverPlot:IsNEOfRiver()) then
			return;
		end

	elseif (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_NORTHWEST) then
		
		riverPlot = startPlot;
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetNEOfRiver(riverPlot, true, thisFlowDirection, riverID);
		AddRiverRow (riverID, riverPlot, thisFlowDirection, "NEOf", iQuadrant);
		-- print ("NW: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		riverPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_WEST);

		if (riverPlot == nil or riverPlot:IsWater() or riverPlot:IsNWOfRiver() or riverPlot:IsWOfRiver()) then
			return;
		end

	else
		--error("Illegal direction type"); 
		-- River is starting here, set the direction in the next step
		riverPlot = startPlot;		
	end

	if (riverPlot == nil or riverPlot:IsWater()) then
		-- The river has flowed off the edge of the map or into the ocean. All is well.
		return; 
	end

	-- Storing X,Y positions as locals to prevent redundant function calls.
	local riverPlotX = riverPlot:GetX();
	local riverPlotY = riverPlot:GetY();
	
	-- Table of methods used to determine the adjacent plot.
	local adjacentPlotFunctions = {
		[FlowDirectionTypes.FLOWDIRECTION_NORTH] = function() 
			return Map.GetAdjacentPlot(riverPlotX, riverPlotY, DirectionTypes.DIRECTION_NORTHWEST); 
		end,
		
		[FlowDirectionTypes.FLOWDIRECTION_NORTHEAST] = function() 
			return Map.GetAdjacentPlot(riverPlotX, riverPlotY, DirectionTypes.DIRECTION_NORTHEAST);
		end,
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST] = function() 
			return Map.GetAdjacentPlot(riverPlotX, riverPlotY, DirectionTypes.DIRECTION_EAST);
		end,
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTH] = function() 
			return Map.GetAdjacentPlot(riverPlotX, riverPlotY, DirectionTypes.DIRECTION_SOUTHWEST);
		end,
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST] = function() 
			return Map.GetAdjacentPlot(riverPlotX, riverPlotY, DirectionTypes.DIRECTION_WEST);
		end,
		
		[FlowDirectionTypes.FLOWDIRECTION_NORTHWEST] = function() 
			return Map.GetAdjacentPlot(riverPlotX, riverPlotY, DirectionTypes.DIRECTION_NORTHWEST);
		end	
	}
	
	if(bestFlowDirection == FlowDirectionTypes.NO_FLOWDIRECTION) then

		-- Attempt to calculate the best flow direction.
		local bestValue = math.huge;
		for flowDirection, getAdjacentPlot in pairs(adjacentPlotFunctions) do
			
			if (GetOppositeFlowDirection(flowDirection) ~= originalFlowDirection) then
				
				if (thisFlowDirection == FlowDirectionTypes.NO_FLOWDIRECTION or
					flowDirection == TurnRightFlowDirections[thisFlowDirection] or 
					flowDirection == TurnLeftFlowDirections[thisFlowDirection]) then
				
					local adjacentPlot = getAdjacentPlot();
					
					if (adjacentPlot ~= nil) then
					
						local value = GetRiverValueAtPlot(adjacentPlot, iQuadrant);
						if (flowDirection == originalFlowDirection) then
							value = (value * 11) / 12;
						end
						
						if (value < bestValue) then
							bestValue = value;
							bestFlowDirection = flowDirection;
						end
					end
				end
			end
		end
		
		if(bestFlowDirection == FlowDirectionTypes.NO_FLOWDIRECTION) then
		
			-- Patch river to north edge of map if can't flow off their normally
			if (originalFlowDirection == FlowDirectionTypes.FLOWDIRECTION_NORTHEAST) then
				TerrainBuilder.SetNWOfRiver(riverPlot, true, FlowDirectionTypes.FLOWDIRECTION_NORTHEAST, riverID);
				TerrainBuilder.SetWOfRiver(riverPlot, true, FlowDirectionTypes.FLOWDIRECTION_NORTH, riverID);
				print ("*** NORTH EDGE OF MAP RIVER REPAIR ***");
			end
		end
	end
	
	--Recursively generate river.
	if (bestFlowDirection ~= FlowDirectionTypes.NO_FLOWDIRECTION) then
		if  (originalFlowDirection == FlowDirectionTypes.NO_FLOWDIRECTION) then
			originalFlowDirection = bestFlowDirection;
		end
		
		DoRiver(riverPlot, bestFlowDirection, originalFlowDirection, riverID, iQuadrant);
	end
end

function GetRiverValueAtPlot(plot, iQuadrant)

	local riverSourceRangeDefault = GlobalParameters.RIVER_SOURCE_RANGE_DEFAULT or 4;

	if(plot:IsNWOfCliff() or plot:IsWOfCliff() or plot:IsNEOfCliff()) then
		return -1;
	end

	local sum = GetPlotElevation(plot) * 20;

	local numDirections = DirectionTypes.NUM_DIRECTION_TYPES;
	for direction = 0, numDirections - 1, 1 do

		local adjacentPlot = Map.GetAdjacentPlot(plot:GetX(), plot:GetY(), direction);

		if (adjacentPlot ~= nil) then
			sum = sum + GetPlotElevation(adjacentPlot);

			if(g_TERRAIN_TYPE_DESERT == adjacentPlot:GetTerrainType()) then
				sum = sum + 4;
			end		
		else
			sum = sum + 40;
		end
		
	end

	sum = sum + TerrainBuilder.GetRandomNumber(10, "River Rand");

	if (iQuadrant == 0 and plot:GetX() > (g_iW / 2) - riverSourceRangeDefault) then
		sum = sum + 100 + plot:GetX();
	elseif (iQuadrant == 1 and plot:GetX() < (g_iW / 2) + riverSourceRangeDefault) then
		sum = sum + 100 + g_iW - plot:GetX();
	end
	if (plot:GetY() > (g_iH / 2) - riverSourceRangeDefault) then
		sum = sum + 100 + plot:GetY();
	end

	return sum;
end

function AddRiverRow (riverID, riverPlot, thisFlowDirection, setFcnName, iQuadrant)
	row = {};
	row.RiverID = riverID;
    row.RiverPlot = riverPlot;
	row.FlowDirection = thisFlowDirection;
	row.SetFcnName = setFcnName;
	row.Quadrant= iQuadrant;
	table.insert (g_QuadrantRivers, row);
end

function TransposeRivers (iSourceQuadrant, iTargetQuadrant)

	for i, row in pairs(g_QuadrantRivers) do

		if (row.Quadrant == 0 and iSourceQuadrant == 0 and iTargetQuadrant == 3) then

			local targetPlotIndex = (g_iH - row.RiverPlot:GetY() - 1) * g_iW + (g_iW - row.RiverPlot:GetX() - 1);      
			local targetPlot = Map.GetPlotByIndex(targetPlotIndex);
			if (targetPlot) then

				if (row.SetFcnName == "WOf") then
					local riverPlot = Map.GetAdjacentPlot(targetPlot:GetX(), targetPlot:GetY(), DirectionTypes.DIRECTION_WEST);
					if (riverPlot) then
						TerrainBuilder.SetWOfRiver(riverPlot, true, GetOppositeFlowDirection(row.FlowDirection), row.RiverID + g_NumNonMirroredRivers);
					end

				elseif (row.SetFcnName == "NWOf") then
					local riverPlot = Map.GetAdjacentPlot(targetPlot:GetX(), targetPlot:GetY(), DirectionTypes.DIRECTION_NORTHWEST);
					if (riverPlot) then
						TerrainBuilder.SetNWOfRiver(riverPlot, true, GetOppositeFlowDirection(row.FlowDirection), row.RiverID + g_NumNonMirroredRivers);
					end

				elseif (row.SetFcnName == "NEOf") then
					local riverPlot = Map.GetAdjacentPlot(targetPlot:GetX(), targetPlot:GetY(), DirectionTypes.DIRECTION_NORTHEAST);
					if (riverPlot) then
						TerrainBuilder.SetNEOfRiver(riverPlot, true, GetOppositeFlowDirection(row.FlowDirection), row.RiverID + g_NumNonMirroredRivers);
					end

				end
			end

		elseif (row.Quadrant == 1 and iSourceQuadrant == 1 and iTargetQuadrant == 2) then

			local targetPlotIndex = (g_iH - row.RiverPlot:GetY() - 1) * g_iW + (g_iW - row.RiverPlot:GetX() - 1);      
			local targetPlot = Map.GetPlotByIndex(targetPlotIndex);
			if (targetPlot) then

				if (row.SetFcnName == "WOf") then
					local riverPlot = Map.GetAdjacentPlot(targetPlot:GetX(), targetPlot:GetY(), DirectionTypes.DIRECTION_WEST);
					if (riverPlot) then
						TerrainBuilder.SetWOfRiver(riverPlot, true, GetOppositeFlowDirection(row.FlowDirection), row.RiverID + g_NumNonMirroredRivers);
					end

				elseif (row.SetFcnName == "NWOf") then
					local riverPlot = Map.GetAdjacentPlot(targetPlot:GetX(), targetPlot:GetY(), DirectionTypes.DIRECTION_NORTHWEST);
					if (riverPlot) then
						TerrainBuilder.SetNWOfRiver(riverPlot, true, GetOppositeFlowDirection(row.FlowDirection), row.RiverID + g_NumNonMirroredRivers);
					end

				elseif (row.SetFcnName == "NEOf") then
					local riverPlot = Map.GetAdjacentPlot(targetPlot:GetX(), targetPlot:GetY(), DirectionTypes.DIRECTION_NORTHEAST);
					if (riverPlot) then
						TerrainBuilder.SetNEOfRiver(riverPlot, true, GetOppositeFlowDirection(row.FlowDirection), row.RiverID + g_NumNonMirroredRivers);
					end

				end
			end
		end
	end
end

function AddCenteredNaturalWonder()

	local possibleNW = {};
	local pCenterHexes = {};
	for dx = 0, 1 do
		for dy = 0, 1 do
			local iCenterHexIndex = ((g_iH/2 + dy - 1) * g_iW) + (g_iW/2 + dx - 1);
			local pCenterHexPlot = Map.GetPlotByIndex(iCenterHexIndex);
			table.insert(pCenterHexes, pCenterHexPlot);
			print ("CenterHex: (" .. tostring(pCenterHexPlot:GetX()) .. ", " .. tostring(pCenterHexPlot:GetY()) .. ")");
		end
	end
	for i, centerHex in ipairs(pCenterHexes) do
		TerrainBuilder.SetFeatureType(centerHex, -1);  -- Clear any feature that might have been dropped here
		for row in GameInfo.Features() do
			if (row.NaturalWonder) then
				local customPlacement = row.CustomPlacement;
				if (customPlacement == nil) then
					if (TerrainBuilder.CanHaveFeature(centerHex, row.Index, false)) then
						local possibleLoc = {};
						possibleLoc.Feature = row.Index;
						possibleLoc.Plot = centerHex;
						table.insert(possibleNW, possibleLoc);
					end
				elseif (CustomCanHaveFeature(centerHex, row.Index)) then
					local possibleLoc = {};
					possibleLoc.Feature = row.Index;
					possibleLoc.Plot = centerHex;
					table.insert(possibleNW, possibleLoc);
				end
			end
		end
	end
	print ("#possibleNW Locs: " .. tostring(#possibleNW));

	if (#possibleNW > 0) then
		local iRoll = TerrainBuilder.GetRandomNumber(#possibleNW, "Random Natural Wonder");
		local possibleLoc = possibleNW[iRoll + 1];
		local eFeatureType = possibleLoc.Feature;
		local pPlot = possibleLoc.Plot;

		print ("iRoll: " .. tostring(iRoll));
		print ("eFeatureType: " .. tostring(eFeatureType));
		print ("Plot: (" .. tostring(pPlot:GetX()) .. ", " .. tostring(pPlot:GetY()) .. ")");

		local customPlacement = GameInfo.Features[eFeatureType].CustomPlacement;
		if (customPlacement == nil) then
			TerrainBuilder.SetFeatureType(pPlot, eFeatureType);
			ResetTerrain(pPlot:GetIndex());
			local plotX = pPlot:GetX();
			local plotY = pPlot:GetY();
			for dx = -2, 2 do
				for dy = -2,2 do
					local otherPlot = Map.GetPlotXY(plotX, plotY, dx, dy, 2);
					if(otherPlot) then
						if(otherPlot:IsNaturalWonder() == true) then
							ResetTerrain(otherPlot:GetIndex());
						end
					end
				end
			end
		else
			CustomSetFeatureType(pPlot, eFeatureType);
		end
		print (" Set Wonder with Feature ID of " .. tostring(eFeatureType) .. " at location (" .. tostring(pPlot:GetX()) .. ", " .. tostring(pPlot:GetY()) .. ")");
	end
end

function MirrorStartPositions(start_plots)
	
	local distancesToQuadrantCenter = {};

	for i, plot in ipairs(start_plots.majorStartPlots) do

		local iQuadrant = GetPlotQuadrant(plot);
		local iXDistanceToBoundary = 0;
		if (iQuadrant == 0 or iQuadrant == 2) then
			iXDistanceToBoundary = math.min((g_iW / 2 - 1) - plot:GetX(), plot:GetX());
		else
			iXDistanceToBoundary = math.min(plot:GetX() - (g_iW / 2), (g_iW - plot:GetX()));
		end
		local iYDistanceToBoundary = 0;
		if (iQuadrant <= 1) then
			iYDistanceToBoundary = (g_iH / 2 - 1) - plot:GetY();
		else
			iYDistanceToBoundary = plot:GetY() - (g_iH / 2);
		end
		local iDistanceToBoundary = iXDistanceToBoundary;
		if (iYDistanceToBoundary < iXDistanceToBoundary) then
			iDistanceToBoundary = iYDistanceToBoundary;
		end
		print (tostring(iQuadrant) .. ": " .. tostring(plot:GetX()) .. ", " .. tostring(plot:GetY()) .. ". Distance: " .. tostring(iDistanceToBoundary));

		local quadrantData = {};
		quadrantData.Distance = iDistanceToBoundary;
		quadrantData.Quadrant = iQuadrant;
		quadrantData.PlayerIndex = i - 1;
		table.insert(distancesToQuadrantCenter, quadrantData);
	end

	table.sort (distancesToQuadrantCenter, function(a, b) return a.Distance > b.Distance; end);

	local iCenteredPlayer = distancesToQuadrantCenter[1].PlayerIndex;
	local iCenteredQuadrant = distancesToQuadrantCenter[1].Quadrant;
	print ("iCenteredPlayer: " .. tostring(iCenteredPlayer));
	print ("iCenteredQuadrant: " .. tostring(iCenteredQuadrant));

	local iXOffsetFromCenter = Players[iCenteredPlayer]:GetStartingPlot():GetX() - GetQuadrantCenterPlot(iCenteredQuadrant):GetX();
	local iYOffsetFromCenter = Players[iCenteredPlayer]:GetStartingPlot():GetY() - GetQuadrantCenterPlot(iCenteredQuadrant):GetY();
	print ("iXOffsetFromCenter: " .. tostring(iXOffsetFromCenter));
	print ("iYOffsetFromCenter: " .. tostring(iYOffsetFromCenter));

	start_plots.majorCopy = {};

	for i = 1, start_plots.iNumMajorCivs do
		local player = Players[start_plots.majorList[i]]
		
		if (player == nil) then
			print("THIS PLAYER FAILED");
		else
		    local iXOffset = iXOffsetFromCenter;
			local iYOffset = iYOffsetFromCenter;
			if ((iCenteredQuadrant == 0 or iCenteredQuadrant == 2) and ((i-1) == 1 or (i-1) == 3) or
			    (iCenteredQuadrant == 1 or iCenteredQuadrant == 3) and ((i-1) == 0 or (i-1) == 2)) then
				iXOffset = -iXOffset;
			end
			if (iCenteredQuadrant <  2 and (i-1) >= 2 or 
			    iCenteredQuadrant >= 2 and (i-1) < 2) then
				iYOffset = -iYOffset;
			end
			local iQuadrantStartX = GetQuadrantCenterPlot(i-1):GetX() + iXOffset;
			local iQuadrantStartY = GetQuadrantCenterPlot(i-1):GetY() + iYOffset;
			local pQuadrantStartPlot = Map.GetPlot(iQuadrantStartX, iQuadrantStartY);
			player:SetStartingPlot(pQuadrantStartPlot);
			print("Mirrored Major Start X: ", iQuadrantStartX, "Start Y: ", iQuadrantStartY);

			table.insert(start_plots.majorCopy, pQuadrantStartPlot);
		end
	end


end

function GetPlotQuadrant(pPlot)
	
	if (pPlot:GetX() < g_iW/2 and pPlot:GetY() < g_iH/2) then
		return 0;
	elseif (pPlot:GetX() >= g_iW/2 and pPlot:GetY() < g_iH/2) then
		return 1;
	elseif (pPlot:GetX() < g_iW/2 and pPlot:GetY() >= g_iH/2) then
		return 2;
	else
		return 3;
	end	
end

function GetQuadrantCenterPlot(iQuadrant)

	local iX;
	local iY;

	if (iQuadrant == 0) then
		iX = g_iW / 4 - 1;
		iY = g_iH / 4;
	elseif (iQuadrant == 1) then
		iX = (3 * g_iW / 4);
		iY = g_iH / 4;
	elseif (iQuadrant == 2) then
		iX = g_iW / 4 - 1;
		iY = (3 * g_iH / 4);
	else
		iX = (3 * g_iW / 4);
		iY = (3 * g_iH / 4);
	end		

	return Map.GetPlot(iX, iY);
end

function RedoMinorStartPositions(start_plots)

	-- Create copy of original minor starts
	local minorStarts = start_plots.minorStartPlots;

	-- Erase ones from start_plots
	start_plots.minorStartPlots = {};

	local iMinorIndex = 1;
	while iMinorIndex <= start_plots.iNumMinorCivs do
		local player1 = Players[start_plots.minorList[iMinorIndex]];
		local player2 = nil;
		if (iMinorIndex + 1 <= start_plots.iNumMinorCivs) then
			player2 = Players[start_plots.minorList[iMinorIndex + 1]];
		end
		
		if (player1 == nil) then
			print("THIS PLAYER FAILED");
			return nil;
		else
			local pStartPlot1 = GetNextMinorCandidate(start_plots);
			if (pStartPlot1 ~= nil) then
				player1:SetStartingPlot(pStartPlot1);
				table.insert(start_plots.minorStartPlots, pStartPlot1);
				print("Minor Start X: ", pStartPlot1:GetX(), "Start Y: ", pStartPlot1:GetY());
				if (player2 ~= nil) then
					pStartPlot2 = GetMirroredMinorPlot(pStartPlot1);
					if (pStartPlot2 ~= nil) then
						player2:SetStartingPlot(pStartPlot2)
						table.insert(start_plots.minorStartPlots, pStartPlot2);
						print("Mirrored Minor Start X: ", pStartPlot2:GetX(), "Start Y: ", pStartPlot2:GetY());
						iMinorIndex = iMinorIndex + 2;
					else
						print("SECOND MINOR START FAILED");
						return nil;
					end
				else
					return;  -- Normal return if odd number of minors
				end
			else
				print("FALLBACK - must use valid original minor city starts mirrored diagonally");
				for i, plot in ipairs(minorStarts) do
					if (start_plots:__MinorMajorCivBuffer(plot) and start_plots:__MinorMinorCivBuffer(plot) ) then
						player1:SetStartingPlot(plot);
						print("Fallback Minor Start X: ", plot:GetX(), "Start Y: ", plot:GetY());
						if (player2 ~= nil) then
							local mirroredPlot = Map.GetPlotByIndex((g_iH - plot:GetY() - 1) * g_iW + (g_iW - plot:GetX() - 1));
							player2:SetStartingPlot(mirroredPlot);
							print("Fallback Mirror Start X: ", mirroredPlot:GetX(), "Start Y: ", mirroredPlot:GetY());
						end
						break;
					end
				end
				iMinorIndex = iMinorIndex + 2;
				return nil;
			end
		end
	end
end

function GetNextMinorCandidate(start_plots)

	local iX = 0;
	local iY = 0;

	while (iX == 0 and iY == 0 and g_MinorCandidatesTried <= 8) do

		local iCandidateX = 0;
		local iCandidateY = 0;
		local iDX = 0;
		local iDY = 0;

		if (g_MinorCandidatesTried == 0) then
			iCandidateX = 14;
			iCandidateY = 18;
			iDX = 0;
			iDY = 1;
		elseif (g_MinorCandidatesTried == 1) then
			iCandidateX = 29;
			iCandidateY = 9;
			iDX = 1;
			iDY = 0;
		elseif (g_MinorCandidatesTried == 2) then
			iCandidateX = 6;
			iCandidateY = 19;
			iDX = 0;
			iDY = -1;
		elseif (g_MinorCandidatesTried == 3) then
			iCandidateX = 22;
			iCandidateY = 18;
			iDX = 0;
			iDY = 1;
		elseif (g_MinorCandidatesTried == 4) then
			iCandidateX = 30;
			iCandidateY = 4;	
			iDX = -1;
			iDY = 0;
		elseif (g_MinorCandidatesTried == 5) then
			iCandidateX = 29;
			iCandidateY = 14;	
			iDX = 1;
			iDY = 0;
		elseif (g_MinorCandidatesTried == 6) then
			iCandidateX = 10;
			iCandidateY = 19;	
			iDX = 0;
			iDY = -1;
		elseif (g_MinorCandidatesTried == 7) then
			iCandidateX = 18;
			iCandidateY = 18;	
			iDX = 0;
			iDY = 1;
		elseif (g_MinorCandidatesTried == 8) then
			iCandidateX = 26;
			iCandidateY = 19;	
			iDX = 0;
			iDY = -1;
		end

		local pCandidatePlot = Map.GetPlot(iCandidateX, iCandidateY);
		if (pCandidatePlot ~= nil and not pCandidatePlot:IsWater() and not pCandidatePlot:IsImpassable() and start_plots:__MinorMajorCivBuffer(pCandidatePlot)) then
			iX = iCandidateX;
			iY = iCandidateY;
		else
			-- Nudge it to the other side of the border and try again
			pCandidatePlot = Map.GetPlot(iCandidateX + iDX, iCandidateY + iDY);
			if (pCandidatePlot ~= nil and not pCandidatePlot:IsWater() and not pCandidatePlot:IsImpassable() and start_plots:__MinorMajorCivBuffer(pCandidatePlot)) then
				iX = iCandidateX + iDX;
				iY = iCandidateY + iDY;
			end
		end

		g_MinorCandidatesTried = g_MinorCandidatesTried + 1;
	end

	if (iX == 0 and iY == 0) then
		return nil;
	end
								
	print("Minor Candidate X: ", iX, " Y: ", iY);

	return Map.GetPlot(iX, iY);
end

function GetMirroredMinorPlot(pOriginalPlot)
	
	local iX = pOriginalPlot:GetX();
	local iY = pOriginalPlot:GetY();

	-- On Equator?
	if (g_iH - (iY * 2) <= 2) then 
		iX = g_iW - iX - 1;

	-- On Prime Meridian?
	elseif (g_iW - (iX * 2) <= 2) then
		iY = g_iH - iY - 1;
	end

	return Map.GetPlot(iX, iY);
end

function AddMirroredLakes(largeLakes)

	print("Map Generation - Adding Mirrored Lakes");
	largeLakes = largeLakes or 0;

	local numLakesAdded = 0;
	local numLargeLakesAdded = 0;

	local lakePlotRand = GlobalParameters.LAKE_PLOT_RANDOM or 25;
	local iW, iH = Map.GetGridSize();

	for iX = 0, (iW/2 - 1), 1 do
		for iY = 0, (iH/2 - 1), 1 do
			plot0 = Map.GetPlotByIndex(iY * g_iW + iX);
			if(plot0) then
				if (plot0:IsWater() == false) then
					if (plot0:IsCoastalLand() == false) then
						if (plot0:IsRiver() == false and plot0:IsRiverAdjacent() == false) then
							if (AdjacentToNaturalWonder(plot0) == false) then
								local r = TerrainBuilder.GetRandomNumber(lakePlotRand, "MapGenerator AddLakes");
								if r == 0 then
									numLakesAdded = numLakesAdded + 4;
									if(largeLakes > numLargeLakesAdded) then
										local bLakes = AddMoreMirroredLake(plot);
										if(bLakes == true) then
											numLargeLakesAdded = numLargeLakesAdded + 4;
										end
									end

									TerrainBuilder.SetTerrainType(plot0, g_TERRAIN_TYPE_COAST);
									plot1 = Map.GetPlotByIndex(iY * g_iW + (g_iW - iX -1));
									TerrainBuilder.SetTerrainType(plot1, g_TERRAIN_TYPE_COAST);
									plot2 = Map.GetPlotByIndex((g_iH - iY -1) * g_iW + iX);
									TerrainBuilder.SetTerrainType(plot2, g_TERRAIN_TYPE_COAST);
									plot3 = Map.GetPlotByIndex((g_iH - iY -1) * g_iW + (g_iW - iX -1));
									TerrainBuilder.SetTerrainType(plot3, g_TERRAIN_TYPE_COAST);
								end
							end
						end
					end
				end
			end
		end
	end
	
	-- this is a minimalist update because lakes have been added
	if numLakesAdded > 0 then
		print(tostring(numLakesAdded).." lakes added")
		AreaBuilder.Recalculate();
	end
end

function AddMoreMirroredLake(plot)
	local largeLake = 0;
	lakePlots = {};

	for direction = 0, DirectionTypes.NUM_DIRECTION_TYPES - 1, 1 do
		local adjacentPlot = Map.GetAdjacentPlot(plot:GetX(), plot:GetY(), direction);
		if (adjacentPlot) then
			if (adjacentPlot:IsWater() == false)  then
				if (adjacentPlot:IsCoastalLand() == false) then
					if (adjacentPlot:IsRiver() == false and adjacentPlot:IsRiverAdjacent() == false) then
						if (AdjacentToNaturalWonder(adjacentPlot) == false) then
							local r = TerrainBuilder.GetRandomNumber(4 + largeLake, "MapGenerator AddLakes");
							if r < 3 then
								table.insert(lakePlots, adjacentPlot);
								largeLake = largeLake + 1;
							end
						end
					end
				end
			end
		end
	end

	for iLake, lakePlot in ipairs(lakePlots) do
		TerrainBuilder.SetTerrainType(lakePlot, g_TERRAIN_TYPE_COAST);
		plot1 = Map.GetPlotByIndex(lakePlot:GetY() * g_iW + (g_iW - lakePlot:GetX() -1));
		TerrainBuilder.SetTerrainType(plot1, g_TERRAIN_TYPE_COAST);
		plot2 = Map.GetPlotByIndex((g_iH - lakePlot:GetY() -1) * g_iW + lakePlot:GetX());
		TerrainBuilder.SetTerrainType(plot2, g_TERRAIN_TYPE_COAST);
		plot3 = Map.GetPlotByIndex((g_iH - lakePlot:GetY() -1) * g_iW + (g_iW - lakePlot:GetX() -1));
		TerrainBuilder.SetTerrainType(plot3, g_TERRAIN_TYPE_COAST);
	end

	if (largeLake > 2) then
		return true;
	else 
		return false;
	end
end