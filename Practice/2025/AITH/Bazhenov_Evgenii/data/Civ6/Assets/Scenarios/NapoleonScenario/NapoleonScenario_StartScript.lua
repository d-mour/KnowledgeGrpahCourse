
function InitializeNewGame()
	print("Napoleon Scenario InitializeNewGame");
	local ballisticsTech = GameInfo.Technologies["TECH_BALLISTICS"];
	local milScienceTech = GameInfo.Technologies["TECH_MILITARY_SCIENCE"];
	local gunpowerTech = GameInfo.Technologies["TECH_GUNPOWDER"];

	local aPlayers = PlayerManager.GetAliveMajors();
	for _, pPlayer in ipairs(aPlayers) do

		-- Give all major civs some techs to make this feel more Napoleon era.
		local curPlayerTech = pPlayer:GetTechs();
		if(curPlayerTech ~= nil) then
			if (ballisticsTech ~= nil) then
				curPlayerTech:SetResearchProgress(ballisticsTech.Index, curPlayerTech:GetResearchCost(ballisticsTech.Index));
			end
			if(milScienceTech ~= nil) then
				curPlayerTech:SetResearchProgress(milScienceTech.Index, curPlayerTech:GetResearchCost(milScienceTech.Index));
			end
			if(gunpowerTech ~= nil) then
				curPlayerTech:SetResearchProgress(gunpowerTech.Index, curPlayerTech:GetResearchCost(gunpowerTech.Index));
			end
		end
	end
end


function Initialize()
	print("Napoleon Scenario Start Script initializing");
	LuaEvents.NewGameInitialized.Add(InitializeNewGame);
end
Initialize();