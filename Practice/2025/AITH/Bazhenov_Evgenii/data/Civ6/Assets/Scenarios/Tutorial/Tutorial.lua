print("Running Tutorial Script");

local lastLocalTurnNumber = 0

local function AssignStartingTech()
	local playerID = Game.GetLocalPlayer()

	if playerID ~= PlayerTypes.NONE then
		local player = Players[playerID]
		local playerTechs = player:GetTechs()

		if playerTechs ~= nil then
			local techHash = DB.MakeHash("TECH_DAWN_OF_CIVILIZATION")

			if techHash ~= nil then
				playerTechs:SetResearchingTech(techHash)
			else
				print("tutscenario invalid tech hash")
			end
		else
			print("tutscenario invalid player techs")
		end
	else
		print("tutscenario invalid local player")
	end
end

local function FinishBuildingCityGoal()
	local playerID = Game.GetLocalPlayer()

	if playerID ~= PlayerTypes.NONE then
		local player = Players[playerID]
		local playerCities = player:GetCities()

		if playerCities ~= nil then
			local capitalCity = playerCities:GetCapitalCity()

			if capitalCity ~= nil then
				local buildQueue = capitalCity:GetBuildQueue()
				buildQueue:FinishProgress()
			else
				print("tutscenario invalid capital city")
			end
		else
			print("tutscenario invalid player cities")
		end
	else
		print("tutscenario invalid local player")
	end
end

local function CreateBarbarianWarrior()
	local playerID = Game.GetLocalPlayer()

	if playerID ~= PlayerTypes.NONE then
		local player = Players[playerID]
		local playerCities = player:GetCities()

		if playerCities ~= nil then
			local capitalCity = playerCities:GetCapitalCity()

			if capitalCity ~= nil then
				local barbarians = PlayerManager.GetAliveBarbarians()
				local barbarianUnits = barbarians[1]:GetUnits()

				local unitType = GameInfo.Units["UNIT_WARRIOR"].Index
				local plotX = capitalCity:GetX() + 1
				local plotY = capitalCity:GetY()
				local barbarianUnit = barbarianUnits:Create(unitType, plotX, plotY)
				local maxDamage = barbarianUnit:GetMaxDamage()
				barbarianUnit:SetDamage(maxDamage - 1)
			else
				print("tutscenario invalid capital city")
			end
		else
			print("tutscenario invalid player cities")
		end
	else
		print("tutscenario invalid local player")
	end
end

local function FinishResearchGoal()
	local playerID = Game.GetLocalPlayer()

	if playerID ~= PlayerTypes.NONE then
		local player = Players[playerID]
		local playerTechs = player:GetTechs()

		if playerTechs ~= nil then
			local tech = playerTechs:GetResearchingTech()
			playerTechs:SetResearchProgress(tech, 1000000)
		else
			print("tutscenario invalid player techs")
		end
	else
		print("tutscenario invalid local player")
	end
end

local function OnPlayerTurnActivated( player, bIsFirstTime )
	if (bIsFirstTime and player == Game.GetLocalPlayer()) then
		local currentTurn = Game.GetCurrentGameTurn();

		if currentTurn > lastLocalTurnNumber then
			if 1 == currentTurn then
				AssignStartingTech()
			elseif 3 == currentTurn then
				FinishBuildingCityGoal()  -- warrior
				CreateBarbarianWarrior()
				LuaEvents.Tutorial_RestoreWorldTracker();
			end

			lastLocalTurnNumber = currentTurn
		end
	end
end

Events.PlayerTurnActivated.Add(OnPlayerTurnActivated)
