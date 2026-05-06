----------------------------------------------------------------  
-- Plot Filtering
--
-- GameCore scripting functions related to filtering tables of plots.
----------------------------------------------------------------  


----------------------------------------------------------------  
-- Custom Filter Functions for Use with Plot Filtering Functions
---------------------------------------------------------------- 
------------------------------------------------------------------------------------------------------------------------
-- Returns true if plot does not contain major civ unit.
function FilterPlot_NotMajorCivUnits(curPlot :object) 
	local pUnitList = Map.GetUnitsAt(curPlot);
	if pUnitList ~= nil then
		local pUnit;
		for pUnit in pUnitList:Units() do
			local pOwnerConfig = PlayerConfigurations[pUnit:GetOwner()];
			if(pOwnerConfig ~= nil and pOwnerConfig:GetCivilizationLevelTypeID() == CivilizationLevelTypes.CIVILIZATION_LEVEL_FULL_CIV) then
				return false;
			end
		end
	end

	return true;
end

------------------------------------------------------------------------------------------------------------------------
-- Returns a custom filter function (usable by FilterAllAdjPlots or FilterOneAdjPlots) that will return true if a given plot contains a unit owned by iPlayerID.
function GetFilterPlots_PlayerUnits(iPlayerID)
	function CustomFilterFunction(filterPlot :object)
		local pfilterUnitList = Map.GetUnitsAt(filterPlot);
		if pfilterUnitList ~= nil then
			for pfilterUnit in pfilterUnitList:Units() do
				if(pfilterUnit:GetOwner() == iPlayerID) then
					return true;
				end
			end
		end

		return false;
	end
	return CustomFilterFunction;
end

------------------------------------------------------------------------------------------------------------------------
-- Returns a custom filter function (usable by FilterAllAdjPlots or FilterOneAdjPlots) that will return true if a given plot does NOT contain a unit owned by iPlayerID.
function GetFilterPlots_NotPlayerUnits(iPlayerID)
	function CustomFilterFunction(filterPlot :object)
		local pfilterUnitList = Map.GetUnitsAt(filterPlot);
		if pfilterUnitList ~= nil then
			for pfilterUnit in pfilterUnitList:Units() do
				if(pfilterUnit:GetOwner() == iPlayerID) then
					return false;
				end
			end
		end

		return true;
	end
	return CustomFilterFunction;
end

------------------------------------------------------------------------------------------------------------------------
-- Returns a custom filter function (usable by FilterAllAdjPlots or FilterOneAdjPlots) that will return true if a given plot is within plotDistance of plotX/plotY.
function GetFilterPlots_NearByPlots(plotX :number, plotY :number, plotDistance :number)
	local targetPlot :object = Map.GetPlot(plotX, plotY);
	local targetPlotIndex :number = targetPlot:GetIndex();
	function CustomFilterFunction(filterPlot :object)
		local distance :number = Map.GetPlotDistance(targetPlotIndex, filterPlot:GetIndex());
		if(distance <= plotDistance) then
			return true;
		end
		return false;
	end
	return CustomFilterFunction;
end

------------------------------------------------------------------------------------------------------------------------
-- Returns a custom filter function (usable by FilterAllAdjPlots or FilterOneAdjPlots) that will return true if a given plot is farther than plotDistance from plotX/plotY.
function GetFilterPlots_FarPlots(plotX :number, plotY :number, plotDistance :number)
	local targetPlot :object = Map.GetPlot(plotX, plotY);
	local targetPlotIndex :number = targetPlot:GetIndex();
	function CustomFilterFunction(filterPlot :object)
		local distance :number = Map.GetPlotDistance(targetPlotIndex, filterPlot:GetIndex());
		if(distance > plotDistance) then
			return true;
		end
		return false;
	end
	return CustomFilterFunction;
end


----------------------------------------------------------------  
-- Filtering Functions
---------------------------------------------------------------- 
------------------------------------------------------------------------------------------------------------------------
-- Returns a filtered version of a given table of map plots (plotsList) based on filterPlotFunction being true the plots in the table.
-- 
-- revertOnEmpty - If true, plotsList will not be changed if the resulting filter results in zero remaining plots. 
function FilterPlots(plotsList :table, filterPlotFunction, revertOnEmpty :boolean)
	local nextPlotsList :table = {};
	for oldPlotsIndex=1, #plotsList do
		local curPlot = plotsList[oldPlotsIndex];
		if(filterPlotFunction(curPlot) == true) then
			table.insert(nextPlotsList, curPlot);
		end
	end

	if(#nextPlotsList > 0 or revertOnEmpty == false) then
		return nextPlotsList;
	else
		print("No plots remaining. Falling back to original plotsList.");
		return plotsList;
	end
end

------------------------------------------------------------------------------------------------------------------------
-- Returns a filtered version of a given table of map plots (supplyDropPlots) based on filterPlotFunction being true for all adjacent plots within range.
-- 
-- revertOnEmpty - If true, supplyDropPlots will not be changed if the resulting filter results in zero remaining plots.  
function FilterAllAdjPlots(supplyDropPlots :table, range :number, filterPlotFunction, revertOnEmpty :boolean)
	if(range <= 0) then
		return;
	end

	local nextSupplyDropPlots :table = {};
	for oldPlotsIndex=1, #supplyDropPlots do
		local oldDropPlot = supplyDropPlots[oldPlotsIndex];
		local adjPlots = Map.GetNeighborPlots(oldDropPlot:GetX(), oldDropPlot:GetY(), range);
		local validPlot :boolean = true;
		for loop, adjPlot in ipairs(adjPlots) do
			-- Is supply crate too close?
			if(filterPlotFunction(adjPlot) == false) then
				validPlot = false;
				break;
			end
		end
					
		if(validPlot == true) then
			table.insert(nextSupplyDropPlots, oldDropPlot);
		end
	end

	if(#nextSupplyDropPlots > 0 or revertOnEmpty == false) then
		return nextSupplyDropPlots;
	else
		print("No supply drops remaining. Falling back to original plots list.");
		return supplyDropPlots;
	end
end

------------------------------------------------------------------------------------------------------------------------
-- Returns a filtered version of a given table of map plots (plotsList) based on filterPlotFunction being true for one of the adjacent plots within range.
-- 
-- revertOnEmpty - If true, plotsList will not be changed if the resulting filter results in zero remaining plots.  
function FilterOneAdjPlots(plotsList :table, range :number, filterPlotFunction, revertOnEmpty :boolean)
	if(range <= 0) then
		return;
	end

	local nextPlotsList :table = {};
	for oldPlotsIndex=1, #plotsList do
		local oldDropPlot = plotsList[oldPlotsIndex];
		local adjPlots = Map.GetNeighborPlots(oldDropPlot:GetX(), oldDropPlot:GetY(), range);
		for loop, adjPlot in ipairs(adjPlots) do
			if(filterPlotFunction(adjPlot) == true) then
				table.insert(nextPlotsList, oldDropPlot);
				break;
			end
		end
	end

	if(#nextPlotsList > 0 or revertOnEmpty == false) then
		return nextPlotsList;
	else
		print("No plots remaining. Falling back to plots list.");
		return plotsList;
	end
end