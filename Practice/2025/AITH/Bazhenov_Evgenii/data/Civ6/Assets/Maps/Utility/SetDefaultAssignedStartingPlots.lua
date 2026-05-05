------------------------------------------------------------------------------
--	FILE:	 SetDefaultAssignedStartingPlots.lua
--	AUTHOR:  
--	PURPOSE: A fallback script to assign starting plots if the map generator or
--			 World Builder map did not assign a player a starting location.
--			 If a player already has a valid starting plot, it will not be changed.
------------------------------------------------------------------------------
--	Copyright (c) 2016 Firaxis Games, Inc. All rights reserved.
------------------------------------------------------------------------------

include "AssignStartingPlots"

function SetDefaultAssignedStartingPlots()

	-- START_MIN_Y and START_MAX_Y is the percent of the map ignored for major civs' starting positions.
	local args = {
		MIN_MAJOR_CIV_FERTILITY = 150,
		MIN_MINOR_CIV_FERTILITY = 50, 
		MIN_BARBARIAN_FERTILITY = 1,
		START_MIN_Y = 15,
		START_MAX_Y = 15
	};
	local start_plot_database = AssignStartingPlots.Create(args)

end