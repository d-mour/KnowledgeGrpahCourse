
include "MapUtilities"

-- ===========================================================================
function InitializeNewGame()

	local gridWidth, gridHeight = Map.GetGridSize();
	AddGoodies(gridWidth, gridHeight);
	AddLeyLines();

end

LuaEvents.NewGameInitialized.Add(InitializeNewGame);
