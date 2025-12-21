--Used to determine the next direction when turning
if(FlowDirectionTypes ~= nil) then
	TurnRightFlowDirections = {
		[FlowDirectionTypes.FLOWDIRECTION_NORTH] 
			= FlowDirectionTypes.FLOWDIRECTION_NORTHEAST,
		
		[FlowDirectionTypes.FLOWDIRECTION_NORTHEAST] 
			= FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST,	
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST] 
			= FlowDirectionTypes.FLOWDIRECTION_SOUTH,		
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTH]	
			= FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST,	
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST] 
			= FlowDirectionTypes.FLOWDIRECTION_NORTHWEST,	
		
		[FlowDirectionTypes.FLOWDIRECTION_NORTHWEST]
			= FlowDirectionTypes.FLOWDIRECTION_NORTH,
	};

	TurnLeftFlowDirections = {
		[FlowDirectionTypes.FLOWDIRECTION_NORTH] 
			= FlowDirectionTypes.FLOWDIRECTION_NORTHWEST,
		
		[FlowDirectionTypes.FLOWDIRECTION_NORTHEAST] 
			= FlowDirectionTypes.FLOWDIRECTION_NORTH,
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST] 
			= FlowDirectionTypes.FLOWDIRECTION_NORTHEAST,
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTH] 
			= FlowDirectionTypes.FLOWDIRECTION_SOUTHEAST,
		
		[FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST] 
			= FlowDirectionTypes.FLOWDIRECTION_SOUTH, 
		
		[FlowDirectionTypes.FLOWDIRECTION_NORTHWEST] 
			= FlowDirectionTypes.FLOWDIRECTION_SOUTHWEST,
	};
end

function GetOppositeFlowDirection(dir)
	local numTypes = FlowDirectionTypes.NUM_FLOWDIRECTION_TYPES;
	return ((dir + 3) % numTypes);
end

function GetRiverValueAtPlot(plot)
	if(plot:IsNWOfCliff() or plot:IsWOfCliff() or plot:IsNEOfCliff()) then
		return -1;
	elseif(plot:IsNaturalWonder() or AdjacentToNaturalWonder(plot)) then
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

	return sum;
end

function GetPlotElevation(plot)

	if (plot:IsMountain()) then
		return 4;
	elseif (plot:IsHills()) then
		return 3;
	elseif (not plot:IsWater()) then
		return 2;
	else
		return 1;
	end
end

nextRiverID = 0;
_rivers = {};
function DoRiver(startPlot, thisFlowDirection, originalFlowDirection, riverID)
	
	thisFlowDirection = thisFlowDirection or FlowDirectionTypes.NO_FLOWDIRECTION;
	originalFlowDirection = originalFlowDirection or FlowDirectionTypes.NO_FLOWDIRECTION;

	-- pStartPlot = the plot at whose SE corner the river is starting
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
		TerrainBuilder.SetWOfRiver(riverPlot, true, thisFlowDirection);
--		print ("NORTH: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		riverPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_NORTHEAST);

		if (riverPlot == nil or riverPlot:IsWater() or riverPlot:IsNEOfRiver() or riverPlot:IsNWOfRiver()) then
			return;
		end

	elseif (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_NORTHEAST) then
	
		riverPlot = startPlot;
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetNWOfRiver(riverPlot, true, thisFlowDirection);
--		print ("NE: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
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
		TerrainBuilder.SetNEOfRiver(riverPlot, true, thisFlowDirection);
--		print ("SE: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
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
		TerrainBuilder.SetWOfRiver(riverPlot, true, thisFlowDirection);
--		print ("SOUTH: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
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
		TerrainBuilder.SetNWOfRiver(riverPlot, true, thisFlowDirection);
--		print ("SW: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
		-- riverPlot does not change

		local adjacentPlot = Map.GetAdjacentPlot(riverPlot:GetX(), riverPlot:GetY(), DirectionTypes.DIRECTION_SOUTHWEST);
		if (adjacentPlot == nil or adjacentPlot:IsWater() or adjacentPlot:IsWOfRiver() or riverPlot:IsNEOfRiver()) then
			return;
		end

	elseif (thisFlowDirection == FlowDirectionTypes.FLOWDIRECTION_NORTHWEST) then
		
		riverPlot = startPlot;
		_rivers[riverPlot] = riverID;
		TerrainBuilder.SetNEOfRiver(riverPlot, true, thisFlowDirection);
--		print ("NW: " .. tostring(riverPlot:GetX()) .. ", " .. tostring(riverPlot:GetY()));
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
					
						local value = GetRiverValueAtPlot(adjacentPlot);
						if (flowDirection == originalFlowDirection) then
							value = (value * 3) / 4;
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
		
		DoRiver(riverPlot, bestFlowDirection, originalFlowDirection, riverID);
	end
	
end

function AddRivers()
	--GlobalParameters.RIVER_SEA_WATER_RANGE_DEFAULT or 
	local riverSourceRangeDefault = GlobalParameters.RIVER_SOURCE_RANGE_DEFAULT or 4;
	local seaWaterRangeDefault = 3;
	local plotsPerRiverEdge = GlobalParameters.RIVER_PLOTS_PER_EDGE or 12;
	
	print("Map Generation - Adding Rivers");
	
	local passConditions = {
		function(plot)
			return (plot:IsHills() or plot:IsMountain());
		end,
		
		function(plot)
			return (not plot:IsCoastalLand()) and (TerrainBuilder.GetRandomNumber(8, "MapGenerator AddRivers") == 0);
		end,
		
		function(plot)
			local area = plot:GetArea();
			return (plot:IsHills() or plot:IsMountain()) and (area:GetRiverEdgeCount() <	((area:GetPlotCount() / plotsPerRiverEdge) + 1));
		end,
		
		function(plot)
			local area = plot:GetArea();
			return (area:GetRiverEdgeCount() < (area:GetPlotCount() / plotsPerRiverEdge) + 1);
		end
	}
	
	for iPass, passCondition in ipairs(passConditions) do
					
		if (iPass <= 2) then
			riverSourceRange = riverSourceRangeDefault;
			seaWaterRange = seaWaterRangeDefault;
		else
			riverSourceRange = (riverSourceRangeDefault / 2);
			seaWaterRange = (seaWaterRangeDefault / 2);
		end
			
		local iW, iH = Map.GetGridSize();

		for i = 0, (iW * iH) - 1, 1 do
			plot = Map.GetPlotByIndex(i);
			if(not plot:IsWater()) then
				if(passCondition(plot) and plot:IsNaturalWonder() == false and AdjacentToNaturalWonder(plot) == false) then
					if (not Map.FindWater(plot, riverSourceRange, true)) then
						if (not Map.FindWater(plot, seaWaterRange, false)) then
							local inlandCorner = TerrainBuilder.GetInlandCorner(plot);
							if(inlandCorner and plot:IsNaturalWonder() == false and AdjacentToNaturalWonder(plot) == false) then
								DoRiver(inlandCorner);
							end
						end
					end
				end			
			end
		end
	end		
end

function AddLakes(largeLakes)

	print("Map Generation - Adding Lakes");
	largeLakes = largeLakes or 0;

	local numLakesAdded = 0;
	local numLargeLakesAdded = 0;

	local lakePlotRand = GlobalParameters.LAKE_PLOT_RANDOM or 25;
	local iW, iH = Map.GetGridSize();

	for i = 0, (iW * iH) - 1, 1 do
		plot = Map.GetPlotByIndex(i);
		if(plot) then
			if (plot:IsWater() == false) then
				if (plot:IsCoastalLand() == false) then
					if (plot:IsRiver() == false and plot:IsRiverAdjacent() == false) then
						if (AdjacentToNaturalWonder(plot) == false) then
							local r = TerrainBuilder.GetRandomNumber(lakePlotRand, "MapGenerator AddLakes");
							if r == 0 then
								numLakesAdded = numLakesAdded + 1;
								if(largeLakes > numLargeLakesAdded) then
									local bLakes = AddMoreLake(plot);
									if(bLakes == true) then
										numLargeLakesAdded = numLargeLakesAdded + 1;
									end
								end

								TerrainBuilder.SetTerrainType(plot, g_TERRAIN_TYPE_COAST);
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

function AddMoreLake(plot)
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
	end

	if (largeLake > 2) then
		return true;
	else 
		return false;
	end
end

function AdjacentToNaturalWonder(plot)
	for direction = 0, DirectionTypes.NUM_DIRECTION_TYPES - 1, 1 do
		local adjacentPlot = Map.GetAdjacentPlot(plot:GetX(), plot:GetY(), direction);
		if (adjacentPlot ~= nil) then
			if(adjacentPlot:IsNaturalWonder() == true) then
				return true;
			end
		end
	end 
	return false;
end