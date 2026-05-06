-- ===========================================================================
--
--	Tutorial items meant to be included from TutorialUIRoot
--	Customized Tutorial-ONLY scenario 
--
-- ===========================================================================

include("InputSupport");


-- ===========================================================================
-- Overall tutorial definition
-- ===========================================================================
hstructure TutorialDefinition
	Id				: string;		-- Id of scenario
	Bank			: table;		-- array of functions that when called populate tutorial items
end


-- ===========================================================================
--	Setup the tutorial environment.
--	RETURN Tutorial defintion
-- ===========================================================================
function InitializeTutorial()
	local scenarioName:string = "RAILS";
	SetScenarioName(scenarioName);
	ForceEnableTutorialLevel();
	ActivateInputFiltering();
	SetSimpleInGameMenu(true);
	SetSlowNextTurnEnable(true);
	DisableSettleHintLens();
	DisableTechAndCivicPopups();
	DisableUnitAction( "UNITCOMMAND_AUTOMATE" );	
	DisableUnitAction( "UNITCOMMAND_DELETE" );	
	DisableUnitAction( "UNITOPERATION_AUTOMATE_EXPLORE" );
	DisableUnitAction( "UNITOPERATION_REMOVE_IMPROVEMENT", "UNIT_BUILDER" );	
	DisableUnitAction( "UNITOPERATION_SKIP_TURN" );	
	DisableUnitAction( "UNITOPERATION_FORTIFY", "UNIT_BUILDER");		
	DisableUnitAction( "UNITOPERATION_FORTIFY", "UNIT_SCOUT");	
	DisableUnitAction( "UNITOPERATION_FORTIFY", "UNIT_WARRIOR");
	DisableUnitAction( "UNITOPERATION_HEAL",	"UNIT_WARRIOR");
	DisableUnitAction( "UNITCOMMAND_CANCEL",	"UNIT_WARRIOR");
	DisableUnitAction( "UNITOPERATION_SLEEP",	"UNIT_BUILDER");	
	UITutorialManager:SetActiveAlways( false );					-- If loading from a save, this may still be (stuck) on.
		
	GoalsAutoRemove();
	UserConfiguration.SetLockedValue("AutoEndTurn", false);		-- Disable AutoEndTurn

	LuaEvents.Tutorial_PlotToolTipsOff();
	LuaEvents.Tutorial_ContextDisableItems( 
		"CityPanel", 
		{
			"PurchaseTileCheck","ManageCitizensCheck","ProduceWithGoldCheck","ProduceWithFaithCheck","YieldsArea",
			"CultureCheck","CultureIgnore","FoodCheck","FoodIgnore","ProductionCheck","ProductionIgnore","ScienceCheck","ScienceIgnore","FaithCheck","FaithIgnore","GoldCheck","GoldIgnore"
		} );

	WriteCustomData("about","Firaxis 'on rails' tutorial.");
	WriteCustomData("version",1);

	Input.SetActiveContext( InputContext.Tutorial ); 

	return hmake TutorialDefinition {
		Id	= scenarioName,
		Bank= { TutorialItemBank1, TutorialItemBank2 }
	};
end


-- ===========================================================================
--	If this is not from a save game, run these commands that would typically
--	be serialized out and read back in automatically.
-- ===========================================================================
function InitFirstRun()
	AddUnitHexRestriction( "UNIT_SCOUT", 14, 12 );				-- Scout cannot go back home		
end


-- ===========================================================================
-- ===========================================================================
function TutorialItemBank1()

	-- ================================ GET_STARTED =====================================
	local item_getStarted:TutorialItem = TutorialItem:new("GET_STARTED");
	item_getStarted:SetRaiseEvents("LocalPlayerTurnBegin");
	item_getStarted:SetIsDoneFunction(
		function()
			return false;
		end );
	item_getStarted:SetNextTutorialItemId("SELECT_SETTLER");
	item_getStarted:SetShowPortrait(true)

	local localPlayer = Game.GetLocalPlayer()
	local playerConfig:table = PlayerConfigurations[localPlayer]
	local leaderTypeName:string = playerConfig:GetLeaderTypeName()

	if "LEADER_CLEOPATRA" == leaderTypeName then
		-- LEADER_CLEOPATRA
		item_getStarted:SetAdvisorMessage("ADVISOR_LINE_FTUE_1ALT_1");		
		item_getStarted:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_1ALT_1");
		item_getStarted:AddAdvisorButton("LOC_ADVISOR_BUTTON_GET_STARTED",
			function( advisorInfo )
				UI.PlaySound("Stop_ADVISOR_LINE_FTUE_1ALT_1")
				LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
			end );
		item_getStarted:SetOpenFunction(
			function()
				-- Disable strategic view
				UI.SetWorldRenderView(WorldRenderView.VIEW_3D)
				UserConfiguration.SetLockedValue("RenderViewIsLocked", true)

				Input.SetActiveContext( InputContext.Tutorial )
				LuaEvents.Tutorial_ForceHideWorldTracker()
                LuaEvents.Tutorial_SwitchToWorldView()
			end );
	else
		-- LEADER_GILGAMESH
		item_getStarted:SetAdvisorMessage("ADVISOR_LINE_FTUE_1ALT_2");
		item_getStarted:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_1ALT_2");
		item_getStarted:AddAdvisorButton("LOC_ADVISOR_BUTTON_GET_STARTED",
			function( advisorInfo )
				UI.PlaySound("Stop_ADVISOR_LINE_FTUE_1ALT_2")
				LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
			end );
		item_getStarted:SetOpenFunction(
			function()
				-- Disable strategic view
				UI.SetWorldRenderView(WorldRenderView.VIEW_3D)
				UserConfiguration.SetLockedValue("RenderViewIsLocked", true)

				Input.SetActiveContext( InputContext.Tutorial )
				LuaEvents.Tutorial_ForceHideWorldTracker()
                LuaEvents.Tutorial_SwitchToWorldView()
			end );
	end

	-- =============================== SELECT_SETTLER =====================================
	local item_selectSettler:TutorialItem = TutorialItem:new("SELECT_SETTLER");
	item_selectSettler:SetPrereqs("GET_STARTED");
	item_selectSettler:SetAdvisorMessage("ADVISOR_LINE_FTUE_2_ALT");
	item_selectSettler:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_2_ALT");
	item_selectSettler:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_2_ALT")
			CenterOnFirstUnit( true );
			UI.DeselectAllUnits();
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_selectSettler:SetIsDoneEvents("UnitSelectionChanged");
	item_selectSettler:SetIsDoneFunction( IsAbleToBuildFirstCity );
	item_selectSettler:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			ClearDimHexes();
		end );
	item_selectSettler:SetAdvisorCallout("LOC_META_1_HEAD", "LOC_META_1_BODY",
		function()
			 local pUnit:table = GetFirstUnitOfType("UNIT_SETTLER");
			 return GetPlotOfUnit( pUnit ):GetIndex();
		end);
	item_selectSettler:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput");
	item_selectSettler:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"));
	item_selectSettler:SetOverlayEnabled( false );
	item_selectSettler:SetNextTutorialItemId("FOUND_FIRST_CITY");
	item_selectSettler:SetShowPortrait(true)
	item_selectSettler:SetOpenFunction(
		function()
			SetGlobalPreActivateFunction( CloseScreensIfOpen );		-- Called before EVERY item's open(); disabled later.  It's not in global init because loading from saves will likely keeping having this behavior.
			UserConfiguration.SetLockedValue("AutoUnitCycle", 0);
		end );

	-- =============================== FOUND_FIRST_CITY =====================================
	local item_foundFirstCity:TutorialItem = TutorialItem:new("FOUND_FIRST_CITY");
	item_foundFirstCity:SetPrereqs("SELECT_SETTLER");
	item_foundFirstCity:SetAdvisorMessage("ADVISOR_LINE_FTUE_22a");
	item_foundFirstCity:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_22a");
	item_foundFirstCity:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_22a")
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_foundFirstCity:SetUITriggers("UnitPanel", "TutorialFoundCityAction");
	item_foundFirstCity:SetEnabledControls(UnitOperationTypes.FOUND_CITY);
	item_foundFirstCity:SetIsDoneEvents("CityAddedToMap");
	item_foundFirstCity:SetShowPortrait(true)
	item_foundFirstCity:SetOpenFunction(
		function()
			UI.SetMapZoom(0.2, 0.0, 0.0);
		end );
	item_foundFirstCity:SetNextTutorialItemId("NURTURE_CITY");

	-- ================================ NURTURE_CITY =====================================
	local item_nurtureCity:TutorialItem = TutorialItem:new("NURTURE_CITY");
	item_nurtureCity:SetPrereqs("FOUND_FIRST_CITY");
	--item_nurtureCity:SetRaiseEvents("CityAddedToMap");
	item_nurtureCity:SetAdvisorMessage("ADVISOR_LINE_FTUE_3_ALTV2");
	item_nurtureCity:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_3_ALTV2");
	item_nurtureCity:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			local player = GetPlayer()
			local capitalCity = player:GetCities():GetCapitalCity()
			UI.SelectCity( capitalCity )  -- Immediate call instead of waiting for callback.
			LuaEvents.Tutorial_CityPanelOpen()

			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_3_ALTV2")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_nurtureCity:SetIsDoneFunction(
		function()
			return false;
		end );
	item_nurtureCity:SetNextTutorialItemId("CITIES_A");
	item_nurtureCity:SetShowPortrait(true)

	-- =============================== CITIES_A =====================================
	local item_citiesA:TutorialItem = TutorialItem:new("CITIES_A");
	item_citiesA:SetPrereqs("NURTURE_CITY");
	item_citiesA:SetAdvisorMessage("LOC_META_103_BODY");
	item_citiesA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_citiesA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_citiesA:SetNextTutorialItemId("CITIES_B");

	-- =============================== CITIES_B =====================================
	local item_citiesB:TutorialItem = TutorialItem:new("CITIES_B");
	item_citiesB:SetPrereqs("CITIES_A");
	item_citiesB:SetAdvisorMessage("LOC_META_104_BODY");
	item_citiesB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_citiesB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_citiesB:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
		end );
	item_citiesB:SetNextTutorialItemId("CITIES_C");

	-- =============================== CITIES_C =====================================
	local item_citiesC:TutorialItem = TutorialItem:new("CITIES_C");
	item_citiesC:SetPrereqs("CITIES_B");
	item_citiesC:SetAdvisorMessage("ADVISOR_LINE_FTUE_36");
	item_citiesC:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_36");
	item_citiesC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_36")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_citiesC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_citiesC:SetShowPortrait(true)
	item_citiesC:SetOpenFunction(
		function()
			UI.SetMapZoom(0.7, 0.0, 0.0);
		end );
	item_citiesC:SetNextTutorialItemId("CITIES_D");

	-- =============================== CITIES_D =====================================
	local item_citiesD:TutorialItem = TutorialItem:new("CITIES_D");
	item_citiesD:SetPrereqs("CITIES_C");
	item_citiesD:SetAdvisorMessage("LOC_META_105_BODY");
	item_citiesD:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_citiesD:SetIsDoneFunction(
		function()
			return false;
		end );
	item_citiesD:SetNextTutorialItemId("YIELDS_9");

	-- =============================== YIELDS_9 =====================================
	local item_yields9:TutorialItem = TutorialItem:new("YIELDS_9");
	item_yields9:SetPrereqs("CITIES_D");
	item_yields9:SetAdvisorMessage("ADVISOR_LINE_FTUE_37a");
	item_yields9:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_37a");
	item_yields9:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_37a")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_yields9:SetIsDoneFunction(
		function()
			return false;
		end );
	item_yields9:SetShowPortrait(true)
	item_yields9:SetNextTutorialItemId("YIELDS_A");

	-- =============================== YIELDS_A =====================================
	local item_yieldsA:TutorialItem = TutorialItem:new("YIELDS_A");
	item_yieldsA:SetPrereqs("YIELDS_9");
	item_yieldsA:SetAdvisorMessage("LOC_META_106_BODY");
	item_yieldsA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_yieldsA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_yieldsA:SetOpenFunction(
	function()
		UI.SetFixedTiltMode( true );
		ShowYieldIcons( true );
	end );
	item_yieldsA:SetNextTutorialItemId("YIELDS_B");

	-- =============================== YIELDS_B =====================================
	local item_yieldsB:TutorialItem = TutorialItem:new("YIELDS_B");
	item_yieldsB:SetPrereqs("YIELDS_A");
	item_yieldsB:SetAdvisorMessage("LOC_META_107_BODY");
	item_yieldsB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_yieldsB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_yieldsB:SetNextTutorialItemId("YIELDS_C");

	-- =============================== YIELDS_C =====================================
	local item_yieldsC:TutorialItem = TutorialItem:new("YIELDS_C");
	item_yieldsC:SetPrereqs("YIELDS_B");
	item_yieldsC:SetAdvisorMessage("LOC_META_108_BODY");
	item_yieldsC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_yieldsC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_yieldsC:SetNextTutorialItemId("YIELDS_C2");

	-- =============================== YIELDS_C2 =====================================
	local item_yieldsC2:TutorialItem = TutorialItem:new("YIELDS_C2");
	item_yieldsC2:SetPrereqs("YIELDS_C");
	item_yieldsC2:SetAdvisorMessage("ADVISOR_LINE_FTUE_38");
	item_yieldsC2:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_38a");
	item_yieldsC2:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_38a")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_yieldsC2:SetIsDoneFunction(
		function()
			return false;
		end );
	item_yieldsC2:SetShowPortrait(true);
	item_yieldsC2:SetOpenFunction(
		function()
			UI.SetFixedTiltMode( false );
			ShowYieldIcons( false );
		end );
	item_yieldsC2:SetNextTutorialItemId("YIELDS_D");

	-- =============================== YIELDS_D =====================================
	local item_yieldsD:TutorialItem = TutorialItem:new("YIELDS_D");
	item_yieldsD:SetPrereqs("YIELDS_C2");
	item_yieldsD:SetAdvisorMessage("LOC_META_109_BODY");
	item_yieldsD:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_yieldsD:SetIsDoneFunction(
		function()
			return false;
		end );
	item_yieldsD:SetNextTutorialItemId("SECURITY_IS_IMPORTANT");

	-- ================================ SECURITY_IS_IMPORTANT =====================================
	local item_securityIsImportant:TutorialItem = TutorialItem:new("SECURITY_IS_IMPORTANT");
	item_securityIsImportant:SetPrereqs("YIELDS_D");
	item_securityIsImportant:SetAdvisorMessage("ADVISOR_LINE_FTUE_46_ALT");
	item_securityIsImportant:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_46_ALT");
	item_securityIsImportant:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_46_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_securityIsImportant:SetIsDoneFunction(
		function()
			return false;
		end );
	item_securityIsImportant:SetNextTutorialItemId("OPEN_CITY_PANEL");
	item_securityIsImportant:SetShowPortrait(true)

	-- =============================== OPEN_CITY_PANEL =====================================
	local item_openCityPanel:TutorialItem = TutorialItem:new("OPEN_CITY_PANEL");
	item_openCityPanel:SetPrereqs("SECURITY_IS_IMPORTANT");
	item_openCityPanel:SetAdvisorMessage("ADVISOR_LINE_FTUE_5_ALT_2");
	item_openCityPanel:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_5_ALT_2");
	item_openCityPanel:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_5_ALT_2")
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_openCityPanel:SetShowPortrait(true)
	item_openCityPanel:SetUITriggers("CityPanel", "TutorialOpenProduction" );
	item_openCityPanel:SetEnabledControls(UITutorialManager:GetHash("ChangeProductionCheck"));
	item_openCityPanel:SetIsDoneEvents("ProductionPanelViaCityOpen");
	item_openCityPanel:SetNextTutorialItemId("TRAIN_WARRIORS_8");

	-- ================================ TRAIN_WARRIORS_8 =====================================
	local item_trainWarriors8:TutorialItem = TutorialItem:new("TRAIN_WARRIORS_8");
	item_trainWarriors8:SetPrereqs("OPEN_CITY_PANEL");
	item_trainWarriors8:SetAdvisorMessage("ADVISOR_LINE_FTUE_51a");
	item_trainWarriors8:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_51a");
	item_trainWarriors8:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_51a")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_trainWarriors8:SetIsDoneFunction(
		function()
			return false;
		end );
	item_trainWarriors8:SetNextTutorialItemId("TRAIN_WARRIORS_9");
	item_trainWarriors8:SetShowPortrait(true)

	-- ================================ TRAIN_WARRIORS_9 =====================================
	local item_trainWarriors9:TutorialItem = TutorialItem:new("TRAIN_WARRIORS_9");
	item_trainWarriors9:SetPrereqs("TRAIN_WARRIORS_8");
	item_trainWarriors9:SetAdvisorMessage("LOC_META_4a_BODY");
	item_trainWarriors9:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_trainWarriors9:SetIsDoneFunction(
		function()
			return false;
		end );
	item_trainWarriors9:SetNextTutorialItemId("TRAIN_WARRIORS");

	-- =============================== TRAIN_WARRIORS =====================================
	local item_trainWarriors:TutorialItem = TutorialItem:new("TRAIN_WARRIORS");
	item_trainWarriors:SetPrereqs("TRAIN_WARRIORS_9");
	item_trainWarriors:SetAdvisorMessage("ADVISOR_LINE_FTUE_6ALTV_1");
	item_trainWarriors:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_6ALTV_1");
	item_trainWarriors:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_6ALTV_1")
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_trainWarriors:SetUITriggers("ChooseProductionMenu", "TutorialTrainWarriors");
	item_trainWarriors:SetEnabledControls( UITutorialManager:GetHash("UNIT_WARRIOR"), UITutorialManager:GetHash("UNIT_AZTEC_EAGLE_WARRIOR") );
	item_trainWarriors:SetIsDoneEvents("CityProductionChanged_Warrior");
	item_trainWarriors:SetShowPortrait(true)
	item_trainWarriors:SetNextTutorialItemId("WARRIORS_BEING_TRAINED");

	-- =============================== WARRIORS_BEING_TRAINED =====================================
	local item_warriorsBeingTrained:TutorialItem = TutorialItem:new("WARRIORS_BEING_TRAINED");
	item_warriorsBeingTrained:SetPrereqs("TRAIN_WARRIORS");
	item_warriorsBeingTrained:SetAdvisorMessage("ADVISOR_LINE_FTUE_61");
	item_warriorsBeingTrained:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_61");
	item_warriorsBeingTrained:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LockProduction();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_61")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_warriorsBeingTrained:SetIsDoneFunction(
		function()
			return false;
		end );
	item_warriorsBeingTrained:SetNextTutorialItemId("WARRIORS_BEING_TRAINED_B");
	item_warriorsBeingTrained:SetShowPortrait(true)

	-- =============================== WARRIORS_BEING_TRAINED_B =====================================
	local item_warriorsBeingTrained:TutorialItem = TutorialItem:new("WARRIORS_BEING_TRAINED_B");
	item_warriorsBeingTrained:SetPrereqs("WARRIORS_BEING_TRAINED");
	item_warriorsBeingTrained:SetAdvisorMessage("ADVISOR_LINE_FTUE_62");
	item_warriorsBeingTrained:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_62");
	item_warriorsBeingTrained:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_62")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_warriorsBeingTrained:SetIsDoneFunction(
		function()
			return false;
		end );
	item_warriorsBeingTrained:SetNextTutorialItemId("TURN_BASED_A");
	item_warriorsBeingTrained:SetShowPortrait(true)

	-- =============================== TURN_BASED_A =====================================
	local item_turnBasedA:TutorialItem = TutorialItem:new("TURN_BASED_A");
	item_turnBasedA:SetPrereqs("WARRIORS_BEING_TRAINED_B");
	item_turnBasedA:SetAdvisorMessage("LOC_META_5a_BODY");
	item_turnBasedA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_turnBasedA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_turnBasedA:SetNextTutorialItemId("TURN_BASED_B");

	-- =============================== TURN_BASED_B =====================================
	local item_turnBasedB:TutorialItem = TutorialItem:new("TURN_BASED_B");
	item_turnBasedB:SetPrereqs("TURN_BASED_A");
	item_turnBasedB:SetAdvisorMessage("LOC_META_5b_BODY");
	item_turnBasedB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_turnBasedB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_turnBasedB:SetNextTutorialItemId("TURN_BASED_C");

	-- =============================== TURN_BASED_C =====================================
	local item:TutorialItem = TutorialItem:new("TURN_BASED_C");
	item:SetPrereqs("TURN_BASED_B");
	item:SetIsEndOfChain(true);
	item:SetIsDoneEvents("LocalPlayerTurnEnd");
	item:SetUITriggers("ActionPanel", "TutorialSelectEndTurn");
	item:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));
	item:SetDisabledControls(UITutorialManager:GetHash("ChangeProductionCheck"));

	-- =============================== SELECT_RESEARCH_8 =====================================
	local item_selectResearch8:TutorialItem = TutorialItem:new("SELECT_RESEARCH_8");
	item_selectResearch8:SetRaiseEvents("DawnOfCivilizationResearchCompleted");
	item_selectResearch8:SetIsQueueable(true)
	item_selectResearch8:SetAdvisorMessage("ADVISOR_LINE_FTUE_7ALT");
	item_selectResearch8:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_7ALT");
	item_selectResearch8:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_7ALT")
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_selectResearch8:SetUITriggers("ActionPanel", "TutorialSelectEndTurnG");
	item_selectResearch8:SetNextTutorialItemId("SELECT_RESEARCH_9");
	item_selectResearch8:SetIsDoneEvents("ResearchChooser_ForceHideWorldTracker");
	item_selectResearch8:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));
	item_selectResearch8:SetShowPortrait(true);
	

	-- =============================== SELECT_RESEARCH_9 =====================================
	local item_selectResearch9:TutorialItem = TutorialItem:new("SELECT_RESEARCH_9");
	item_selectResearch9:SetPrereqs("SELECT_RESEARCH_8");
	item_selectResearch9:SetAdvisorMessage("ADVISOR_LINE_FTUE_71");
	item_selectResearch9:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_71");
	item_selectResearch9:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_71")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_selectResearch9:SetShowPortrait(true)
	item_selectResearch9:SetIsDoneFunction(
		function()
			return false;
		end );
	item_selectResearch9:SetNextTutorialItemId("SELECT_RESEARCH_A");

	-- =============================== SELECT_RESEARCH_A =====================================
	local item_selectResearchA:TutorialItem = TutorialItem:new("SELECT_RESEARCH_A");
	item_selectResearchA:SetPrereqs("SELECT_RESEARCH_9");
	item_selectResearchA:SetAdvisorMessage("LOC_META_167_BODY");
	item_selectResearchA:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			LuaEvents.Tutorial_ResearchOpen();
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_selectResearchA:SetUITriggers("ResearchChooser", "TutorialSelectResearch");
	item_selectResearchA:SetEnabledControls(UITutorialManager:GetHash("TECH_MINING"));
	item_selectResearchA:SetIsDoneEvents("ResearchChanged");
	item_selectResearchA:SetNextTutorialItemId("MINING_SELECTED");

	-- ================================ MINING_SELECTED =====================================
	local item_miningSelected:TutorialItem = TutorialItem:new("MINING_SELECTED");
	item_miningSelected:SetPrereqs("SELECT_RESEARCH_9");
	item_miningSelected:SetAdvisorMessage("ADVISOR_LINE_FTUE_8ALT");
	item_miningSelected:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_8ALT");
	item_miningSelected:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_8ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_miningSelected:SetIsDoneFunction(
		function()
			return false;
		end );
	item_miningSelected:SetNextTutorialItemId("MINING_SELECTED_B");
	item_miningSelected:SetShowPortrait(true)
	item_miningSelected:SetOpenFunction(
		function()
			LockResearch();			
		end );

	-- =============================== MINING_SELECTED_B =====================================
	local item_miningSelectedB:TutorialItem = TutorialItem:new("MINING_SELECTED_B");
	item_miningSelectedB:SetPrereqs("MINING_SELECTED");
	item_miningSelectedB:SetAdvisorMessage("LOC_META_111_BODY");
	item_miningSelectedB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_miningSelectedB:SetIsDoneFunction(
		function()
			return false;
		end );
	--item_miningSelectedB:SetUITriggers("TopPanel", "TutorialSelectEndTurnB");
	item_miningSelectedB:SetNextTutorialItemId("MINING_SELECTED_C");

	-- =============================== MINING_SELECTED_C =====================================
	local item_miningSelectedC:TutorialItem = TutorialItem:new("MINING_SELECTED_C");
	item_miningSelectedC:SetPrereqs("MINING_SELECTED_B");
	item_miningSelectedC:SetAdvisorMessage("LOC_META_112_BODY");
	item_miningSelectedC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_miningSelectedC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_miningSelectedC:SetNextTutorialItemId("SELECT_END_TURN_B");

	-- =============================== SELECT_END_TURN_B =====================================
	local item_selectEndTurnB:TutorialItem = TutorialItem:new("SELECT_END_TURN_B");
	item_selectEndTurnB:SetPrereqs("MINING_SELECTED_C");
	item_selectEndTurnB:SetIsEndOfChain(true);
	--item_selectEndTurnB:SetRaiseEvents("EndTurnDirty");
	--item_selectEndTurnB:SetRaiseFunction( IsTurnFinished );
	item_selectEndTurnB:SetIsDoneEvents("LocalPlayerTurnEnd");
	item_selectEndTurnB:SetUITriggers("ActionPanel", "TutorialSelectEndTurn");
	item_selectEndTurnB:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));

	-- =============================== SELECT_WARRIOR =====================================
	local item_selectWarrior:TutorialItem = TutorialItem:new("SELECT_WARRIOR");
	--item_selectWarrior:SetPrereqs("SELECT_END_TURN_B");
	item_selectWarrior:SetRaiseEvents("CapitalWarriorProductionCompleted");
	item_selectWarrior:SetIsQueueable(true)
	item_selectWarrior:SetAdvisorMessage("ADVISOR_LINE_FTUE_9ALT");
	item_selectWarrior:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_9ALT");
	item_selectWarrior:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_9ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_selectWarrior:SetIsDoneFunction(
		function()
			return false;
		end );
	item_selectWarrior:SetNextTutorialItemId("SELECT_WARRIOR_B");
	item_selectWarrior:SetShowPortrait(true)
	item_selectWarrior:SetOpenFunction(
		function()
			UserConfiguration.ShowMapResources(false);
		end );

	-- ================================ SELECT_WARRIOR_B =====================================
	local item_selectWarriorB:TutorialItem = TutorialItem:new("SELECT_WARRIOR_B");
	item_selectWarriorB:SetPrereqs("SELECT_WARRIOR");
	item_selectWarriorB:SetAdvisorMessage("ADVISOR_LINE_FTUE_92");
	item_selectWarriorB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_92");
	item_selectWarriorB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_92")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_selectWarriorB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_selectWarriorB:SetNextTutorialItemId("SELECT_WARRIOR_B2");
	item_selectWarriorB:SetShowPortrait(true)

	-- =============================== SELECT_WARRIOR_B2 =====================================
	local item_selectWarriorB2:TutorialItem = TutorialItem:new("SELECT_WARRIOR_B2");
	item_selectWarriorB2:SetPrereqs("SELECT_WARRIOR_B");
	item_selectWarriorB2:SetAdvisorMessage("LOC_META_113_BODY");
	item_selectWarriorB2:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			local pUnit:table = CenterOnFirstUnit( true );
			UI.DeselectAllUnits();
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_selectWarriorB2:SetIsDoneFunction(
		function()
			LuaEvents.Tutorial_DisableMapDrag( false );
			ClearDimHexes();
		end );
	item_selectWarriorB2:SetAdvisorCallout("LOC_META_9_HEAD", "LOC_META_9_BODY",
		function()
			return GetPlotOfUnit(GetFirstUnitOfType("UNIT_WARRIOR")):GetIndex();
		end);
	item_selectWarriorB2:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput");
	item_selectWarriorB2:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"));
	item_selectWarriorB2:SetOverlayEnabled( false );
	item_selectWarriorB2:SetIsDoneEvents("UnitSelectionChanged");
	item_selectWarriorB2:SetIsDoneFunction( UnitNotCityBuilder );
	item_selectWarriorB2:SetNextTutorialItemId("MOVE_WARRIOR");

	-- =============================== MOVE_WARRIOR =====================================
	local item_moveWarrior:TutorialItem = TutorialItem:new("MOVE_WARRIOR");
	item_moveWarrior:SetPrereqs("SELECT_WARRIOR");
	item_moveWarrior:SetAdvisorMessage("ADVISOR_LINE_FTUE_94");
	item_moveWarrior:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_94");
	item_moveWarrior:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.LookAtPlot(15,12);
			UI.SetMapZoom(0.3, 0.0, 0.0);
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_94")
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_moveWarrior:SetOpenFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true );
			ForceMoveUnitOnePlot();
		end );
	item_moveWarrior:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
			EndMovementRestriction();
		end );
	item_moveWarrior:SetAdvisorCallout("LOC_META_10_HEAD", "LOC_META_10_BODY",
		function()
			local unit = GetFirstUnitOfType("UNIT_WARRIOR");
			return Map.GetPlot(unit:GetX() + 1, unit:GetY()):GetIndex();
		end);
	item_moveWarrior:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput", "UnitPanel");
	item_moveWarrior:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item_moveWarrior:SetShowPortrait(true)
	item_moveWarrior:SetOverlayEnabled( false );
	item_moveWarrior:SetIsDoneEvents("UnitKilledInCombat");
	item_moveWarrior:SetNextTutorialItemId("BARBARIAN_KILLED");

	-- ================================ BARBARIAN_KILLED =====================================
	local item_barbarianKilled:TutorialItem = TutorialItem:new("BARBARIAN_KILLED");
	item_barbarianKilled:SetPrereqs("MOVE_WARRIOR");
	item_barbarianKilled:SetAdvisorMessage("ADVISOR_LINE_FTUE_10ALT");
	item_barbarianKilled:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_10ALT");
	item_barbarianKilled:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_10ALT");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_barbarianKilled:SetIsDoneFunction(
		function()
			return false;
		end );
	item_barbarianKilled:SetNextTutorialItemId("WARRIORS_COMPLETE");
	item_barbarianKilled:SetShowPortrait(true)

	-- ================================ WARRIORS_COMPLETE =====================================
	local item_trainBuilder:TutorialItem = TutorialItem:new("WARRIORS_COMPLETE");
	item_trainBuilder:SetPrereqs("BARBARIAN_KILLED");
	item_trainBuilder:SetAdvisorMessage("ADVISOR_LINE_FTUE_12ALT");
	item_trainBuilder:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_12ALT");
	item_trainBuilder:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_12ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_trainBuilder:SetIsDoneFunction(
		function()
			return false;
		end );
	item_trainBuilder:SetNextTutorialItemId("NOTIFICATION_PANEL");
	item_trainBuilder:SetShowPortrait(true);
	item_trainBuilder:SetOpenFunction(
		function()
			UI.SetMapZoom(0.7, 0.0, 0.0);
			UserConfiguration.ShowMapResources(true);
		end );

	-- ================================ NOTIFICATION_PANEL =====================================
	local item:TutorialItem = TutorialItem:new("NOTIFICATION_PANEL");
	item:SetPrereqs("WARRIORS_COMPLETE");
	item:SetAdvisorMessage("LOC_META_11a_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("ActionPanel", "TutorialNotificationPointer");
	item:SetNextTutorialItemId("SELECT_END_TURN_PRODUCTION");

	-- =============================== SELECT_END_TURN_PRODUCTION =====================================
	local item:TutorialItem = TutorialItem:new("SELECT_END_TURN_PRODUCTION");
	item:SetPrereqs("NOTIFICATION_PANEL");
	item:SetRaiseEvents("EndTurnDirty");
	item:SetIsDoneEvents("ProductionPanelOpen");
	item:SetUITriggers("ActionPanel", "TutorialSelectEndTurnC");
	item:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));
	item:SetNextTutorialItemId("SHOULD_TRAIN_BUILDER");

	-- ================================ SHOULD_TRAIN_BUILDER =====================================
	local item_trainBuilder:TutorialItem = TutorialItem:new("SHOULD_TRAIN_BUILDER");
	item_trainBuilder:SetPrereqs("SELECT_END_TURN_PRODUCTION");
	item_trainBuilder:SetAdvisorMessage("ADVISOR_LINE_FTUE_13ALT");
	item_trainBuilder:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_13ALT");
	item_trainBuilder:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_13ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_trainBuilder:SetIsDoneFunction(
		function()
			return false;
		end );
	item_trainBuilder:SetNextTutorialItemId("TRAIN_BUILDER");
	item_trainBuilder:SetShowPortrait(true)

	-- =============================== TRAIN_BUILDER =====================================
	local item_trainBuilder:TutorialItem = TutorialItem:new("TRAIN_BUILDER");
	item_trainBuilder:SetPrereqs("SHOULD_TRAIN_BUILDER");
	item_trainBuilder:SetAdvisorMessage("LOC_ADVISOR_LINE_FTUE_14");
	item_trainBuilder:SetUITriggers("ChooseProductionMenu", "TutorialTrainBuilders");
	item_trainBuilder:SetEnabledControls( UITutorialManager:GetHash("UNIT_BUILDER") );
	item_trainBuilder:SetIsDoneEvents("CityProductionChanged_Builder");
	item_trainBuilder:SetNextTutorialItemId("TRAIN_BUILDER_B");

	-- =============================== TRAIN_BUILDER_B =====================================
	local item_trainBuilderB:TutorialItem = TutorialItem:new("TRAIN_BUILDER_B");
	item_trainBuilderB:SetPrereqs("TRAIN_BUILDER");
	item_trainBuilderB:SetAdvisorMessage("ADVISOR_LINE_FTUE_121");
	item_trainBuilderB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_121");
	item_trainBuilderB:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LockProduction();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_121")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_trainBuilderB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_trainBuilderB:SetShowPortrait(true)
	item_trainBuilderB:SetNextTutorialItemId("SELECT_END_TURN_C");

	-- =============================== SELECT_END_TURN_C =====================================
	local item_selectEndTurnC:TutorialItem = TutorialItem:new("SELECT_END_TURN_C");
	item_selectEndTurnC:SetPrereqs("TRAIN_BUILDER");
	item_selectEndTurnC:SetIsEndOfChain(true)
	item_selectEndTurnC:SetAdvisorMessage("LOC_META_13a_BODY");
	item_selectEndTurnC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_selectEndTurnC:SetRaiseEvents("EndTurnDirty");
	item_selectEndTurnC:SetIsDoneEvents("LocalPlayerTurnEnd");
	item_selectEndTurnC:SetUITriggers("ActionPanel", "TutorialSelectEndTurnD");
	item_selectEndTurnC:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));

	-- =============================== EXPLORE_A =====================================
	local item_exploreA:TutorialItem = TutorialItem:new("EXPLORE_A");
	--item_exploreA:SetPrereqs("SELECT_END_TURN_C");
	item_exploreA:SetPrereqs("SELECT_WARRIOR");
	item_exploreA:SetIsQueueable(true)
	item_exploreA:SetRaiseEvents("LocalPlayerTurnBegin");
	item_exploreA:SetAdvisorMessage("ADVISOR_LINE_FTUE_14_ALT");
	item_exploreA:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_14_ALT");
	item_exploreA:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_14_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_exploreA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_exploreA:SetNextTutorialItemId("EXPLORE_A2");
	item_exploreA:SetShowPortrait(true)

	-- =============================== EXPLORE_A2 =====================================
	local item_exploreA2:TutorialItem = TutorialItem:new("EXPLORE_A2");
	item_exploreA2:SetPrereqs("EXPLORE_A");
	item_exploreA2:SetAdvisorMessage("LOC_META_14_BODY");
	item_exploreA2:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_exploreA2:SetIsDoneFunction(
		function()
			return false;
		end );
	item_exploreA2:SetNextTutorialItemId("EXPLORE_B");

	-- =============================== EXPLORE_B =====================================
	local item_selectWarriorB:TutorialItem = TutorialItem:new("EXPLORE_B");
	item_selectWarriorB:SetPrereqs("EXPLORE_A");
	--item_selectWarriorB:SetRaiseEvents("CityProductionCompleted");
	item_selectWarriorB:SetAdvisorMessage("ADVISOR_LINE_FTUE_15ALT");
	item_selectWarriorB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_15ALT");
	item_selectWarriorB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			CenterOnFirstUnit( true );
			UI.DeselectAllUnits();
			LuaEvents.Tutorial_DisableMapDrag( true );
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_15ALT")
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_selectWarriorB:SetIsDoneEvents("UnitSelectionChanged");
	item_selectWarriorB:SetIsDoneFunction( UnitNotCityBuilder );
	item_selectWarriorB:SetCleanupFunction(
		function()
			LuaEvents.Tutorial_DisableMapDrag( false );
			ClearDimHexes();
		end );
	item_selectWarriorB:SetAdvisorCallout("LOC_META_9_HEAD", "LOC_META_9_BODY",
		function()
			return GetPlotOfUnit(GetFirstUnitOfType("UNIT_WARRIOR")):GetIndex();
		end);
	item_selectWarriorB:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput");
	item_selectWarriorB:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"));
	item_selectWarriorB:SetOverlayEnabled( false );
	item_selectWarriorB:SetShowPortrait(true)
	item_selectWarriorB:SetNextTutorialItemId("MOVEMENT_RULES_A");

	-- =============================== MOVEMENT_RULES_A =====================================
	local item_movementRulesA:TutorialItem = TutorialItem:new("MOVEMENT_RULES_A");
	item_movementRulesA:SetPrereqs("EXPLORE_B");
	item_movementRulesA:SetAdvisorMessage("LOC_META_16_BODY");
	item_movementRulesA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_movementRulesA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_movementRulesA:SetNextTutorialItemId("MOVEMENT_RULES_A2");

	-- ================================ MOVEMENT_RULES_A2 =====================================
	local item_movementRulesA2:TutorialItem = TutorialItem:new("MOVEMENT_RULES_A2");
	item_movementRulesA2:SetPrereqs("MOVEMENT_RULES_A");
	item_movementRulesA2:SetAdvisorMessage("ADVISOR_LINE_FTUE_151");
	item_movementRulesA2:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_151");
	item_movementRulesA2:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_151")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_movementRulesA2:SetIsDoneFunction(
		function()
			return false;
		end );
	item_movementRulesA2:SetNextTutorialItemId("MOVEMENT_RULES_B");
	item_movementRulesA2:SetShowPortrait(true)

	-- =============================== MOVEMENT_RULES_B =====================================
	local item_movementRulesB:TutorialItem = TutorialItem:new("MOVEMENT_RULES_B");
	item_movementRulesB:SetPrereqs("MOVEMENT_RULES_A2");
	item_movementRulesB:SetAdvisorMessage("LOC_META_17_BODY");
	item_movementRulesB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_movementRulesB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_movementRulesB:SetNextTutorialItemId("MOVE_WARRIOR_B");

	-- =============================== MOVE_WARRIOR_B =====================================
	local item_moveWarriorB:TutorialItem = TutorialItem:new("MOVE_WARRIOR_B");
	item_moveWarriorB:SetPrereqs("MOVEMENT_RULES_B");
	item_moveWarriorB:SetOpenFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true );
			ForceMoveUnitRelative(1, 1)
		end );
	item_moveWarriorB:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
			EndMovementRestriction();
		end );
	item_moveWarriorB:SetAdvisorCallout("LOC_META_17b_HEAD", "LOC_META_17b_BODY",
		function()
			local unit = GetFirstUnitOfType("UNIT_WARRIOR")
			return Map.GetPlot(unit:GetX() + 1, unit:GetY() + 1):GetIndex();
		end);
	item_moveWarriorB:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput", "UnitPanel");
	item_moveWarriorB:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item_moveWarriorB:SetOverlayEnabled( false );
	item_moveWarriorB:SetIsDoneEvents("UnitMoveComplete");
	item_moveWarriorB:SetNextTutorialItemId("GOODY_HUT_DISCOVERED");

	-- =============================== GOODY_HUT_DISCOVERED =====================================
	local item_goodyHutDiscovered:TutorialItem = TutorialItem:new("GOODY_HUT_DISCOVERED");
	item_goodyHutDiscovered:SetPrereqs("MOVE_WARRIOR_B");
	item_goodyHutDiscovered:SetRaiseEvents("WarriorFoundGoodyHut");
	--item_goodyHutDiscovered:SetRaiseEvents("GoodyHutDiscovered");  -- Cannot use GoodyHutDiscovered event because it happens before the preceeding UnitMoveComplete happens.
	item_goodyHutDiscovered:SetAdvisorMessage("ADVISOR_LINE_FTUE_153");
	item_goodyHutDiscovered:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_153");
	item_goodyHutDiscovered:AddAdvisorButton("LOC_ADVISOR_BUTTON_TELL_ME_MORE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_153")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
			DisableInputFiltering();								-- DEBUG: Input resumes to normal state!
		end );
	item_goodyHutDiscovered:SetIsDoneFunction(
		function()
			return false;
		end );
	item_goodyHutDiscovered:SetNextTutorialItemId("TRIBAL_VILLAGES_A");
	item_goodyHutDiscovered:SetShowPortrait(true)
	item_goodyHutDiscovered:SetOpenFunction(
		function()
			UI.LookAtPlot(16,14);
			UI.SetMapZoom(0.2, 0.0, 0.0);
		end );

	-- =============================== TRIBAL_VILLAGES_A =====================================
	local item_tribalVillagesA:TutorialItem = TutorialItem:new("TRIBAL_VILLAGES_A");
	item_tribalVillagesA:SetPrereqs("GOODY_HUT_DISCOVERED");
	item_tribalVillagesA:SetAdvisorMessage("LOC_META_18_BODY");
	item_tribalVillagesA:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_tribalVillagesA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_tribalVillagesA:SetNextTutorialItemId("TRIBAL_VILLAGES_B");

	-- =============================== TRIBAL_VILLAGES_B =====================================
	local item_tribalVillagesB:TutorialItem = TutorialItem:new("TRIBAL_VILLAGES_B");
	item_tribalVillagesB:SetPrereqs("TRIBAL_VILLAGES_A");
	item_tribalVillagesB:SetAdvisorMessage("ADVISOR_LINE_FTUE_154");
	item_tribalVillagesB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_154");
	item_tribalVillagesB:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_154")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_tribalVillagesB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_tribalVillagesB:SetShowPortrait(true)
	item_tribalVillagesB:SetNextTutorialItemId("TRIBAL_VILLAGES_C");

	-- =============================== TRIBAL_VILLAGES_C =====================================
	local item_tribalVillagesC:TutorialItem = TutorialItem:new("TRIBAL_VILLAGES_C");
	item_tribalVillagesC:SetPrereqs("TRIBAL_VILLAGES_B");
	item_tribalVillagesC:SetAdvisorMessage("LOC_META_19_BODY");
	item_tribalVillagesC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_tribalVillagesC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_tribalVillagesC:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
			UI.SetMapZoom(0.7, 0.0, 0.0);
		end );
	item_tribalVillagesC:SetNextTutorialItemId("SELECT_END_TURN_D");

	-- =============================== SELECT_END_TURN_D =====================================
	local item_selectEndTurnD:TutorialItem = TutorialItem:new("SELECT_END_TURN_D");
	item_selectEndTurnD:SetPrereqs("TRIBAL_VILLAGES_B");
	item_selectEndTurnD:SetIsEndOfChain(true)
	item_selectEndTurnD:SetRaiseEvents("EndTurnDirty");
	item_selectEndTurnD:SetIsDoneEvents("LocalPlayerTurnEnd");
	item_selectEndTurnD:SetUITriggers("ActionPanel", "TutorialSelectEndTurnE");
	item_selectEndTurnD:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));

	-- =============================== MOVE_WARRIOR_C =====================================
	local item_moveWarriorC:TutorialItem = TutorialItem:new("MOVE_WARRIOR_C");
	item_moveWarriorC:SetPrereqs("TRIBAL_VILLAGES_C");
	item_moveWarriorC:SetRaiseEvents("LocalPlayerTurnBegin");
	item_moveWarriorC:SetAdvisorMessage("ADVISOR_FTUE_47_ALT");
	item_moveWarriorC:SetAdvisorAudio("Play_ADVISOR_FTUE_47_ALT");
	item_moveWarriorC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK", 
		function( advisorInfo )
			local unit = GetFirstUnitOfType("UNIT_WARRIOR");
			UI.SelectUnit(unit);
			UI.PlaySound("Stop_ADVISOR_FTUE_47_ALT")
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true );
			ForceMoveUnitDirection(DirectionTypes.DIRECTION_NORTHWEST);
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_moveWarriorC:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
			EndMovementRestriction();
		end );
	item_moveWarriorC:SetAdvisorCallout("LOC_META_20_HEAD", "LOC_META_20_BODY",
		function()
			local unit = GetFirstUnitOfType("UNIT_WARRIOR");
			return Map.GetAdjacentPlot(unit:GetX(), unit:GetY(), DirectionTypes.DIRECTION_NORTHWEST)
		end);
	item_moveWarriorC:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput", "UnitPanel");
	item_moveWarriorC:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item_moveWarriorC:SetOverlayEnabled( false );
	item_moveWarriorC:SetShowPortrait(true)
	item_moveWarriorC:SetIsDoneEvents("UnitMoveComplete");
	item_moveWarriorC:SetNextTutorialItemId("SCOUTS_A");

	-- =============================== SCOUTS_A =====================================
	local item_scoutsA:TutorialItem = TutorialItem:new("SCOUTS_A");
	item_scoutsA:SetPrereqs("MOVE_WARRIOR_C");
	item_scoutsA:SetAdvisorMessage("ADVISOR_LINE_FTUE_16_ALT");
	item_scoutsA:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_16_ALT");
	item_scoutsA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_16_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_scoutsA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_scoutsA:SetNextTutorialItemId("SCOUTS_A2");
	item_scoutsA:SetShowPortrait(true)

	-- =============================== SCOUTS_A2 =====================================
	local item_scoutsA2:TutorialItem = TutorialItem:new("SCOUTS_A2");
	item_scoutsA2:SetPrereqs("SCOUTS_A");
	item_scoutsA2:SetAdvisorMessage("LOC_META_114_BODY");
	item_scoutsA2:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_scoutsA2:SetOpenFunction(
		function()
			AddUnitHexRestriction( "UNIT_SCOUT", 14, 13 );				-- Scout cannot block the warrior
			UI.LookAtPlot(14,12);
			local unit = GetFirstUnitOfType("UNIT_SCOUT");
			UI.SelectUnit(unit);
			UI.SetMapZoom(0.5, 0.0, 0.0);
		end );
	item_scoutsA2:SetIsDoneFunction(
		function()
			return false;
		end );
	item_scoutsA2:SetNextTutorialItemId("SCOUTS_B");

	-- =============================== SCOUTS_B =====================================
	local item_scoutsB:TutorialItem = TutorialItem:new("SCOUTS_B");
	item_scoutsB:SetPrereqs("SCOUTS_A2");
	item_scoutsB:SetAdvisorMessage("ADVISOR_LINE_FTUE_17_ALT");
	item_scoutsB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_17_ALT");
	item_scoutsB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			--CenterOnFirstUnit( true );
			--UI.DeselectAllUnits();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_17_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_scoutsB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_scoutsB:SetNextTutorialItemId("SCOUTS_C");
	item_scoutsB:SetShowPortrait(true)

	-- =============================== SCOUTS_C =====================================
	local item_scoutsC:TutorialItem = TutorialItem:new("SCOUTS_C");
	item_scoutsC:SetPrereqs("SCOUTS_B");
	item_scoutsC:SetAdvisorMessage("LOC_META_21_BODY");
	item_scoutsC:SetOpenFunction(
		function()
			UI.SetMapZoom(0.7, 0.0, 0.0);
		end );
	item_scoutsC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_scoutsC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_scoutsC:SetNextTutorialItemId("SCOUTS_D");

	-- =============================== SCOUTS_D =====================================
	local item_scoutsD:TutorialItem = TutorialItem:new("SCOUTS_D");
	item_scoutsD:SetPrereqs("SCOUTS_C");
	item_scoutsD:SetAdvisorMessage("ADVISOR_LINE_FTUE_18_ALT");
	item_scoutsD:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_18_ALT");
	item_scoutsD:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_18_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_scoutsD:SetIsDoneFunction(
		function()
			return false;
		end );
	item_scoutsD:SetShowPortrait(true);
	item_scoutsD:SetNextTutorialItemId("SCOUTS_D2");

	-- =============================== SCOUTS_D2 =====================================	
	local item_scoutsD2:TutorialItem = TutorialItem:new("SCOUTS_D2");
	item_scoutsD2:SetPrereqs("SCOUTS_D");
	item_scoutsD2:SetUITriggers("ActionPanel", "WorldInput");
	item_scoutsD2:SetIsDoneEvents("ScoutMoved");
	item_scoutsD2:SetNextTutorialItemId("SCOUTS_E");

	-- =============================== SCOUTS_E =====================================
	local item_scoutsE:TutorialItem = TutorialItem:new("SCOUTS_E");
	item_scoutsE:SetPrereqs("SCOUTS_D2");
	item_scoutsE:SetIsEndOfChain(true);
	item_scoutsE:SetRaiseEvents("ScoutMoved");
	item_scoutsE:SetIsDoneEvents("LocalPlayerTurnEnd");
	item_scoutsE:SetUITriggers("ActionPanel", "TutorialSelectEndTurnE");
	item_scoutsE:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));

	-- =============================== BUILDERS_A =====================================
	local item_buildersA:TutorialItem = TutorialItem:new("BUILDERS_A");
	item_buildersA:SetRaiseEvents("CapitalBuilderProductionCompleted");
	item_buildersA:SetIsQueueable(true);
	item_buildersA:SetAdvisorMessage("ADVISOR_LINE_FTUE_19_ALT");
	item_buildersA:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_19_ALT");
	item_buildersA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			local localPlayer = Game.GetLocalPlayer();
			local player = Players[localPlayer];
			local playerUnits = player:GetUnits();

			for i, unit in playerUnits:Members() do
				local unitTypeName = UnitManager.GetTypeName(unit);

				if "UNIT_BUILDER" == unitTypeName then
					local plot = Map.GetPlot(unit:GetX(), unit:GetY());
					UI.LookAtPlot(plot);
					UI.SelectUnit(unit);
				end
			end

			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_19_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_buildersA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_buildersA:SetNextTutorialItemId("BUILDERS_B");
	item_buildersA:SetShowPortrait(true)
	item_buildersA:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
		end );

	-- =============================== BUILDERS_B =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_B");
	item:SetPrereqs("BUILDERS_A");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_191");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_191");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_191");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetNextTutorialItemId("BUILDERS_C");

	-- =============================== BUILDERS_C =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_C");
	item:SetPrereqs("BUILDERS_B");
	item:SetAdvisorMessage("LOC_META_22_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.LookAtPlot(14,11);
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );	
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("BUILDERS_D");

	-- =============================== BUILDERS_D =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_D");
	item:SetPrereqs("BUILDERS_C");
	item:SetOpenFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true );
			ForceMoveUnitDirection(DirectionTypes.DIRECTION_SOUTHEAST)
		end );
	item:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
			EndMovementRestriction();
		end );
	item:SetAdvisorCallout("LOC_META_23_HEAD", "LOC_META_23_BODY",
		function()
			local unit = GetFirstUnitOfType("UNIT_BUILDER")
			return Map.GetAdjacentPlot(unit:GetX(), unit:GetY(), DirectionTypes.DIRECTION_SOUTHEAST)
		end);
	item:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput", "UnitPanel");
	item:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item:SetOverlayEnabled( false );
	item:SetIsDoneEvents("UnitMoveComplete");
	item:SetNextTutorialItemId("BUILDERS_E");

	-- =============================== BUILDERS_E =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_E");
	item:SetPrereqs("BUILDERS_D");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_192");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_192");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_192");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,11);
			DisableUnitAction( "UNITOPERATION_MOVE_TO", "UNIT_BUILDER");
		end );
	item:SetNextTutorialItemId("BUILDERS_F");

	-- ================================ BUILDERS_F =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_F");
	item:SetPrereqs("BUILDERS_E");
	item:SetAdvisorMessage("LOC_META_24_BODY");
	item:SetUITriggers("UnitPanel", "TutorialBuildFarmAction");
	--item:SetEnabledControls(UnitOperationTypes.BUILD_IMPROVEMENT);  -- FIXME: This does not appear to work.
	item:SetIsDoneEvents("ImprovementAddedToMap");
	item:SetNextTutorialItemId("BUILDERS_G");

	-- ================================ BUILDERS_G =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_G");
	item:SetPrereqs("BUILDERS_F");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_193");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_193");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_193");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,11);
			EnableUnitAction( "UNITOPERATION_MOVE_TO", "UNIT_BUILDER");
		end );
	item:SetNextTutorialItemId("BUILDERS_H");

	-- ================================ BUILDERS_H =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_H");
	item:SetPrereqs("BUILDERS_G");
	item:SetAdvisorMessage("LOC_META_25_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,11);
			ShowYieldIcons( true );
			UI.SetFixedTiltMode(true);
		end );
	item:SetNextTutorialItemId("BUILDERS_I");

	-- ================================ BUILDERS_I =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_I");
	item:SetPrereqs("BUILDERS_H");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_194");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_194");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_194");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetOpenFunction(
		function()
			UI.SetFixedTiltMode(false);
			ShowYieldIcons( false );
		end );
	item:SetNextTutorialItemId("BUILDERS_J");

	-- ================================ BUILDERS_J =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_J");
	item:SetPrereqs("BUILDERS_I");
	item:SetAdvisorMessage("LOC_META_26_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			local playerID = Game.GetLocalPlayer();
			local player = Players[playerID];
			local playerUnits = player:GetUnits()
			for i, unit in playerUnits:Members() do
				local unitTypeName = UnitManager.GetTypeName(unit)

				if (unitTypeName == "UNIT_BUILDER") then
					UI.SelectUnit(unit);
				end
			end
		end );
	item:SetNextTutorialItemId("BUILDERS_K");

	-- ================================ BUILDERS_K =====================================
	local item:TutorialItem = TutorialItem:new("BUILDERS_K");
	item:SetPrereqs("BUILDERS_J");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_20_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_20_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_20_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
		end );
	item:SetNextTutorialItemId("CONSTRUCTING_BUILDINGS_A");

	-- =============================== CONSTRUCTING_BUILDINGS_A =====================================
	-- Build a Monument
	local item:TutorialItem = TutorialItem:new("CONSTRUCTING_BUILDINGS_A");
	item:SetPrereqs("BUILDERS_K");
	item:SetAdvisorMessage("LOC_META_27_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
		end );
	item:SetNextTutorialItemId("CONSTRUCTING_BUILDINGS_B");

	-- =============================== CONSTRUCTING_BUILDINGS_B =====================================
	local item:TutorialItem = TutorialItem:new("CONSTRUCTING_BUILDINGS_B");
	item:SetPrereqs("CONSTRUCTING_BUILDINGS_A");
	item:SetOpenFunction(
		function( )
			local player = GetPlayer();
			if player == nil then
				UI.DataError("Unable to obtain player in Open City Panel tutorial item.");
			end
			local capitalCity = player:GetCities():GetCapitalCity();
			if capitalCity == nil then
				UI.DataError("Unable to obtain capital city in Open City Panel tutorial item.");
			end
			UI.SelectCity( capitalCity );	-- Immediate call instead of waiting for callback
			LuaEvents.Tutorial_CityPanelOpen();
		end );
	item:SetUITriggers("CityPanel", "TutorialOpenProduction" );
	item:SetEnabledControls(UITutorialManager:GetHash("ChangeProductionCheck"));
	item:SetIsDoneEvents("ProductionPanelViaCityOpen");
	item:SetNextTutorialItemId("CONSTRUCTING_BUILDINGS_C");

	-- =============================== CONSTRUCTING_BUILDINGS_C =====================================
	local item:TutorialItem = TutorialItem:new("CONSTRUCTING_BUILDINGS_C");	
	item:SetPrereqs("CONSTRUCTING_BUILDINGS_B");
	item:SetUITriggers("ChooseProductionMenu", "TutorialBuildMonument");
	item:SetEnabledControls( UITutorialManager:GetHash("BUILDING_MONUMENT") );
	item:SetIsDoneEvents("CityProductionChanged_Monument");

	-- =============================== CONSTRUCTING_BUILDINGS_D =====================================
	local item:TutorialItem = TutorialItem:new("CONSTRUCTING_BUILDINGS_D");	
	item:SetPrereqs("CONSTRUCTING_BUILDINGS_C");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_201");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_201");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LockProduction();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_201");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
		end );
	item:SetNextTutorialItemId("CONSTRUCTING_BUILDINGS_E");

	-- =============================== CONSTRUCTING_BUILDINGS_E =====================================
	local item:TutorialItem = TutorialItem:new("CONSTRUCTING_BUILDINGS_E");
	item:SetPrereqs("CONSTRUCTING_BUILDINGS_D");
	item:SetIsEndOfChain(true);
	item:SetAdvisorMessage("LOC_META_35_BODY");	-- "Continue exploring the world with your scout unit"
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );

	-- ================================ CITY_DEFENSE_A =====================================
	local item_cityDefenseA:TutorialItem = TutorialItem:new("CITY_DEFENSE_A");
	--item_cityDefenseA:SetPrereqs("BUILD_MONUMENT");
	item_cityDefenseA:SetPrereqs("SCOUTS_A");
	item_cityDefenseA:SetIsQueueable(true);
	item_cityDefenseA:SetRaiseEvents("LocalPlayerTurnBegin");
	item_cityDefenseA:SetAdvisorMessage("ADVISOR_LINE_FTUE_21_ALT");
	item_cityDefenseA:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_21_ALT");
	item_cityDefenseA:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			local localPlayer = Game.GetLocalPlayer()
			local player = Players[localPlayer]
			local playerUnits = player:GetUnits()
			for i, unit in playerUnits:Members() do
				local unitTypeName = UnitManager.GetTypeName(unit);
				if "UNIT_WARRIOR" == unitTypeName then
					local plot = Map.GetPlot(unit:GetX(), unit:GetY());
					UI.LookAtPlot(plot);
					UI.SelectUnit(unit);
				end
			end
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_21_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_cityDefenseA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_cityDefenseA:SetShowPortrait(true)
	item_cityDefenseA:SetOpenFunction(
		function()
			-- Prevent scout from returning to any hex around the city.
			AddUnitHexRestriction( "UNIT_SCOUT", 14, 11 );	-- Plane where farm is to be built
			AddUnitHexRestriction( "UNIT_SCOUT", 15, 12 );	-- Stone where mine to be built
			AddUnitHexRestriction( "UNIT_SCOUT", 14, 13 );
			AddUnitHexRestriction( "UNIT_SCOUT", 13, 13 );
			AddUnitHexRestriction( "UNIT_SCOUT", 13, 12 );
			AddUnitHexRestriction( "UNIT_SCOUT", 13, 11 );
			AddUnitHexRestriction( "UNIT_SCOUT", 15, 13 );
			AddUnitHexRestriction( "UNIT_SCOUT", 18, 11 );  -- Location of second city
		end );
	item_cityDefenseA:SetNextTutorialItemId("CITY_DEFENSE_B");

	-- =============================== CITY_DEFENSE_B =====================================
	local item_cityDefenseB:TutorialItem = TutorialItem:new("CITY_DEFENSE_B");
	item_cityDefenseB:SetPrereqs("CITY_DEFENSE_A");
	item_cityDefenseB:SetAdvisorMessage("LOC_META_28a_BODY");
	item_cityDefenseB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_cityDefenseB:AddGoal("GOAL_2", "LOC_TUTORIAL_GOAL_2", "LOC_TUTORIAL_GOAL_TOOLTIP_2");
	item_cityDefenseB:SetOpenFunction(
		function( )			
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true );
			ForceMoveUnitToCapital();
		end );
	item_cityDefenseB:SetUITriggers("UnitPanel", "TutorialMoveToTileAction");
	item_cityDefenseB:SetAdvisorCallout("LOC_META_28_HEAD", "LOC_META_28_BODY",
		function()
			local player = GetPlayer();
			local capitalCity = player:GetCities():GetCapitalCity();
			return GetPlotOfUnit(capitalCity):GetIndex();
		end);
	item_cityDefenseB:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item_cityDefenseB:SetOverlayEnabled( false );
	item_cityDefenseB:SetIsDoneEvents("MultiMoveToCity");
	item_cityDefenseB:SetNextTutorialItemId("CITY_DEFENSE_C");

	-- =============================== CITY_DEFENSE_C =====================================
	local item:TutorialItem = TutorialItem:new("CITY_DEFENSE_C");
	item:SetPrereqs("CITY_DEFENSE_B");
	item:SetUITriggers("UnitFlagManager", "WorldInput", "UnitPanel", "TutorialMoveToTileAction");
	item:SetAdvisorCallout("LOC_META_28_HEAD", "LOC_META_28_BODY",
		function()
			local player = GetPlayer();
			local capitalCity = player:GetCities():GetCapitalCity();
			return Map.GetPlot(capitalCity:GetX(), capitalCity:GetY()):GetIndex();
		end);
	item:SetCleanupFunction(
		function( )		
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
			EndMovementRestriction();			
		end );
	item:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item:SetOverlayEnabled( false );
	item:SetIsDoneEvents("UnitMoveComplete");
	item:SetNextTutorialItemId("MOVE_SCOUT");

	-- ================================ MOVE_SCOUT =====================================
	local item_moveScout:TutorialItem = TutorialItem:new("MOVE_SCOUT");
	item_moveScout:SetPrereqs("CITY_DEFENSE_C");
	item_moveScout:SetIsEndOfChain(true)
	item_moveScout:SetAdvisorMessage("ADVISOR_LINE_FTUE_22_ALT");
	item_moveScout:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_22_ALT");
	item_moveScout:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_22_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_moveScout:SetIsDoneFunction(
		function()
			return false;
		end );
	item_moveScout:SetShowPortrait(true)
	item_moveScout:SetOpenFunction(
		function()
			SelectAndCenterOnUnit( "UNIT_SCOUT" );
			AddMapUnitMoveRestriction("UNIT_WARRIOR");	-- Restrict unit re-movement until back at the city.
			DisableUnitAction( "UNITOPERATION_MOVE_TO",	"UNIT_WARRIOR");
		end );

	-- ================================ MOVE_SCOUT_B =====================================
	local item_moveScoutB:TutorialItem = TutorialItem:new("MOVE_SCOUT_B");
	item_moveScoutB:SetPrereqs("MOVE_SCOUT");
	item_moveScoutB:SetRaiseEvents("UnitMoveComplete");
	item_moveScoutB:SetIsQueueable(true);
	item_moveScoutB:SetIsEndOfChain(true);
	item_moveScoutB:SetAdvisorMessage("ADVISOR_LINE_FTUE_23_ALT");
	item_moveScoutB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_23_ALT");
	item_moveScoutB:AddAdvisorButton("LOC_ADVISOR_BUTTON_VERY_GOOD",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_23_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_moveScoutB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_moveScoutB:SetShowPortrait(true)

	-- =============================== MINING_COMPLETE =====================================
	local item_miningComplete:TutorialItem = TutorialItem:new("MINING_COMPLETE");
	item_miningComplete:SetRaiseEvents("MiningResearchCompleted");
	item_miningComplete:SetIsQueueable(true);
	item_miningComplete:SetAdvisorMessage("ADVISOR_LINE_FTUE_24_ALT");
	item_miningComplete:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_24_ALT");
	item_miningComplete:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_24_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );			
		end );
	item_miningComplete:SetIsDoneFunction(
		function()
			return false;
		end );
	item_miningComplete:SetNextTutorialItemId("REVISIT_RESEARCH_A");
	item_miningComplete:SetShowPortrait(true)
	item_miningComplete:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
		end );

	-- =============================== REVISIT_RESEARCH_A =====================================
	local item_Revisit_Research_A:TutorialItem = TutorialItem:new("REVISIT_RESEARCH_A");
	item_Revisit_Research_A:SetPrereqs("MINING_COMPLETE");
	item_Revisit_Research_A:SetAdvisorMessage("LOC_META_116_BODY");
	item_Revisit_Research_A:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_Revisit_Research_A:SetIsDoneFunction(
		function()
			return false;
		end );
	item_Revisit_Research_A:SetNextTutorialItemId("REVISIT_RESEARCH_B");

	-- =============================== REVISIT_RESEARCH_B =====================================
	local item_Revisit_Research_B:TutorialItem = TutorialItem:new("REVISIT_RESEARCH_B");
	item_Revisit_Research_B:SetPrereqs("REVISIT_RESEARCH_A");
	item_Revisit_Research_B:SetAdvisorMessage("ADVISOR_LINE_FTUE_241");
	item_Revisit_Research_B:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_241");
	item_Revisit_Research_B:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_241");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_Revisit_Research_B:SetIsDoneFunction(
		function()
			return false;
		end );
	item_Revisit_Research_B:SetShowPortrait(true);
	item_Revisit_Research_B:SetNextTutorialItemId("SELECT_END_TURN_RESEARCH");

	-- =============================== SELECT_END_TURN_RESEARCH =====================================
	local item_selectEndTurnProduction:TutorialItem = TutorialItem:new("SELECT_END_TURN_RESEARCH");
	item_selectEndTurnProduction:SetPrereqs("REVISIT_RESEARCH_B");
	item_selectEndTurnProduction:SetRaiseEvents("EndTurnDirty");
	item_selectEndTurnProduction:SetUITriggers("ActionPanel", "TutSelectEndTurnActionI");
	item_selectEndTurnProduction:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));
	item_selectEndTurnProduction:SetNextTutorialItemId("SELECT_POTTERY_TECH");

	-- =============================== SELECT_POTTERY_TECH =====================================
	local item_selectPotteryTech:TutorialItem = TutorialItem:new("SELECT_POTTERY_TECH");
	item_selectPotteryTech:SetPrereqs("SELECT_END_TURN_RESEARCH");
	item_selectPotteryTech:SetUITriggers("ResearchChooser", "TutorialSelectResearchB");
	item_selectPotteryTech:SetEnabledControls(UITutorialManager:GetHash("TECH_POTTERY")); 

	--item_selectPotteryTech:SetIsDoneEvents("ResearchChooser_ForceHideWorldTracker");  -- TODO(asherburne): Create a new luaEvent in researchChooser specifically for this listener.
	item_selectPotteryTech:SetIsDoneEvents("ResearchChanged");
	item_selectPotteryTech:SetOpenFunction(
		function()
			-- Try to work around automatic unit selection cycling having closed the research panel.
			LuaEvents.Tutorial_ResearchOpen()
		end );
	item_selectPotteryTech:SetNextTutorialItemId("POTTERY_TECH_SELECTED_A");

	-- =============================== POTTERY_TECH_SELECTED_A =====================================
	local item_potteryTechSelected_A:TutorialItem = TutorialItem:new("POTTERY_TECH_SELECTED_A");
	item_potteryTechSelected_A:SetPrereqs("SELECT_POTTERY_TECH");
	item_potteryTechSelected_A:SetAdvisorMessage("ADVISOR_LINE_FTUE_242");
	item_potteryTechSelected_A:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_242");
	item_potteryTechSelected_A:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LockResearch();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_242");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_potteryTechSelected_A:SetIsDoneFunction(
		function()
			return false;
		end );
	item_potteryTechSelected_A:SetShowPortrait(true);
	item_potteryTechSelected_A:SetNextTutorialItemId("POTTERY_TECH_SELECTED_B");

	-- =============================== POTTERY_TECH_SELECTED_B =====================================
	local item_potteryTechSelected_B:TutorialItem = TutorialItem:new("POTTERY_TECH_SELECTED_B");
	item_potteryTechSelected_B:SetPrereqs("POTTERY_TECH_SELECTED_A");
	item_potteryTechSelected_B:SetAdvisorMessage("ADVISOR_LINE_FTUE_243");
	item_potteryTechSelected_B:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_243");
	item_potteryTechSelected_B:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_243");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_potteryTechSelected_B:SetIsDoneFunction(
		function()
			return false;
		end );
	item_potteryTechSelected_B:SetShowPortrait(true);
	item_potteryTechSelected_B:SetNextTutorialItemId("POTTERY_TECH_SELECTED_C");

	-- =============================== POTTERY_TECH_SELECTED_C =====================================
	local item_potteryTechSelected_C:TutorialItem = TutorialItem:new("POTTERY_TECH_SELECTED_C");
	item_potteryTechSelected_C:SetPrereqs("POTTERY_TECH_SELECTED_A");
	item_potteryTechSelected_C:SetAdvisorMessage("LOC_META_117_BODY");
	item_potteryTechSelected_C:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_potteryTechSelected_C:SetIsDoneFunction(
		function()
			return false;
		end );
	item_potteryTechSelected_C:SetIsEndOfChain(true);
	item_potteryTechSelected_C:SetOpenFunction(
		function()
			DisableUnitAction( "UNITOPERATION_MOVE_TO",	"UNIT_WARRIOR");
			local unit = GetFirstUnitOfType("UNIT_SCOUT");
			UI.SelectUnit(unit);
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true );
		end );

	-- =============================== SELECT_END_TURN_UNIT_ORDERS =====================================
	-- TODO(asherburne): Move the following pair of events to the first turn the scout becomes available.
--	local item_selectEndTurnUnitOrders:TutorialItem = TutorialItem:new("SELECT_END_TURN_UNIT_ORDERS");
--	item_selectEndTurnUnitOrders:SetPrereqs("SELECT_RESEARCH_B");
--	item_selectEndTurnUnitOrders:SetRaiseEvents("EndTurnDirty");
--	item_selectEndTurnUnitOrders:SetIsDoneEvents("UnitSelectionChanged");
--	item_selectEndTurnUnitOrders:SetUITriggers("ActionPanel", "TutorialSelectEndTurnH");
--	item_selectEndTurnUnitOrders:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));
--	item_selectEndTurnUnitOrders:SetNextTutorialItemId("USE_SCOUT");

	-- =============================== USE_SCOUT =====================================
--	local item_useScout:TutorialItem = TutorialItem:new("USE_SCOUT");
--	item_useScout:SetPrereqs("SELECT_END_TURN_UNIT_ORDERS");
--	item_useScout:SetAdvisorMessage("LOC_META_35_BODY");
--	item_useScout:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
--		function( advisorInfo )
--			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
--		end );
--	item_useScout:SetIsDoneFunction(
--		function()
--			return false;
--		end );

	-- =============================== EXPLAIN_RESOURCES_A =====================================
	local item:TutorialItem = TutorialItem:new("EXPLAIN_RESOURCES_A");
	item:SetPrereqs("BUILDERS_K");
	item:SetRaiseEvents("LocalPlayerTurnBegin");
	item:SetIsQueueable(true);
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_204");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_204");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_204")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,11);
		end );
	item:SetNextTutorialItemId("EXPLAIN_RESOURCES_B");

	-- =============================== EXPLAIN_RESOURCES_B =====================================
	-- TODO: Begin new chain when farm is built (top of following turn)
	local item:TutorialItem = TutorialItem:new("EXPLAIN_RESOURCES_B");
	item:SetPrereqs("EXPLAIN_RESOURCES_A");
	item:SetAdvisorMessage("LOC_META_30_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			--[[
			local localPlayer = Game.GetLocalPlayer()
			local player = Players[localPlayer]
			local playerUnits = player:GetUnits()

			for i, unit in playerUnits:Members() do
				local unitTypeName = UnitManager.GetTypeName(unit)

				if "UNIT_BUILDER" == unitTypeName then
					local plot = Map.GetPlot(unit:GetX(), unit:GetY())
					UI.LookAtPlot(plot)
					UI.SelectUnit(unit)
				end
			end
			]]--
			UI.LookAtPlot(15,12);
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("EXPLAIN_RESOURCES_C");

	-- =============================== EXPLAIN_RESOURCES_C =====================================
	local item:TutorialItem = TutorialItem:new("EXPLAIN_RESOURCES_C");
	item:SetPrereqs("EXPLAIN_RESOURCES_B");
	item:SetAdvisorMessage("LOC_META_31a_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(15,12);
			UI.SetMapZoom(0.3, 0.0, 0.0);
		end );
	item:SetNextTutorialItemId("EXPLAIN_RESOURCES_D");

	-- =============================== EXPLAIN_RESOURCES_D =====================================
	local item:TutorialItem = TutorialItem:new("EXPLAIN_RESOURCES_D");
	item:SetPrereqs("EXPLAIN_RESOURCES_C");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_205");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_205");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_205");
			local unit = GetFirstUnitOfType("UNIT_BUILDER");
			UI.SelectUnit(unit);
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetOpenFunction(
		function()
			UI.SetMapZoom(0.7, 0.0, 0.0);
		end );
	item:SetNextTutorialItemId("EXPLAIN_RESOURCES_E");

	-- =============================== EXPLAIN_RESOURCES_E =====================================
	local item:TutorialItem = TutorialItem:new("EXPLAIN_RESOURCES_E");
	item:SetPrereqs("EXPLAIN_RESOURCES_D");
	item:SetOpenFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( true );
			ForceMoveUnitDirection(DirectionTypes.DIRECTION_NORTHEAST)
		end );
	item:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			EndMovementRestriction();
		end );
	item:SetAdvisorCallout("LOC_META_31a_HEAD", "LOC_META_31b_BODY",
		function()
			local unit = GetFirstUnitOfType("UNIT_BUILDER");
			return Map.GetAdjacentPlot(unit:GetX(), unit:GetY(), DirectionTypes.DIRECTION_NORTHEAST)
		end);
	item:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput", "UnitPanel");
	item:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item:SetOverlayEnabled( false );
	item:SetIsDoneEvents("UnitMoveComplete");
	item:SetNextTutorialItemId("EXPLAIN_RESOURCES_F");

	-- =============================== EXPLAIN_RESOURCES_F =====================================
	local item:TutorialItem = TutorialItem:new("EXPLAIN_RESOURCES_F");
	item:SetPrereqs("EXPLAIN_RESOURCES_E");
	item:SetOpenFunction(
		function( )
			DisableUnitAction( "UNITOPERATION_MOVE_TO", "UNIT_BUILDER");
		end );
	item:SetAdvisorMessage("LOC_META_31a_HEAD");
	item:SetUITriggers("UnitPanel", "TutorialBuildQuarryAction");
	item:SetEnabledControls(UnitOperationTypes.BUILD_IMPROVEMENT);  -- FIXME: This does not appear to work.
	item:SetIsDoneEvents("ImprovementAddedToMap");
	item:SetCleanupFunction(
		function( )
			EnableUnitAction( "UNITOPERATION_MOVE_TO", "UNIT_BUILDER");
		end );
	item:SetNextTutorialItemId("EXPLAIN_RESOURCES_G");

	-- =============================== EXPLAIN_RESOURCES_G =====================================
	local item:TutorialItem = TutorialItem:new("EXPLAIN_RESOURCES_G");
	item:SetPrereqs("EXPLAIN_RESOURCES_F");
	item:SetIsEndOfChain(true);
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_206");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_206");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_206");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetCleanupFunction(
		function( )			
			EnableUnitAction( "UNITOPERATION_SLEEP", "UNIT_BUILDER");	
			local pUnit = GetFirstUnitOfType("UNIT_SCOUT");
			UI.SelectUnit(pUnit);		-- Reselect so enabled actions are shown enabled.
		end );
	item:SetOpenFunction(
		function()
			SetGlobalPreActivateFunction( nil );				-- Remove the auto-closing of the screens and partial screens
			AddUnitHexRestriction( "UNIT_BUILDER", 14, 12 );	-- Builder cannot go home.
			RemoveUnitHexRestriction( "UNIT_SCOUT", 14, 13 );	-- Scouts can again hang out north-east of the city (no longer blocking warriro)
		end );


if true then
	-- =============================== GOVERNMENT_POLICIES_A =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_A");
	item:SetRaiseEvents("CodeOfLawsCivicCompleted");
	item:SetIsQueueable(true);
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_44_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_44_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_44_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_B");

	-- =============================== GOVERNMENT_POLICIES_B =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_B");
	item:SetPrereqs("GOVERNMENT_POLICIES_A");
	item:SetAdvisorMessage("LOC_META_93a_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_C");

	-- =============================== GOVERNMENT_POLICIES_C =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_C");
	item:SetPrereqs("GOVERNMENT_POLICIES_B");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_441");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_441");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_441")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_D");

	-- =============================== GOVERNMENT_POLICIES_D =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_D");
	item:SetPrereqs("GOVERNMENT_POLICIES_C");
	item:SetUITriggers("LaunchBar", "TutorialOpenGovernment" );
	item:SetEnabledControls(UITutorialManager:GetHash("GovernmentButton"));
	item:SetIsDoneEvents("GovernmentScreenOpened");
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_E");

	-- =============================== GOVERNMENT_POLICIES_E =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_E");
	item:SetPrereqs("GOVERNMENT_POLICIES_D");
	item:SetAdvisorMessage("LOC_META_94_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_F");

	-- =============================== GOVERNMENT_POLICIES_F =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_F");
	item:SetPrereqs("GOVERNMENT_POLICIES_E");
	item:SetAdvisorMessage("LOC_META_95a_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_G");

	-- =============================== GOVERNMENT_POLICIES_G =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_G");
	item:SetPrereqs("GOVERNMENT_POLICIES_E");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_45_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_45_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_45_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_H");

	-- =============================== GOVERNMENT_POLICIES_H =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_H");
	item:SetPrereqs("GOVERNMENT_POLICIES_G");
	item:SetUITriggers( "ButtonPolicies", "TutorialChangePolicies" );
	item:SetIsDoneEvents("GovernmentPoliciesOpened");
	item:SetNextTutorialItemId("GOVERNMENT_POLICIES_I");

	-- =============================== GOVERNMENT_POLICIES_I =====================================
	local item:TutorialItem = TutorialItem:new("GOVERNMENT_POLICIES_I");
	item:SetPrereqs("GOVERNMENT_POLICIES_H");
	item:SetAdvisorMessage("LOC_META_96_BODY");
	item:SetIsEndOfChain(true);
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );

	--[[
	-- =============================== CIVICS_TREE_A =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_A");
	
	item:SetAdvisorMessage("LOC_META_97_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("CIVICS_TREE_B");
	--]]

	-- =============================== CIVICS_TREE_B =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_B");
	item:SetRaiseEvents("GovernmentPolicyChanged");
	item:SetIsQueueable(true);
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_453");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_453");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_453")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetNextTutorialItemId("CIVICS_TREE_C");

	-- =============================== CIVICS_TREE_C =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_C");
	item:SetPrereqs("CIVICS_TREE_B");
	item:SetAdvisorMessage("LOC_META_98_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("CIVICS_TREE_D");

	-- =============================== CIVICS_TREE_D =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_D");
	item:SetPrereqs("CIVICS_TREE_C");
	item:SetAdvisorMessage("LOC_META_99a_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("CIVICS_TREE_E");

	-- =============================== CIVICS_TREE_E =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_E");
	item:SetPrereqs("CIVICS_TREE_D");
	item:SetUITriggers("LaunchBar", "CivicsTree", "TutorialOpenCivicsTree" );
	item:SetEnabledControls(UITutorialManager:GetHash("CultureButton"));
	item:SetIsDoneEvents("CivicsTreeOpened");
	item:SetNextTutorialItemId("CIVICS_TREE_F");

	-- =============================== CIVICS_TREE_F =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_F");
	item:SetPrereqs("CIVICS_TREE_E");
	item:SetAdvisorMessage("LOC_META_100_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("CIVICS_TREE_G");
	item:SetOpenFunction( ReparentTutorialTreeNodes );

	-- =============================== CIVICS_TREE_G =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_G");
	item:SetPrereqs("CIVICS_TREE_F");
	item:SetUITriggers( "CivicsTree", "TutorialChangeCivic" );
	item:SetEnabledControls( GameInfo.Types["CIVIC_CRAFTSMANSHIP"].Hash );
	item:SetIsDoneEvents("CivicChanged");
	item:SetNextTutorialItemId("CIVICS_TREE_H");

	-- =============================== CIVICS_TREE_H =====================================
	local item:TutorialItem = TutorialItem:new("CIVICS_TREE_H");
	item:SetPrereqs("CIVICS_TREE_G");
	item:SetIsEndOfChain(true);
	item:SetUITriggers( "TutorialCloseCivicsPointer" );
	item:SetEnabledControls( UITutorialManager:GetHash("CivicsTreeModal") );
	item:SetIsDoneEvents("CivicsTreeClosed");

end

	-- =============================== BUILDERS_O =====================================
	--[[
	local item_buildersL:TutorialItem = TutorialItem:new("BUILDERS_O");
	item_buildersL:SetPrereqs("BUILDERS_N");
	item_buildersL:SetAdvisorMessage("LOC_META_32_BODY");
	item_buildersL:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_buildersL:SetIsDoneFunction(
		function()
			return false;
		end );
	item_buildersL:SetNextTutorialItemId("BUILDERS_P");

	-- =============================== BUILDERS_P =====================================
	local item_buildersM:TutorialItem = TutorialItem:new("BUILDERS_P");
	item_buildersM:SetPrereqs("BUILDERS_O");
	item_buildersM:SetIsEndOfChain(true)
	item_buildersM:SetAdvisorMessage("LOC_ADVISOR_LINE_FTUE_37");
	item_buildersM:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_37")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_buildersM:SetIsDoneFunction(
		function()
			return false;
		end );
	--item_buildersM:SetNextTutorialItemId("SELECT_END_TURN_RESEARCH");
	item_buildersM:SetShowPortrait(true)
	item_buildersM:SetOpenFunction(
		function()
			UI.PlaySound("Play_ADVISOR_LINE_FTUE_37")
		end );
	]]--

	-- ================================ FORTIFY_WARRIOR_A =====================================
	local item:TutorialItem = TutorialItem:new("FORTIFY_WARRIOR_A");
	item:SetRaiseEvents("WarriorMoveComplete");
	item:SetIsQueueable(true);
	item:SetCompletedGoals("GOAL_2");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_26_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_26_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_26_ALT");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("FORTIFY_WARRIOR_B");
	item:SetShowPortrait(true)
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
		end );

	-- =============================== FORTIFY_WARRIOR_B =====================================
	local item:TutorialItem = TutorialItem:new("FORTIFY_WARRIOR_B");
	item:SetPrereqs("FORTIFY_WARRIOR_A");
	item:SetAdvisorMessage("LOC_META_36a_BODY");
		item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item:SetOpenFunction(
		function( )
			EnableUnitAction( "UNITOPERATION_FORTIFY", "UNIT_WARRIOR");
			EnableUnitAction( "UNITOPERATION_HEAL",	"UNIT_WARRIOR");
			EnableUnitAction( "UNITOPERATION_FORTIFY", "UNIT_SCOUT");
			EnableUnitAction( "UNITOPERATION_HEAL",	"UNIT_SCOUT");
			EnableUnitAction( "UNITOPERATION_FORTIFY", "UNIT_BUILDER");	
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true );
			ForceMoveUnitToCapital();
			local localPlayer = Game.GetLocalPlayer();
			local player = Players[localPlayer];
			local playerUnits = player:GetUnits();
			for i, unit in playerUnits:Members() do
				local unitTypeName = UnitManager.GetTypeName(unit);
				if "UNIT_WARRIOR" == unitTypeName then
					local plot = Map.GetPlot(unit:GetX(), unit:GetY());
					UI.LookAtPlot(plot);
					UI.SelectUnit(unit);
				end
			end
		end );
	item:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
			DisableUnitAction( "UNITCOMMAND_CANCEL",	"UNIT_WARRIOR");
			DisableUnitAction( "UNITOPERATION_HEAL",	"UNIT_WARRIOR");
			EndMovementRestriction();
		end );
	item:SetUITriggers("UnitFlagManager", "WorldInput", "UnitPanel", "TutorialFortifyAction");
	item:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.FORTIFY);
	item:SetOverlayEnabled( false );
	item:SetIsDoneEvents("UnitOperationStarted");
	item:SetNextTutorialItemId("FORTIFY_WARRIOR_C");

	-- =============================== FORTIFY_WARRIOR_C =====================================
	local item:TutorialItem = TutorialItem:new("FORTIFY_WARRIOR_C");
	item:SetPrereqs("FORTIFY_WARRIOR_B");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_261");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_261");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_261")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetOpenFunction(
		function()
			local localPlayer = Game.GetLocalPlayer();
			local player = Players[localPlayer];
			local playerUnits = player:GetUnits();
			for i, unit in playerUnits:Members() do
				local unitTypeName = UnitManager.GetTypeName(unit);
				if "UNIT_WARRIOR" == unitTypeName then
					LockUnit(unit:GetID());
				end
			end
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetNextTutorialItemId("FORTIFY_WARRIOR_D");

	-- =============================== FORTIFY_WARRIOR_D =====================================
	local item:TutorialItem = TutorialItem:new("FORTIFY_WARRIOR_D");
	item:SetPrereqs("FORTIFY_WARRIOR_C");
	item:AddGoal("GOAL_3", "LOC_TUTORIAL_GOAL_3", "LOC_TUTORIAL_GOAL_TOOLTIP_3");
	item:SetAdvisorMessage("LOC_META_37_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			UI.SetMapZoom(0.7, 0,0, 0,0);
			UI.LookAtPlot(14,12);
		end );
	item:SetNextTutorialItemId("FORTIFY_WARRIOR_E");

	-- =============================== FORTIFY_WARRIOR_E =====================================
	local item:TutorialItem = TutorialItem:new("FORTIFY_WARRIOR_E");
	item:SetPrereqs("FORTIFY_WARRIOR_D");
	item:SetIsEndOfChain(true);
	item:SetAdvisorMessage("LOC_META_35_BODY");	-- "Continue exploring the world with your scout unit"
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			SelectAndCenterOnUnit( "UNIT_SCOUT" );
		end );

	-- =============================== BUILDER_WORKFORCE_9 =====================================
	local item_builderWorkforce9:TutorialItem = TutorialItem:new("BUILDER_WORKFORCE_9");
	item_builderWorkforce9:SetRaiseEvents("LocalPlayerTurnBegin");
	item_builderWorkforce9:SetPrereqs("EXPLAIN_RESOURCES_G");
	item_builderWorkforce9:SetIsQueueable(true);
	item_builderWorkforce9:SetAdvisorMessage("ADVISOR_LINE_FTUE_209");
	item_builderWorkforce9:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_209");
	item_builderWorkforce9:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_209")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_builderWorkforce9:SetIsDoneFunction(
		function()
			return false;
		end );
	item_builderWorkforce9:SetShowPortrait(true)
	item_builderWorkforce9:SetNextTutorialItemId("BUILDER_WORKFORCE");

	-- =============================== BUILDER_WORKFORCE =====================================
	local item_builderWorkforce:TutorialItem = TutorialItem:new("BUILDER_WORKFORCE");
	item_builderWorkforce:SetPrereqs("BUILDER_WORKFORCE_9");
	item_builderWorkforce:SetAdvisorMessage("LOC_META_38a_BODY");
	item_builderWorkforce:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_builderWorkforce:SetIsDoneFunction(
		function()
			return false;
		end );
	item_builderWorkforce:SetNextTutorialItemId("BUILDER_WORKFORCE_B");

	-- =============================== BUILDER_WORKFORCE_B =====================================
	local item_builderWorkforceB:TutorialItem = TutorialItem:new("BUILDER_WORKFORCE_B");
	item_builderWorkforceB:SetPrereqs("BUILDER_WORKFORCE");
	item_builderWorkforceB:AddGoal("GOAL_13", "LOC_TUTORIAL_GOAL_13", "LOC_TUTORIAL_GOAL_13");
	item_builderWorkforceB:SetAdvisorMessage("ADVISOR_LINE_FTUE_2091");
	item_builderWorkforceB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_2091");
	item_builderWorkforceB:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_2091")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_builderWorkforceB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_builderWorkforceB:SetShowPortrait(true)
	item_builderWorkforceB:SetNextTutorialItemId("BUILDER_WORKFORCE_C");

	-- =============================== BUILDER_WORKFORCE_C =====================================
	local item_builderWorkforceC:TutorialItem = TutorialItem:new("BUILDER_WORKFORCE_C");
	item_builderWorkforceC:SetPrereqs("BUILDER_WORKFORCE_B");
	item_builderWorkforceC:SetAdvisorMessage("LOC_META_38b_BODY");
	item_builderWorkforceC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_builderWorkforceC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_builderWorkforceC:SetNextTutorialItemId("EXPLORATION");

	-- =============================== EXPLORATION =====================================
	local item_exploreA:TutorialItem = TutorialItem:new("EXPLORATION");
	item_exploreA:SetPrereqs("BUILDER_WORKFORCE");
	item_exploreA:SetIsEndOfChain(true)
	item_exploreA:SetAdvisorMessage("LOC_META_39_BODY");
	item_exploreA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_exploreA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_exploreA:SetOpenFunction(
		function()
			SelectAndCenterOnUnit( "UNIT_SCOUT" );
		end );

	-- =============================== MONUMENT_COMPLETE =====================================
	local item_monumentComplete:TutorialItem = TutorialItem:new("MONUMENT_COMPLETE");
	--item_monumentComplete:SetPrereqs("EXPLORATION");
	item_monumentComplete:SetIsQueueable(true);
	item_monumentComplete:SetRaiseEvents("CapitalMonumentProductionCompleted");
	item_monumentComplete:SetAdvisorMessage("ADVISOR_LINE_FTUE_27_ALT");
	item_monumentComplete:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_27_ALT");
	item_monumentComplete:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_27_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_monumentComplete:SetIsDoneFunction(
		function()
			return false;
		end );
	item_monumentComplete:SetNextTutorialItemId("MONUMENT_COMPLETE_B");
	item_monumentComplete:SetShowPortrait(true)
	item_monumentComplete:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);
			UI.SetMapZoom(0.0, 0.0, 0.0);
		end );

	-- =============================== MONUMENT_COMPLETE_B =====================================
	local item_monumentCompleteB:TutorialItem = TutorialItem:new("MONUMENT_COMPLETE_B");
	item_monumentCompleteB:SetPrereqs("MONUMENT_COMPLETE");
	item_monumentCompleteB:SetAdvisorMessage("LOC_META_40_BODY");
	item_monumentCompleteB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_monumentCompleteB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_monumentCompleteB:SetNextTutorialItemId("MONUMENT_COMPLETE_C");

	-- =============================== MONUMENT_COMPLETE_C =====================================
	local item_monumentCompleteC:TutorialItem = TutorialItem:new("MONUMENT_COMPLETE_C");
	item_monumentCompleteC:SetPrereqs("MONUMENT_COMPLETE_B");
	item_monumentCompleteC:SetAdvisorMessage("ADVISOR_LINE_FTUE_28_ALT");
	item_monumentCompleteC:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_28_ALT");
	item_monumentCompleteC:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_28_ALT");
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_monumentCompleteC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_monumentCompleteC:SetShowPortrait(true);
	item_monumentCompleteC:SetOpenFunction(
		function()
			UI.SetMapZoom(0.7, 0.0, 0.0);
		end );
	item_monumentCompleteC:SetNextTutorialItemId("TRAIN_SETTLER_A");

	-- =============================== TRAIN_SETTLER_A =====================================
	local item:TutorialItem = TutorialItem:new("TRAIN_SETTLER_A");
	item:SetPrereqs("MONUMENT_COMPLETE_C");
	item:SetAdvisorMessage("LOC_META_41b_BODY"); -- "Open the production panel..."
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			--LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item:SetOpenFunction(
		function( )
			local player = GetPlayer();
			if player == nil then
				UI.DataError("Unable to obtain player in Open City Panel tutorial item.");
			end
			local capitalCity = player:GetCities():GetCapitalCity();
			if capitalCity == nil then
				UI.DataError("Unable to obtain capital city in Open City Panel tutorial item.");
			end
			UI.SelectCity( capitalCity );	-- Immediate call instead of waiting for callback
			LuaEvents.Tutorial_CityPanelOpen();
		end );
	item:SetUITriggers("CityPanel", "TutorialOpenProduction");
	item:SetEnabledControls(UITutorialManager:GetHash("ChangeProductionCheck"));
	item:SetIsDoneEvents("ProductionPanelViaCityOpen");
	item:SetNextTutorialItemId("TRAIN_SETTLER_B");

	-- =============================== TRAIN_SETTLER_B =====================================
	local item:TutorialItem = TutorialItem:new("TRAIN_SETTLER_B");
	item:SetPrereqs("TRAIN_SETTLER_A");
	item:SetRaiseEvents("ProductionPanelOpen");
	item:SetUITriggers("ChooseProductionMenu", "TutorialTrainSettlers");
	item:SetEnabledControls( UITutorialManager:GetHash("UNIT_SETTLER") );
	item:SetIsDoneEvents("CityProductionChanged_Settler");
	item:SetNextTutorialItemId("TRAIN_SETTLER_C");

	-- =============================== TRAIN_SETTLER_C =====================================
	local item:TutorialItem = TutorialItem:new("TRAIN_SETTLER_C");
	item:SetPrereqs("TRAIN_SETTLER_B");
	item:SetIsEndOfChain(true);
	item:AddGoal("GOAL_4", "LOC_TUTORIAL_GOAL_4", "LOC_TUTORIAL_GOAL_TOOLTIP_4");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_29_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_29_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LockProduction();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_29_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)

	-- ================================ SETTLER_COMPLETE =====================================
	local item_settlerComplete:TutorialItem = TutorialItem:new("SETTLER_COMPLETE");
	item_settlerComplete:SetCompletedGoals("GOAL_4");
	item_settlerComplete:SetRaiseEvents("CapitalSettlerProductionCompleted");
	item_settlerComplete:SetIsQueueable(true)
	item_settlerComplete:SetAdvisorMessage("ADVISOR_LINE_FTUE_30_ALT");
	item_settlerComplete:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_30_ALT");
	item_settlerComplete:AddAdvisorButton("LOC_ADVISOR_BUTTON_GET_STARTED",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_30_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_settlerComplete:SetIsDoneFunction(
		function()
			return false;
		end );
	item_settlerComplete:SetNextTutorialItemId("SELECT_SETTLER_B");
	item_settlerComplete:SetShowPortrait(true)

	-- =============================== SELECT_SETTLER_B =====================================
	local item_settlerCompleteB:TutorialItem = TutorialItem:new("SELECT_SETTLER_B");
	item_settlerCompleteB:SetPrereqs("SETTLER_COMPLETE");
	item_settlerCompleteB:SetAdvisorMessage("LOC_META_42_BODY");
	item_settlerCompleteB:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			local localPlayer = Game.GetLocalPlayer()
			local player = Players[localPlayer]
			local playerUnits = player:GetUnits()

			for i, unit in playerUnits:Members() do
				local unitTypeName = UnitManager.GetTypeName(unit)

				if "UNIT_SETTLER" == unitTypeName then
					local plot = Map.GetPlot(unit:GetX(), unit:GetY());
					UI.LookAtPlot(plot);
					UI.SelectUnit(unit);
				end
			end
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_settlerCompleteB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_settlerCompleteB:SetNextTutorialItemId("SETTLER_FORMATION");

	-- =============================== SETTLER_FORMATION =====================================
	local item_settlerFormation:TutorialItem = TutorialItem:new("SETTLER_FORMATION");
	item_settlerFormation:SetPrereqs("SELECT_SETTLER_B");
	item_settlerFormation:SetCompletedGoals("GOAL_3");
	item_settlerFormation:SetAdvisorMessage("LOC_META_43a_BODY");
	item_settlerFormation:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_settlerFormation:SetOpenFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( true );
			DisableUnitAction( "UNITOPERATION_MOVE_TO", "UNIT_SETTLER");		
			DisableUnitAction( "UNITOPERATION_SLEEP", "UNIT_SETTLER");		
			DisableUnitAction( "UNITCOMMAND_EXIT_FORMATION", "UNIT_SETTLER");
			DisableUnitAction( "UNITCOMMAND_EXIT_FORMATION", "UNIT_WARRIOR");
			DisableUnitAction( "UNITCOMMAND_CANCEL",	"UNIT_SETTLER");
			AddMapUnitMoveRestriction( "UNIT_SETTLER" );
			LuaEvents.Tutorial_DisableMapSelect( true );
		end );
	item_settlerFormation:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
		end );
	item_settlerFormation:SetUITriggers("UnitFlagManager", "WorldInput", "UnitPanel", "TutorialFormationAction");
	item_settlerFormation:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitCommandTypes.ENTER_FORMATION);
	item_settlerFormation:SetOverlayEnabled( false );
	item_settlerFormation:SetIsDoneEvents("UnitEnterFormation");
	item_settlerFormation:SetNextTutorialItemId("SETTLER_FORMATION_B");

	-- =============================== SETTLER_FORMATION_B =====================================
	local item_settlerFormationB:TutorialItem = TutorialItem:new("SETTLER_FORMATION_B");
	item_settlerFormationB:SetPrereqs("SETTLER_FORMATION");
	item_settlerFormationB:SetAdvisorMessage("ADVISOR_LINE_FTUE_301");
	item_settlerFormationB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_301");
	item_settlerFormationB:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_301")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_settlerFormationB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_settlerFormationB:SetShowPortrait(true)
	item_settlerFormationB:SetOpenFunction(
		function()
			RemoveMapUnitMoveRestriction( "UNIT_SETTLER" );
			EnableUnitAction( "UNITOPERATION_MOVE_TO", "UNIT_SETTLER");		
		end );
	item_settlerFormationB:SetNextTutorialItemId("SETTLER_FORMATION_C");

	-- =============================== SETTLER_FORMATION_C =====================================
	local item_settlerFormationC:TutorialItem = TutorialItem:new("SETTLER_FORMATION_C");
	item_settlerFormationC:SetPrereqs("SETTLER_FORMATION_B");
	item_settlerFormationC:SetAdvisorMessage("ADVISOR_LINE_FTUE_302");
	item_settlerFormationC:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_302");
	item_settlerFormationC:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_302")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_settlerFormationC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_settlerFormationC:SetShowPortrait(true)
	item_settlerFormationC:SetNextTutorialItemId("MOVE_SETTLER");

	-- =============================== MOVE_SETTLER =====================================
	local item_moveSettler:TutorialItem = TutorialItem:new("MOVE_SETTLER");
	item_moveSettler:SetPrereqs("SETTLER_FORMATION_B");
	item_moveSettler:AddGoal("GOAL_5", "LOC_TUTORIAL_GOAL_5", "LOC_TUTORIAL_GOAL_TOOLTIP_5");
	item_moveSettler:SetOpenFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( true );
			ForceMoveUnitEastward()
		end );
	item_moveSettler:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			EndMovementRestriction();
		end );
	item_moveSettler:SetAdvisorCallout("LOC_META_44_HEAD", "LOC_META_44_BODY",
		function()
			local unit = GetFirstUnitOfType("UNIT_SETTLER")
			return Map.GetPlot(unit:GetX() + 4, unit:GetY() - 1):GetIndex();
		end);
	item_moveSettler:SetUITriggers("TutorialSelectUnit", "UnitFlagManager", "WorldInput", "UnitPanel");
	item_moveSettler:SetEnabledControls(UITutorialManager:GetHash("UnitFlagManager"), UnitOperationTypes.MOVE_TO);
	item_moveSettler:SetOverlayEnabled( false );
	item_moveSettler:SetIsDoneEvents("UnitMoveComplete");
	item_moveSettler:SetNextTutorialItemId("MOVE_SETTLER_B");

	-- =============================== MOVE_SETTLER_B =====================================
	local item_moveSettlerB:TutorialItem = TutorialItem:new("MOVE_SETTLER_B");
	item_moveSettlerB:SetPrereqs("MOVE_SETTLER");
	item_moveSettlerB:SetIsEndOfChain(true)
	item_moveSettlerB:SetAdvisorMessage("ADVISOR_LINE_FTUE_31_ALT");
	item_moveSettlerB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_31_ALT");
	item_moveSettlerB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_31_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_moveSettlerB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_moveSettlerB:SetShowPortrait(true)
	item_moveSettlerB:SetOpenFunction(
		function()
			AddMapUnitMoveRestriction( "UNIT_SETTLER" );	-- Keep disabled until reaching 2nd city location
		end );

	-- =============================== TRAIN_SLINGER =====================================
	local item_trainSlinger:TutorialItem = TutorialItem:new("TRAIN_SLINGER");
	item_trainSlinger:SetPrereqs("MOVE_SETTLER_B");
	item_trainSlinger:SetAdvisorMessage("LOC_META_45a_BODY");
	item_trainSlinger:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_trainSlinger:SetRaiseEvents("ProductionPanelOpen");
	item_trainSlinger:SetUITriggers("ChooseProductionMenu", "TutorialTrainSlinger");
	item_trainSlinger:SetEnabledControls( UITutorialManager:GetHash("UNIT_SLINGER") );
	item_trainSlinger:SetIsDoneEvents("CityProductionChanged_Slinger");
	item_trainSlinger:SetNextTutorialItemId("TRAIN_SLINGER_B");

	-- =============================== TRAIN_SLINGER_B =====================================
	local item_trainSlingerB:TutorialItem = TutorialItem:new("TRAIN_SLINGER_B");
	item_trainSlingerB:SetPrereqs("TRAIN_SLINGER");
	item_trainSlingerB:SetIsEndOfChain(true);
	item_trainSlingerB:SetIsEndOfChain(true);
	item_trainSlingerB:SetAdvisorMessage("ADVISOR_LINE_FTUE_311");
	item_trainSlingerB:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_311");
	item_trainSlingerB:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_311")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_trainSlingerB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_trainSlingerB:SetShowPortrait(true)

	-- =============================== POTTERY_COMPLETE =====================================
	local item_potteryComplete:TutorialItem = TutorialItem:new("POTTERY_COMPLETE");
	item_potteryComplete:SetRaiseEvents("PotteryResearchCompleted");
	item_potteryComplete:SetIsQueueable(true);
	item_potteryComplete:SetAdvisorMessage("LOC_META_POTTERY_COMPLETE");
	item_potteryComplete:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_potteryComplete:SetIsDoneFunction(
		function()
			return false;
		end );
	item_potteryComplete:SetNextTutorialItemId("RESEARCH_IRRIGATION");

	-- =============================== RESEARCH_IRRIGATION =====================================
	local item_researchIrrigation:TutorialItem = TutorialItem:new("RESEARCH_IRRIGATION");
	item_researchIrrigation:SetPrereqs("POTTERY_COMPLETE");
	item_researchIrrigation:SetRaiseEvents("EndTurnDirty");
	--item_researchIrrigation:SetIsDoneEvents("ProductionPanelOpen");
	item_researchIrrigation:SetUITriggers("ActionPanel", "TutorialSelectEndTurnIrrigation");
	item_researchIrrigation:SetEnabledControls(UITutorialManager:GetHash("ActionPanel"));

	-- =============================== RESEARCH_IRRIGATION_B =====================================
	-- Once the ResearchChooser is visible, disable everything on the ResearchChooser.
	-- During each tutorial step, Enable happens first, Disable happens second
	-- so we need one step for disable, one step for enable.
	local item_researchIrrigationB:TutorialItem = TutorialItem:new("RESEARCH_IRRIGATION_B");
	item_researchIrrigationB:SetPrereqs("RESEARCH_IRRIGATION");
	item_researchIrrigationB:SetRaiseEvents("ResearchChooser_ForceHideWorldTracker");
	item_researchIrrigationB:SetUITriggers("ResearchChooser", "TutorialSelectResearchIrrigation");
	--item_researchIrrigationB:SetDisabledControls(UITutorialManager:GetHash("ResearchStack"));
	item_researchIrrigationB:SetNextTutorialItemId("RESEARCH_IRRIGATION_C");
	
	-- =============================== RESEARCH_IRRIGATION_C =====================================
	local item_researchIrrigationC:TutorialItem = TutorialItem:new("RESEARCH_IRRIGATION_C");
	item_researchIrrigationC:SetPrereqs("RESEARCH_IRRIGATION_B");
	item_researchIrrigationC:SetIsEndOfChain(true);
	item_researchIrrigationC:SetIsDoneEvents("ResearchChanged");
	item_researchIrrigationC:SetIsDoneFunction(
		function()
			LockResearch();
			return true;
		end );
	item_researchIrrigationC:SetUITriggers("ResearchChooser", "TutorialSelectResearchIrrigation");
	item_researchIrrigationC:SetEnabledControls(UITutorialManager:GetHash("TECH_IRRIGATION"));


	-- ================================ EXPLAIN_TECH_TREE =====================================
	local item:TutorialItem = TutorialItem:new("EXPLAIN_TECH_TREE");
	item:SetIsQueueable(true);
	item:SetRaiseEvents("IrrigationResearchCompleted");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetAdvisorMessage("LOC_META_46_BODY");
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("TECH_TREE_A");

	-- ================================ TECH_TREE_A =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_A");
	item:SetPrereqs("EXPLAIN_TECH_TREE");
	item:SetUITriggers("LaunchBar", "TutorialOpenTechTree");
	item:SetEnabledControls(UITutorialManager:GetHash("ScienceButton"));
	item:SetIsDoneEvents("TechTreeOpened");
	item:SetNextTutorialItemId("TECH_TREE_B");

	-- =============================== TECH_TREE_B =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_B");
	item:SetPrereqs("TECH_TREE_A");
	item:SetOpenFunction( ReparentTutorialTreeNodes );
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_312");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_312");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_312")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)
	item:SetNextTutorialItemId("TECH_TREE_C");

	-- ================================ TECH_TREE_C =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_C");
	item:SetPrereqs("TECH_TREE_B");
	item:SetAdvisorMessage("LOC_META_47_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			LuaEvents.Tutorial_TechTreeScrollToNode("TECH_IRRIGATION");
		end );
	item:SetNextTutorialItemId("TECH_TREE_D");

	-- ================================ TECH_TREE_D =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_D");
	item:SetPrereqs("TECH_TREE_C");
	item:SetAdvisorMessage("LOC_META_48_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("TechTree", "TutorialCompletedTechNodePointer");
	item:SetNextTutorialItemId("TECH_TREE_E");

	-- ================================ TECH_TREE_E =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_E");
	item:SetPrereqs("TECH_TREE_D");
	item:SetAdvisorMessage("LOC_META_49_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("TechTree", "TutorialIncompleteTechNodePointer");
	item:SetNextTutorialItemId("TECH_TREE_F");

	-- ================================ TECH_TREE_F =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_F");
	item:SetPrereqs("TECH_TREE_E");
	item:SetAdvisorMessage("LOC_META_50_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			LuaEvents.Tutorial_TechTreeScrollToNode("TECH_WRITING");
		end );
	item:SetAdvisorUITriggers("TechTree", "TutorialUnavailableTechNodePointer");
	item:SetNextTutorialItemId("TECH_TREE_G");

	-- ================================ TECH_TREE_G =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_G");
	item:SetPrereqs("TECH_TREE_F");
	item:SetAdvisorMessage("LOC_META_51a_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item:SetNextTutorialItemId("TECH_TREE_G2");

	-- ================================ TECH_TREE_G2 =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_G2");
	item:SetPrereqs("TECH_TREE_G");
	item:SetUITriggers("TechTree","TutorialChooseWritingPointer");	
	item:SetEnabledControls( GameInfo.Types["TECH_WRITING"].Hash );
	item:SetIsDoneEvents("ResearchChanged");
	item:SetNextTutorialItemId("TECH_TREE_H");

	-- ================================ TECH_TREE_H =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_H");
	item:SetPrereqs("TECH_TREE_G2");
	item:SetAdvisorMessage("LOC_META_52_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LockResearch();
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("TechTree", "TutorialActiveTechNodePointer");
	item:SetNextTutorialItemId("TECH_TREE_I");

	-- ================================ TECH_TREE_I =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_I");
	item:SetPrereqs("TECH_TREE_H");
	item:SetAdvisorMessage("LOC_META_53A_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("TechTree", "TutorialTechUnlocksPointer");
	item:SetNextTutorialItemId("TECH_TREE_J");

	-- ================================ TECH_TREE_J =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_J");
	item:SetPrereqs("TECH_TREE_I");
	item:SetAdvisorMessage("LOC_META_53B_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("TechTree", "TutorialTechUnlocksPointer");
	item:SetNextTutorialItemId("TECH_TREE_K");

	-- ================================ TECH_TREE_K =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_K");
	item:SetPrereqs("TECH_TREE_J");
	item:SetUITriggers("TechTree", "TutorialCloseTechTreePointer");
	item:SetEnabledControls( UITutorialManager:GetHash("TechTreeModal") );
	item:SetIsDoneEvents("TechTreeClosed");
	item:SetNextTutorialItemId("TECH_TREE_L");

	-- ================================ TECH_TREE_L =====================================
	local item:TutorialItem = TutorialItem:new("TECH_TREE_L");
	item:SetPrereqs("TECH_TREE_K");
	item:SetIsEndOfChain(true);
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_38_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_38_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_38_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)

	-- =============================== SLINGER_COMPLETED_A =====================================
	local item_slingerCompletedA:TutorialItem = TutorialItem:new("SLINGER_COMPLETED_A");
	item_slingerCompletedA:SetRaiseEvents("CapitalSlingerProductionCompleted");
	item_slingerCompletedA:SetIsQueueable(true);
	item_slingerCompletedA:SetAdvisorMessage("ADVISOR_LINE_FTUE_381");
	item_slingerCompletedA:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_381");
	item_slingerCompletedA:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_381")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_slingerCompletedA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_slingerCompletedA:SetShowPortrait(true)
	item_slingerCompletedA:SetOpenFunction(
		function()
			UI.LookAtPlot(14,12);			
		end );
	item_slingerCompletedA:SetNextTutorialItemId("SLINGER_COMPLETED_B");

	-- ================================ SLINGER_COMPLETED_B =====================================
	local item_slingerCompletedB:TutorialItem = TutorialItem:new("SLINGER_COMPLETED_B");
	item_slingerCompletedB:SetPrereqs("SLINGER_COMPLETED_A");
	item_slingerCompletedB:SetAdvisorMessage("LOC_META_103_OTHER_BODY");
	item_slingerCompletedB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_slingerCompletedB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_slingerCompletedB:SetNextTutorialItemId("SLINGER_COMPLETED_C");

	-- ================================ SLINGER_COMPLETED_C =====================================
	local item_slingerCompletedC:TutorialItem = TutorialItem:new("SLINGER_COMPLETED_C");
	item_slingerCompletedC:SetPrereqs("SLINGER_COMPLETED_B");
	item_slingerCompletedC:SetAdvisorMessage("LOC_META_104_OTHER_BODY");
	item_slingerCompletedC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_slingerCompletedC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_slingerCompletedC:SetNextTutorialItemId("SLINGER_COMPLETED_D");

	-- =============================== SLINGER_COMPLETED_D =====================================
	local item_slingerCompletedD:TutorialItem = TutorialItem:new("SLINGER_COMPLETED_D");
	item_slingerCompletedD:SetPrereqs("SLINGER_COMPLETED_C");
	item_slingerCompletedD:SetAdvisorMessage("ADVISOR_LINE_FTUE_382");
	item_slingerCompletedD:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_382");
	item_slingerCompletedD:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_382")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_slingerCompletedD:SetIsDoneFunction(
		function()
			return false;
		end );
	item_slingerCompletedD:SetShowPortrait(true)
	item_slingerCompletedD:SetNextTutorialItemId("SLINGER_COMPLETED_E");

	-- ================================ SLINGER_COMPLETED_E =====================================
	local item_slingerCompletedE:TutorialItem = TutorialItem:new("SLINGER_COMPLETED_E");
	item_slingerCompletedE:SetPrereqs("SLINGER_COMPLETED_D");
	item_slingerCompletedE:SetAdvisorMessage("LOC_META_105_OTHER_BODY");
	item_slingerCompletedE:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_slingerCompletedE:SetIsDoneFunction(
		function()
			return false;
		end );
	item_slingerCompletedE:SetNextTutorialItemId("SLINGER_COMPLETED_F");

	-- =============================== SLINGER_COMPLETED_F =====================================
	local item_slingerCompletedF:TutorialItem = TutorialItem:new("SLINGER_COMPLETED_F");
	item_slingerCompletedF:SetPrereqs("SLINGER_COMPLETED_E");
	item_slingerCompletedF:SetAdvisorMessage("ADVISOR_LINE_FTUE_383");
	item_slingerCompletedF:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_383");
	item_slingerCompletedF:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_383")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_slingerCompletedF:SetIsDoneFunction(
		function()
			return false;
		end );
	item_slingerCompletedF:SetShowPortrait(true)
	item_slingerCompletedF:SetNextTutorialItemId("SLINGER_COMPLETED_G");

	-- ================================ SLINGER_COMPLETED_G =====================================
	local item_slingerCompletedG:TutorialItem = TutorialItem:new("SLINGER_COMPLETED_G");
	item_slingerCompletedG:SetPrereqs("SLINGER_COMPLETED_F");
	item_slingerCompletedG:SetIsEndOfChain(true);
	item_slingerCompletedG:SetAdvisorMessage("LOC_META_110_BODY");
	item_slingerCompletedG:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_slingerCompletedG:SetIsDoneFunction(
		function()
			return false;
		end );

	-- ================================ FOUND_SECOND_CITY =====================================
	local item_foundSecondCity:TutorialItem = TutorialItem:new("FOUND_SECOND_CITY");
	item_foundSecondCity:SetIsQueueable(true);
	item_foundSecondCity:SetCompletedGoals("GOAL_5");
	item_foundSecondCity:SetRaiseEvents("SettlerMoveComplete");
	item_foundSecondCity:SetAdvisorMessage("LOC_META_56_BODY");
	item_foundSecondCity:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_foundSecondCity:SetIsDoneFunction(
		function()
			return false;
		end );
	item_foundSecondCity:SetOpenFunction(
		function()
			UI.LookAtPlot(18,11);
		end );
	item_foundSecondCity:SetNextTutorialItemId("FOUND_SECOND_CITY2");

	-- ================================ FOUND_SECOND_CITY2 =====================================
	local item_foundSecondCity2:TutorialItem = TutorialItem:new("FOUND_SECOND_CITY2");
	item_foundSecondCity2:SetPrereqs("FOUND_SECOND_CITY");
	item_foundSecondCity2:SetAdvisorMessage("ADVISOR_LINE_FTUE_331");
	item_foundSecondCity2:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_331");
	item_foundSecondCity2:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_331")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_foundSecondCity2:SetIsDoneFunction(
		function()
			return false;
		end );
	item_foundSecondCity2:SetShowPortrait(true)
	item_foundSecondCity2:SetOpenFunction(
		function()
			SelectAndCenterOnUnit( "UNIT_SETTLER");
		end );
	item_foundSecondCity2:SetNextTutorialItemId("FOUND_SECOND_CITY_B");

	-- ================================ FOUND_SECOND_CITY_B =====================================
	local item_foundSecondCityB:TutorialItem = TutorialItem:new("FOUND_SECOND_CITY_B");
	item_foundSecondCityB:SetPrereqs("FOUND_SECOND_CITY2");
	item_foundSecondCityB:SetIsEndOfChain(true);
	item_foundSecondCityB:SetAdvisorMessage("LOC_META_57_BODY");
	item_foundSecondCityB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_foundSecondCityB:SetIsDoneFunction(
		function()
			return false;
		end );

	-- ================================ FOUND_SECOND_CITY_C =====================================
	local item_foundSecondCityC:TutorialItem = TutorialItem:new("FOUND_SECOND_CITY_C");
	item_foundSecondCityC:SetPrereqs("FOUND_SECOND_CITY_B");
	item_foundSecondCityC:SetRaiseEvents("CityAddedToMap");
	item_foundSecondCityC:SetIsQueueable(true);
	item_foundSecondCityC:SetAdvisorMessage("ADVISOR_LINE_FTUE_332");
	item_foundSecondCityC:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_332");
	item_foundSecondCityC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_332")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_foundSecondCityC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_foundSecondCityC:SetShowPortrait(true);
	item_foundSecondCityC:SetNextTutorialItemId("FOUND_SECOND_CITY_D");

	-- ================================ FOUND_SECOND_CITY_D =====================================
	local item_foundSecondCityD:TutorialItem = TutorialItem:new("FOUND_SECOND_CITY_D");
	item_foundSecondCityD:SetPrereqs("FOUND_SECOND_CITY_C");
	item_foundSecondCityD:SetIsEndOfChain(true);
	item_foundSecondCityD:AddGoal("GOAL_6", "LOC_TUTORIAL_GOAL_6", "LOC_TUTORIAL_GOAL_TOOLTIP_6");
	item_foundSecondCityD:SetAdvisorMessage("ADVISOR_LINE_FTUE_34_ALT");
	item_foundSecondCityD:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_34_ALT");
	item_foundSecondCityD:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_34_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_foundSecondCityD:SetIsDoneFunction(
		function()
			return false;
		end );
	item_foundSecondCityD:SetShowPortrait(true)
	item_foundSecondCityD:SetOpenFunction(
		function()
			RemoveMapUnitMoveRestriction( "UNIT_SETTLER" );
			RemoveMapUnitMoveRestriction( "UNIT_WARRIOR" );
			EnableUnitAction( "UNITOPERATION_MOVE_TO", "UNIT_SETTLER");		
			EnableUnitAction( "UNITOPERATION_SLEEP", "UNIT_SETTLER");		
			EnableUnitAction( "UNITCOMMAND_EXIT_FORMATION", "UNIT_SETTLER");
			EnableUnitAction( "UNITCOMMAND_EXIT_FORMATION", "UNIT_WARRIOR");
			EnableUnitAction( "UNITCOMMAND_CANCEL",	"UNIT_SETTLER");
			EnableUnitAction( "UNITOPERATION_REMOVE_IMPROVEMENT", "UNIT_BUILDER" );
			UnlockUnit();
		end );
	-- ================================ DISTRICTS_9 =====================================
	local item_districts9:TutorialItem = TutorialItem:new("DISTRICTS_9");
	--item_districts9:SetPrereqs("TECH_TREE_I");
	item_districts9:SetRaiseEvents("WritingResearchCompleted");
	item_districts9:SetIsQueueable(true)
	item_districts9:SetAdvisorMessage("LOC_META_WRITING_COMPLETE");
	item_districts9:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districts9:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districts9:SetNextTutorialItemId("DISTRICTS_A");

	-- =============================== DISTRICTS_A =====================================
--	local item_districtsA:TutorialItem = TutorialItem:new("DISTRICTS_A");
--	item_districtsA:SetPrereqs("FOUND_SECOND_CITY_D");
--	item_districtsA:SetRaiseEvents("ResearchCompleted");
--	item_districtsA:SetAdvisorMessage("LOC_ADVISOR_LINE_FTUE_37");
--	item_districtsA:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
--		function( advisorInfo )
--			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_37")
			--LuaEvents.Tutorial_ResearchOpen();
			--LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
--			LuaEvents.AdvisorPopup_ClearActive( advisorInfo )
--		end );
	--item_districtsA:SetUITriggers("ResearchChooser", "TutorialSelectResearch");
	--item_districtsA:SetEnabledControls(UITutorialManager:GetHash("TECH_MINING"));
	--item_districtsA:SetIsDoneEvents("ResearchChanged");
--	item_districtsA:SetNextTutorialItemId("DISTRICTS_B");
--	item_districtsA:SetShowPortrait(true)
--	item_districtsA:SetOpenFunction(
--		function()
--			UI.PlaySound("Play_ADVISOR_LINE_FTUE_37")
--		end );

	-- =============================== DISTRICTS_A =====================================
	local item_districtsA:TutorialItem = TutorialItem:new("DISTRICTS_A");
	item_districtsA:SetPrereqs("DISTRICTS_9");
	--item_districtsA:SetRaiseEvents("ResearchCompleted");
	item_districtsA:SetAdvisorMessage("ADVISOR_LINE_FTUE_39_ALT");
	item_districtsA:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_39_ALT");
	item_districtsA:AddAdvisorButton("LOC_ADVISOR_BUTTON_SHOW_ME",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_39_ALT")
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_districtsA:SetShowPortrait(true)
	item_districtsA:SetOpenFunction(
		function( )
			local player = GetPlayer();
			local capitalCity = player:GetCities():GetCapitalCity();
			UI.SelectCity( capitalCity );	-- Immediate call instead of waiting for callback
			LuaEvents.Tutorial_CityPanelOpen();
		end );
	item_districtsA:SetUITriggers("CityPanel", "TutorialOpenProduction" );
	item_districtsA:SetEnabledControls(UITutorialManager:GetHash("ChangeProductionCheck"));
	item_districtsA:SetIsDoneEvents("ProductionPanelViaCityOpen");
	item_districtsA:SetNextTutorialItemId("DISTRICTS_B");

	-- ================================ DISTRICTS_B =====================================
	local item_districtsB:TutorialItem = TutorialItem:new("DISTRICTS_B");
	item_districtsB:SetPrereqs("DISTRICTS_A");
	item_districtsB:SetAdvisorMessage("LOC_META_77_BODY");
	item_districtsB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsB:SetNextTutorialItemId("DISTRICTS_C");

	-- ================================ DISTRICTS_C =====================================
	local item_districtsC:TutorialItem = TutorialItem:new("DISTRICTS_C");
	item_districtsC:SetPrereqs("DISTRICTS_B");
	item_districtsC:SetAdvisorMessage("LOC_META_78_BODY");
	item_districtsC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsC:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsC:SetNextTutorialItemId("DISTRICTS_D");

	-- ================================ DISTRICTS_D =====================================
	local item_districtsD:TutorialItem = TutorialItem:new("DISTRICTS_D");
	item_districtsD:SetPrereqs("DISTRICTS_C");
	item_districtsD:SetAdvisorMessage("ADVISOR_LINE_8_ALT2");
	item_districtsD:SetAdvisorAudio("Play_ADVISOR_LINE_8_ALT2");
	item_districtsD:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_8_ALT2")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsD:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsD:SetShowPortrait(true)
	item_districtsD:SetNextTutorialItemId("DISTRICTS_E");

	-- ================================ DISTRICTS_E =====================================
	local item_districtsE:TutorialItem = TutorialItem:new("DISTRICTS_E");
	item_districtsE:SetPrereqs("DISTRICTS_D");
	item_districtsE:SetAdvisorMessage("LOC_META_79_BODY");
	item_districtsE:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsE:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsE:SetNextTutorialItemId("DISTRICTS_F");

	-- =============================== DISTRICTS_F =====================================
	local item_districtsF:TutorialItem = TutorialItem:new("DISTRICTS_F");
	item_districtsF:SetPrereqs("DISTRICTS_E");
	item_districtsF:SetAdvisorMessage("LOC_META_80_BODY");
	item_districtsF:SetUITriggers("ChooseProductionMenu", "TutorialBuildCampus");
	item_districtsF:SetEnabledControls( UITutorialManager:GetHash("DISTRICT_CAMPUS") );
	item_districtsF:SetIsDoneEvents("DistrictPlacementInterfaceMode");
	item_districtsF:SetNextTutorialItemId("DISTRICTS_G");

	-- ================================ DISTRICTS_G =====================================
	local item_districtsG:TutorialItem = TutorialItem:new("DISTRICTS_G");
	item_districtsG:SetPrereqs("DISTRICTS_F");
	item_districtsG:SetAdvisorMessage("LOC_META_81_BODY");
	item_districtsG:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsG:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsG:SetNextTutorialItemId("DISTRICTS_H");

	-- ================================ DISTRICTS_H =====================================
	local item:TutorialItem = TutorialItem:new("DISTRICTS_H");
	item:SetPrereqs("DISTRICTS_G");
	item:SetAdvisorMessage("LOC_META_82_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			UI.LookAtPlot(13,11);
		end );
	item:SetNextTutorialItemId("PLACE_DISTRICT");

	-- ================================ PLACE_DISTRICT =====================================
	local item:TutorialItem = TutorialItem:new("PLACE_DISTRICT");
	item:SetPrereqs("DISTRICTS_H");
	item:SetOpenFunction(
		function( )
			ClearAllUnitHexRestrictions();		-- Should be safe now to remove any restricted plots
			local kSelectableHexIds:table = { Map.GetPlot(13,11):GetIndex() };
			LuaEvents.Tutorial_DisableMapDrag( true );
			LuaEvents.Tutorial_DisableMapSelect( true, kSelectableHexIds );
			LuaEvents.Tutorial_DisableMapCancel( true );
			DimHexes( kSelectableHexIds );
		end );
	item:SetCleanupFunction(
		function( )
			LuaEvents.Tutorial_DisableMapDrag( false );
			LuaEvents.Tutorial_DisableMapSelect( false );
			LuaEvents.Tutorial_DisableMapCancel( false );
		end );
	item:SetAdvisorCallout("LOC_META_80_HEAD", "LOC_META_83_BODY",
		function()
			return Map.GetPlot(13,11):GetIndex();
		end);
	item:SetUITriggers("TutorialSelectUnit","WorldInput");
	item:SetEnabledControls(UITutorialManager:GetHash("WorldInput"), UITutorialManager:GetHash("PopupRoot"));
	item:SetOverlayEnabled( false );
	item:SetIsDoneEvents("CampusPlaced");
	item:SetNextTutorialItemId("DISTRICTS_I");

	-- =============================== DISTRICTS_I =====================================
	local item_districtsI:TutorialItem = TutorialItem:new("DISTRICTS_I");
	item_districtsI:SetRaiseEvents("CityProductionChanged_Campus");
	item_districtsI:SetPrereqs("DISTRICTS_H");
	item_districtsI:AddGoal("GOAL_7", "LOC_TUTORIAL_GOAL_7", "LOC_TUTORIAL_GOAL_TOOLTIP_7");
	item_districtsI:SetAdvisorMessage("ADVISOR_LINE_FTUE_40_ALT");
	item_districtsI:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_40_ALT");
	item_districtsI:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LockProduction();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_40_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsI:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsI:SetShowPortrait(true)
	item_districtsI:SetOpenFunction(
		function()
			LuaEvents.Tutorial_ForceHideWorldTracker()
		end );
	item_districtsI:SetNextTutorialItemId("DISTRICTS_I2");

	-- =============================== DISTRICTS_I2 =====================================
	local item_districtsI2:TutorialItem = TutorialItem:new("DISTRICTS_I2");
	item_districtsI2:SetPrereqs("DISTRICTS_I");
	item_districtsI2:SetAdvisorMessage("ADVISOR_LINE_FTUE_401");
	item_districtsI2:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_401");
	item_districtsI2:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_401")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsI2:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsI2:SetShowPortrait(true)
	item_districtsI2:SetNextTutorialItemId("DISTRICTS_J");

	-- ================================ DISTRICTS_J =====================================
	local item_districtsJ:TutorialItem = TutorialItem:new("DISTRICTS_J");
	item_districtsJ:SetPrereqs("DISTRICTS_I");
	item_districtsJ:SetAdvisorMessage("LOC_META_84_BODY");
	item_districtsJ:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsJ:SetIsDoneFunction(
		function()
			return false;
		end );
	item_districtsJ:SetNextTutorialItemId("DISTRICTS_K");

	-- ================================ DISTRICTS_K =====================================
	local item_districtsJ:TutorialItem = TutorialItem:new("DISTRICTS_K");
	item_districtsJ:SetPrereqs("DISTRICTS_J");
	item_districtsJ:SetIsEndOfChain(true)
	item_districtsJ:SetAdvisorMessage("LOC_META_85_BODY");
	item_districtsJ:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_districtsJ:SetIsDoneFunction(
		function()
			return false;
		end );

	-- ================================ CAMPUS_COMPLETE_A =====================================
	local item_campusCompleteA:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_A");
	--item_campusCompleteA:SetPrereqs("DISTRICTS_J");
	item_campusCompleteA:SetIsQueueable(true)
	item_campusCompleteA:SetRaiseEvents("CapitalCampusProductionCompleted");
	item_campusCompleteA:SetCompletedGoals("GOAL_7");
	item_campusCompleteA:SetAdvisorMessage("ADVISOR_LINE_FTUE_41_ALT");
	item_campusCompleteA:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_41_ALT");
	item_campusCompleteA:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_41_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteA:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteA:SetNextTutorialItemId("CAMPUS_COMPLETE_B");
	item_campusCompleteA:SetShowPortrait(true)
	item_campusCompleteA:SetOpenFunction(
		function()
			UI.LookAtPlot(13,11);
		end );

	-- ================================ CAMPUS_COMPLETE_B =====================================
	local item_campusCompleteB:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_B");
	item_campusCompleteB:SetPrereqs("CAMPUS_COMPLETE_A");
	item_campusCompleteB:SetAdvisorMessage("LOC_META_86_BODY");
	item_campusCompleteB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteB:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteB:SetOpenFunction(
		function()
			UI.LookAtPlot(13,11);
		end );
	item_campusCompleteB:SetNextTutorialItemId("CAMPUS_COMPLETE_C");

	-- =============================== CAMPUS_COMPLETE_C =====================================
	-- TODO(asherburne): Select city so production button can be highlighted.
--	local item_campusCompleteC:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_C");
--	item_campusCompleteC:SetPrereqs("CAMPUS_COMPLETE_B");
--	item_campusCompleteC:SetAdvisorMessage("LOC_META_87_BODY");
--	item_campusCompleteC:SetUITriggers("ChooseProductionMenu", "TutorialBuildLibrary");
--	item_campusCompleteC:SetEnabledControls( UITutorialManager:GetHash("BUILDING_LIBRARY") );
--	item_campusCompleteC:SetIsDoneEvents("CityProductionChanged");
--	item_campusCompleteC:SetNextTutorialItemId("CAMPUS_COMPLETE_D");
--	item_campusCompleteC:SetOpenFunction(
--		function( )
--			local player = GetPlayer();
--			local capitalCity = player:GetCities():GetCapitalCity();
--			UI.SelectCity( capitalCity );	-- Immediate call instead of waiting for callback
--			LuaEvents.Tutorial_CityPanelOpen();
--		end );
	-- =============================== CAMPUS_COMPLETE_C =====================================
	local item_campusCompleteC:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_C");
	item_campusCompleteC:SetPrereqs("CAMPUS_COMPLETE_B");
	item_campusCompleteC:SetAdvisorMessage("LOC_META_87_BODY");
	item_campusCompleteC:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ShowDetails( advisorInfo );
		end );
	item_campusCompleteC:SetOpenFunction(
		function( )
			local player = GetPlayer();
			if player == nil then
				error("Unable to obtain player in Open City Panel tutorial item.");
			end
			local capitalCity = player:GetCities():GetCapitalCity();
			if capitalCity == nil then
				error("Unable to obtain capital city in Open City Panel tutorial item.");
			end
			UI.SelectCity( capitalCity );	-- Immediate call instead of waiting for callback
			LuaEvents.Tutorial_CityPanelOpen();
		end );
	item_campusCompleteC:SetUITriggers("CityPanel", "TutorialOpenProduction" );
	item_campusCompleteC:SetEnabledControls(UITutorialManager:GetHash("ChangeProductionCheck"));
	item_campusCompleteC:SetIsDoneEvents("ProductionPanelViaCityOpen");
	item_campusCompleteC:SetNextTutorialItemId("CAMPUS_COMPLETE_D");

	-- =============================== CAMPUS_COMPLETE_D =====================================
	local item_campusCompleteD:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_D");
	item_campusCompleteD:SetPrereqs("CAMPUS_COMPLETE_C");
	item_campusCompleteD:SetAdvisorMessage("LOC_META_87_BODY");
	item_campusCompleteD:SetUITriggers("ChooseProductionMenu", "TutorialBuildLibrary");
	item_campusCompleteD:SetEnabledControls( UITutorialManager:GetHash("BUILDING_LIBRARY") );
	item_campusCompleteD:SetIsDoneEvents("CityProductionChanged_Library");
	item_campusCompleteD:SetNextTutorialItemId("CAMPUS_COMPLETE_D2");

	-- ================================ CAMPUS_COMPLETE_D2 =====================================
	local item_campusCompleteD2:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_D2");
	item_campusCompleteD2:SetPrereqs("CAMPUS_COMPLETE_D");
	item_campusCompleteD2:SetAdvisorMessage("ADVISOR_LINE_FTUE_END_SCRIPTED_ALT");
	item_campusCompleteD2:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_END_SCRIPTED_ALT");
	item_campusCompleteD2:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LockProduction();
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_END_SCRIPTED_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteD2:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteD2:SetShowPortrait(true)
	item_campusCompleteD2:SetOpenFunction(
		function()
			UserConfiguration.SetLockedValue("AutoUnitCycle", true);
		end );
	item_campusCompleteD2:SetNextTutorialItemId("CAMPUS_COMPLETE_E");

	-- ================================ CAMPUS_COMPLETE_E =====================================
	-- This is the beginning of the HOW TO WIN chapter.
	local item_campusCompleteE:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_E");
	item_campusCompleteE:SetPrereqs("CAMPUS_COMPLETE_D2");
	item_campusCompleteE:SetAdvisorMessage("LOC_META_118_BODY");
	item_campusCompleteE:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteE:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteE:SetNextTutorialItemId("CAMPUS_COMPLETE_F");

	-- =============================== CAMPUS_COMPLETE_F =====================================
	local item_campusCompleteF:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_F");
	item_campusCompleteF:SetPrereqs("CAMPUS_COMPLETE_E");
	item_campusCompleteF:SetAdvisorMessage("ADVISOR_LINE_FTUE_END_SCRIPTED_2");
	item_campusCompleteF:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_END_SCRIPTED_2");
	item_campusCompleteF:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_END_SCRIPTED_2")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteF:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteF:SetShowPortrait(true)
	item_campusCompleteF:SetNextTutorialItemId("CAMPUS_COMPLETE_G");

	-- ================================ CAMPUS_COMPLETE_G =====================================
	local item_campusCompleteG:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_G");
	item_campusCompleteG:SetPrereqs("CAMPUS_COMPLETE_F");
	item_campusCompleteG:SetAdvisorMessage("LOC_META_119_BODY");
	item_campusCompleteG:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteG:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteG:SetNextTutorialItemId("OPEN_WORLD_RANKINGS");

	-- ================================ OPEN_WORLD_RANKINGS =====================================
	local item:TutorialItem = TutorialItem:new("OPEN_WORLD_RANKINGS");
	item:SetPrereqs("CAMPUS_COMPLETE_G");
	item:SetUITriggers("PartialScreenHooks", "TutorialOpenWorldRankings" );
	item:SetEnabledControls(UITutorialManager:GetHash("WorldRankingsButton"));
	item:SetIsDoneEvents("WorldRankingsOpened");
	item:SetNextTutorialItemId("CAMPUS_COMPLETE_H");

	-- ================================ CAMPUS_COMPLETE_H =====================================
	local item_campusCompleteH:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_H");
	item_campusCompleteH:SetPrereqs("CAMPUS_COMPLETE_G");
	item_campusCompleteH:SetAdvisorMessage("LOC_META_120_BODY");
	item_campusCompleteH:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteH:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteH:SetNextTutorialItemId("CAMPUS_COMPLETE_I");

	-- ================================ CAMPUS_COMPLETE_I =====================================
	local item_campusCompleteI:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_I");
	item_campusCompleteI:SetPrereqs("CAMPUS_COMPLETE_H");
	item_campusCompleteI:SetAdvisorMessage("LOC_META_121_BODY");
	item_campusCompleteI:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteI:SetIsDoneFunction(
		function()
			return false;
		end );

	-- ================================ CAMPUS_COMPLETE_J =====================================
	local item:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_J");
	item:SetIsQueueable(true);
	item:SetRaiseEvents("WorldRankingsClosed");
	item:SetPrereqs("CAMPUS_COMPLETE_I");
	item:SetAdvisorMessage("LOC_META_122_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("CAMPUS_COMPLETE_K");

	-- ================================ CAMPUS_COMPLETE_K =====================================
	local item_campusCompleteK:TutorialItem = TutorialItem:new("CAMPUS_COMPLETE_K");
	item_campusCompleteK:SetPrereqs("CAMPUS_COMPLETE_J");
	item_campusCompleteK:SetIsEndOfChain(true);
	item_campusCompleteK:SetAdvisorMessage("LOC_META_123_BODY");
	item_campusCompleteK:AddGoal("GOAL_14", "LOC_TUTORIAL_GOAL_14", "LOC_TUTORIAL_GOAL_14");
	item_campusCompleteK:AddGoal("GOAL_15", "LOC_TUTORIAL_GOAL_15", "LOC_TUTORIAL_GOAL_15");
	item_campusCompleteK:AddGoal("GOAL_17", "LOC_TUTORIAL_GOAL_17", "LOC_TUTORIAL_GOAL_17");
	item_campusCompleteK:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_campusCompleteK:SetIsDoneFunction(
		function()
			return false;
		end );
	item_campusCompleteK:SetOpenFunction(
		function()
			LuaEvents.Tutorial_EndTutorialRestrictions(); --Removes (some) control restrictions, because the on-rails portion of the tutorial has ended 

			-- Removing goals during the Open function is currently okay since the open function
			-- is called before goals are initialized.
			if( TutorialItemCompleted("CapitalWallsProductionCompleted") ) then
				item_campusCompleteK:RemoveGoal("GOAL_14");
			end

			if( TutorialItemCompleted("BarracksProductionCompleted") ) then
				item_campusCompleteK:RemoveGoal("GOAL_15");
			end
		end );
	item_campusCompleteK:SetAdvisorUITriggers("TopPanel", "TutorialCivilopediaPointer");

	-- =============================== Non Sequential Items =====================================
	-- =============================== BARBARIAN_CAMP_DISCOVERED_A =====================================
	local item_barbarianCampDiscovered_A:TutorialItem = TutorialItem:new("BARBARIAN_CAMP_DISCOVERED_A");
	item_barbarianCampDiscovered_A:SetIsQueueable(true)
	item_barbarianCampDiscovered_A:SetRaiseEvents("BarbarianVillageDiscovered");
	item_barbarianCampDiscovered_A:SetAdvisorMessage("ADVISOR_LINE_2_ALT");
	item_barbarianCampDiscovered_A:SetAdvisorAudio("Play_ADVISOR_LINE_2_ALT");
	item_barbarianCampDiscovered_A:AddAdvisorButton("LOC_ADVISOR_BUTTON_AGREED",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_2_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_barbarianCampDiscovered_A:SetIsDoneFunction(
		function()
			return false;
		end );
	item_barbarianCampDiscovered_A:SetNextTutorialItemId("BARBARIAN_CAMP_DISCOVERED_B");
	item_barbarianCampDiscovered_A:SetShowPortrait(true)

	-- =============================== BARBARIAN_CAMP_DISCOVERED_B =====================================
	local item_barbarianCampDiscovered_B:TutorialItem = TutorialItem:new("BARBARIAN_CAMP_DISCOVERED_B");
	item_barbarianCampDiscovered_B:SetPrereqs("BARBARIAN_CAMP_DISCOVERED_A");
	item_barbarianCampDiscovered_B:SetAdvisorMessage("ADVISOR_LINE_3_ALT");
	item_barbarianCampDiscovered_B:SetAdvisorAudio("Play_ADVISOR_LINE_3_ALT");
	item_barbarianCampDiscovered_B:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_3_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_barbarianCampDiscovered_B:SetIsDoneFunction(
		function()
			return false;
		end );
	item_barbarianCampDiscovered_B:SetNextTutorialItemId("BARBARIAN_CAMP_DISCOVERED_C");
	item_barbarianCampDiscovered_B:SetShowPortrait(true)

	-- =============================== BARBARIAN_CAMP_DISCOVERED_C =====================================
	local item_barbarianCampDiscovered_C:TutorialItem = TutorialItem:new("BARBARIAN_CAMP_DISCOVERED_C");
	item_barbarianCampDiscovered_C:SetPrereqs("BARBARIAN_CAMP_DISCOVERED_B");
	item_barbarianCampDiscovered_C:SetIsEndOfChain(true)
	item_barbarianCampDiscovered_C:SetAdvisorMessage("LOC_META_124_BODY");
	item_barbarianCampDiscovered_C:SetIsDoneFunction(
		function()
			return false;
		end );
	item_barbarianCampDiscovered_C:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );

	-- =============================== CITY_POPULATION_CHANGED_A =====================================
	local item_populationChanged_A:TutorialItem = TutorialItem:new("CITY_POPULATION_CHANGED_A");
	item_populationChanged_A:SetIsQueueable(true)
	item_populationChanged_A:SetRaiseEvents("CityPopulationFirstChange");
	item_populationChanged_A:SetAdvisorMessage("ADVISOR_LINE_4_ALT");
	item_populationChanged_A:SetAdvisorAudio("Play_ADVISOR_LINE_4_ALT");
	item_populationChanged_A:AddAdvisorButton("LOC_ADVISOR_BUTTON_VERY_GOOD",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_4_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_populationChanged_A:SetIsDoneFunction(
		function()
			return false;
		end );
	item_populationChanged_A:SetNextTutorialItemId("CITY_POPULATION_CHANGED_B");
	item_populationChanged_A:SetShowPortrait(true)

	-- =============================== CITY_POPULATION_CHANGED_B =====================================
	local item_populationChanged_B:TutorialItem = TutorialItem:new("CITY_POPULATION_CHANGED_B");
	item_populationChanged_B:SetPrereqs("CITY_POPULATION_CHANGED_A");
	item_populationChanged_B:SetAdvisorMessage("LOC_META_125_BODY");
	item_populationChanged_B:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_populationChanged_B:SetIsDoneFunction(
		function()
			return false;
		end );
	item_populationChanged_B:SetNextTutorialItemId("CITY_POPULATION_CHANGED_C");

	-- =============================== CITY_POPULATION_CHANGED_C =====================================
	local item_populationChanged_C:TutorialItem = TutorialItem:new("CITY_POPULATION_CHANGED_C");
	item_populationChanged_C:SetPrereqs("CITY_POPULATION_CHANGED_B");
	item_populationChanged_C:SetIsEndOfChain(true)
	item_populationChanged_C:SetAdvisorMessage("LOC_META_126_BODY");
	item_populationChanged_C:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_populationChanged_C:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== BUILDER_CHARGES_DEPLETED =====================================
	local item_builderChargesDepleted:TutorialItem = TutorialItem:new("BUILDER_CHARGES_DEPLETED");
	item_builderChargesDepleted:SetIsQueueable(true)
	item_builderChargesDepleted:SetIsEndOfChain(true)
	item_builderChargesDepleted:SetCompletedGoals("GOAL_13")
	item_builderChargesDepleted:SetRaiseEvents("ImprovementsBuilt3");
	item_builderChargesDepleted:SetAdvisorMessage("LOC_META_74_BODY");
	item_builderChargesDepleted:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_builderChargesDepleted:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== NATURAL_WONDER_REVEALED =====================================
	local item_naturalWonderRevealed:TutorialItem = TutorialItem:new("NATURAL_WONDER_REVEALED");
	item_naturalWonderRevealed:SetIsQueueable(true)
	item_naturalWonderRevealed:SetRaiseEvents("NaturalWonderPopupClosed");
	item_naturalWonderRevealed:SetAdvisorMessage("ADVISOR_LINE_FTUE_WONDER_73");
	item_naturalWonderRevealed:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_WONDER_73");
	item_naturalWonderRevealed:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_WONDER_73")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_naturalWonderRevealed:SetIsDoneFunction(
		function()
			return false;
		end );
	item_naturalWonderRevealed:SetShowPortrait(true)
	item_naturalWonderRevealed:SetNextTutorialItemId("NATURAL_WONDER_REVEALED_B");

	-- =============================== NATURAL_WONDER_REVEALED_B =====================================
	local item_naturalWonderRevealedB:TutorialItem = TutorialItem:new("NATURAL_WONDER_REVEALED_B");
	item_naturalWonderRevealedB:SetPrereqs("NATURAL_WONDER_REVEALED");
	item_naturalWonderRevealedB:SetIsEndOfChain(true)
	item_naturalWonderRevealedB:SetAdvisorMessage("LOC_META_73_BODY");
	item_naturalWonderRevealedB:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_naturalWonderRevealedB:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== PLAYER_VICTORY_A =====================================
	local item_victory_a:TutorialItem = TutorialItem:new("PLAYER_VICTORY_A");
	item_victory_a:SetIsQueueable(true)
	item_victory_a:SetCompletedGoals("GOAL_12")
	item_victory_a:SetRaiseEvents("TeamVictory");
	item_victory_a:SetAdvisorMessage("ADVISOR_LINE_FTUE_END_SCRIPTED_3");
	item_victory_a:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_END_SCRIPTED_3");
	item_victory_a:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_END_SCRIPTED_3")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_victory_a:SetIsDoneFunction(
		function()
			return false;
		end );
	item_victory_a:SetShowPortrait(true)
	item_victory_a:SetNextTutorialItemId("PLAYER_VICTORY_B");
	
	-- =============================== PLAYER_VICTORY_B =====================================
	local item_victory_b:TutorialItem = TutorialItem:new("PLAYER_VICTORY_B");
	item_victory_b:SetPrereqs("PLAYER_VICTORY_A");
	item_victory_b:SetIsEndOfChain(true)
	item_victory_b:SetAdvisorMessage("LOC_META_88_BODY");
	item_victory_b:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item_victory_b:SetIsDoneFunction(
		function()
			return false;
		end );
	item_victory_b:SetCleanupFunction(
		function( )
            -- 1 is BANKS_MENU from the enum in AudioSystem.h, TODO: figure out how to tell Lua that.
			PlayFullScreenMovie( "TUT_OUTRO.bk2", 1, "Play_Cinematic_Tutorial_Outro", "Stop_Cinematic_Tutorial_Outro", false,
				function()
					LuaEvents.Tutorial_TutorialEndHideBulkUI();
					Events.ExitToMainMenu();					
				end );
		end );

end
-- ===========================================================================
--
--	2 two ii
--
-- ===========================================================================
function TutorialItemBank2()

	-- =============================== GOAL_9_COMPLETE =====================================
--	local item:TutorialItem = TutorialItem:new("GOAL_9_COMPLETE");
--	item:SetRaiseEvents("CityPopulationGreaterThanFive");
--	item:SetPrereqs("CAMPUS_COMPLETE_K");
--	item:SetIsQueueable(true)
--	item:SetIsEndOfChain(true)
--	item:SetCompletedGoals("GOAL_9")
--	item:SetAdvisorMessage("LOC_META_GOAL_9_COMPLETE");
--	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
--		function( advisorInfo )
--			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
--		end );
--	item:SetIsDoneFunction(
--		function()
--			return false;
--		end );
	
	-- =============================== GOAL_10_COMPLETE =====================================
--	local item:TutorialItem = TutorialItem:new("GOAL_10_COMPLETE");
--	item:SetRaiseEvents("BuilderChargesOneRemaining");
--	item:SetPrereqs("BUILDER_CHARGES_DEPLETED");
--	item:SetIsQueueable(true)
--	item:SetIsEndOfChain(true)
--	item:SetCompletedGoals("GOAL_10")
--	item:SetAdvisorMessage("LOC_META_GOAL_10_COMPLETE");
--	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
--		function( advisorInfo )
--			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
--		end );
--	item:SetIsDoneFunction(
--		function()
--			return false;
--		end );

	-- =============================== GOAL_8_COMPLETE =====================================
--	local item:TutorialItem = TutorialItem:new("GOAL_8_COMPLETE");
--	item:SetRaiseEvents("GoodyHutReward");
--	item:SetPrereqs("CAMPUS_COMPLETE_K");
--	item:SetIsQueueable(true)
--	item:SetIsEndOfChain(true)
--	item:SetCompletedGoals("GOAL_8")
--	item:SetAdvisorMessage("LOC_META_GOAL_8_COMPLETE");
--	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
--		function( advisorInfo )
--			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
--		end );
--	item:SetIsDoneFunction(
--		function()
--			return false;
--		end );

	-- =============================== GOAL_6_COMPLETE =====================================
	local item:TutorialItem = TutorialItem:new("GOAL_6_COMPLETE");
	item:SetRaiseEvents("ImprovementAddedToSecondCity");
	item:SetIsQueueable(true)
	item:SetIsEndOfChain(true)
	item:SetCompletedGoals("GOAL_6")
	item:SetAdvisorMessage("LOC_META_GOAL_6_COMPLETE");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== GOAL_14_COMPLETE =====================================
	local item:TutorialItem = TutorialItem:new("GOAL_14_COMPLETE");
	item:SetRaiseEvents("CapitalWallsProductionCompleted");
	item:SetIsQueueable(true)
	item:SetIsEndOfChain(true)
	item:SetCompletedGoals("GOAL_14")
	item:SetAdvisorMessage("LOC_META_GOAL_14_COMPLETE");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== GOAL_15_COMPLETE =====================================
	local item:TutorialItem = TutorialItem:new("GOAL_15_COMPLETE");
	item:SetRaiseEvents("BarracksProductionCompleted");
	item:SetIsQueueable(true)
	item:SetIsEndOfChain(true)
	item:SetCompletedGoals("GOAL_15")
	item:SetAdvisorMessage("LOC_META_GOAL_15_COMPLETE");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== GREAT_PEOPLE_A =====================================
	local item:TutorialItem = TutorialItem:new("GREAT_PEOPLE_A");
	item:SetIsQueueable(true);
	item:SetRaiseEvents("GreatPersonAvailable");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_50_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_50_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_VERY_GOOD",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_50_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)
	item:SetNextTutorialItemId("GREAT_PEOPLE_B");

	-- =============================== GREAT_PEOPLE_B =====================================
	local item:TutorialItem = TutorialItem:new("GREAT_PEOPLE_B");
	item:SetPrereqs("GREAT_PEOPLE_A");
	item:SetAdvisorMessage("LOC_META_136_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("GREAT_PEOPLE_C");

	-- =============================== GREAT_PEOPLE_C =====================================
	local item:TutorialItem = TutorialItem:new("GREAT_PEOPLE_C");
	item:SetPrereqs("GREAT_PEOPLE_B");
	item:SetUITriggers("LaunchBar", "TutorialOpenGP" );
	item:SetEnabledControls(UITutorialManager:GetHash("GreatPeopleButton"));
	item:SetIsDoneEvents("GreatPeopleOpened");
	item:SetNextTutorialItemId("GREAT_PEOPLE_D");

	-- =============================== GREAT_PEOPLE_D =====================================
	local item:TutorialItem = TutorialItem:new("GREAT_PEOPLE_D");
	item:SetPrereqs("GREAT_PEOPLE_C");
	item:SetAdvisorMessage("LOC_META_138_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("GreatPeoplePopup", "TutorialGPAbilityPointer");
	item:SetNextTutorialItemId("GREAT_PEOPLE_E");

	-- =============================== GREAT_PEOPLE_E =====================================
	local item:TutorialItem = TutorialItem:new("GREAT_PEOPLE_E");
	item:SetPrereqs("GREAT_PEOPLE_D");
	item:SetAdvisorMessage("LOC_META_139_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("GreatPeoplePopup", "TutorialGPCostPointer");
	item:SetNextTutorialItemId("GREAT_PEOPLE_F");

	-- =============================== GREAT_PEOPLE_F =====================================
	local item:TutorialItem = TutorialItem:new("GREAT_PEOPLE_F");
	item:SetPrereqs("GREAT_PEOPLE_E");
	item:SetIsEndOfChain(true);
	item:SetAdvisorMessage("LOC_META_140_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK", 
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== MEETS_ANOTHER_CIV_A =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_A");
	item:SetIsQueueable(true);
	item:SetRaiseEvents("DiploScene_SceneClosed");
	item:SetAdvisorMessage("ADVISOR_LINE_FTUE_42_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_42_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_VERY_GOOD",
		function( advisorInfo )
			UI.PlaySound("Stop_ADVISOR_LINE_FTUE_42_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_B");

	-- =============================== MEETS_ANOTHER_CIV_B =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_B");
	item:SetPrereqs("MEETS_ANOTHER_CIV_A");
	item:SetAdvisorMessage("LOC_META_156_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_C");

	-- =============================== MEETS_ANOTHER_CIV_C =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_C");
	item:SetPrereqs("MEETS_ANOTHER_CIV_B");
	item:SetAdvisorMessage("LOC_META_157_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	--item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_D");

	--[[
	-- =============================== MEETS_ANOTHER_CIV_D =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_D");
	item:SetPrereqs("MEETS_ANOTHER_CIV_C");
	item:SetAdvisorMessage("LOC_META_158_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("TopPanel", "TutorialDiploRibbon");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_E");

	-- =============================== MEETS_ANOTHER_CIV_E =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_E");
	item:SetPrereqs("MEETS_ANOTHER_CIV_D");
	item:SetUITriggers("TopPanel", "TutorialSelectLeaderIcon" );
	item:SetEnabledControls(UITutorialManager:GetHash("DiplomacyRibbon")); --would be ideal to lock out everything but the other leader
	item:SetIsDoneEvents("DiploActionView");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_F");

	-- =============================== MEETS_ANOTHER_CIV_F =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_F");
	item:SetPrereqs("MEETS_ANOTHER_CIV_E");
	item:SetAdvisorMessage("LOC_META_159_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_G");

	-- =============================== MEETS_ANOTHER_CIV_G =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_G");
	item:SetPrereqs("MEETS_ANOTHER_CIV_F");
	item:SetAdvisorMessage("LOC_META_160_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("DiplomacyActionView", "TutorialDiploDelegation");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_H");

	-- =============================== MEETS_ANOTHER_CIV_H =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_H");
	item:SetPrereqs("MEETS_ANOTHER_CIV_G");
	item:SetAdvisorMessage("LOC_META_161_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("DiplomacyActionView", "TutorialDiploDenounce");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_I");

	-- =============================== MEETS_ANOTHER_CIV_I =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_I");
	item:SetPrereqs("MEETS_ANOTHER_CIV_H");
	item:SetAdvisorMessage("LOC_META_162_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("DiplomacyActionView", "TutorialDiploDeal");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_J");

	-- =============================== MEETS_ANOTHER_CIV_J =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_J");
	item:SetPrereqs("MEETS_ANOTHER_CIV_I");
	item:SetAdvisorMessage("LOC_META_163_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			OpenDiploIntelView();
		end );
	item:SetAdvisorUITriggers("DiplomacyActionView", "TutorialDiploIntel");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_K");

	-- =============================== MEETS_ANOTHER_CIV_K =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_K");
	item:SetPrereqs("MEETS_ANOTHER_CIV_J");
	item:SetAdvisorMessage("LOC_META_164_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			OpenDiploAccessLevelView();
		end );
	item:SetAdvisorUITriggers("DiplomacyActionView", "TutorialDiploIntel");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_L");

	-- =============================== MEETS_ANOTHER_CIV_L =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_L");
	item:SetPrereqs("MEETS_ANOTHER_CIV_K");
	item:SetAdvisorMessage("LOC_META_165_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetOpenFunction(
		function()
			OpenDiploRelationshipView();
		end );
	item:SetAdvisorUITriggers("DiplomacyActionView", "TutorialDiploDetails");
	item:SetNextTutorialItemId("MEETS_ANOTHER_CIV_M");

	-- =============================== MEETS_ANOTHER_CIV_M =====================================
	local item:TutorialItem = TutorialItem:new("MEETS_ANOTHER_CIV_M");
	item:SetPrereqs("MEETS_ANOTHER_CIV_L");
	item:SetIsEndOfChain(true);
	item:SetAdvisorMessage("LOC_META_166_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			CloseDiploActionView();
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	--]]
		
	-- =============================== FIRST_PANTHEON_A =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_A");
	item:SetIsQueueable(true)
	item:SetRaiseEvents("PantheonAvailable");
	item:SetAdvisorMessage("LOC_ADVISOR_LINE_FTUE_48");
	item:SetAdvisorAudio("PLAY_ADVISOR_LINE_FTUE_48");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_VERY_GOOD",
		function( advisorInfo )
			UI.PlaySound("STOP_ADVISOR_LINE_FTUE_48")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true);
	item:SetNextTutorialItemId("FIRST_PANTHEON_B");

	-- =============================== FIRST_PANTHEON_B =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_B");
	item:SetPrereqs("FIRST_PANTHEON_A");
	item:SetAdvisorMessage("LOC_META_128_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetAdvisorUITriggers("TopPanel", "TutorialFaithYieldPointer");
	item:SetNextTutorialItemId("FIRST_PANTHEON_C");

	-- =============================== FIRST_PANTHEON_C =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_C");
	item:SetPrereqs("FIRST_PANTHEON_B");
	item:SetAdvisorMessage("LOC_META_129_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("FIRST_PANTHEON_D");

	-- =============================== FIRST_PANTHEON_D =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_D");
	item:SetPrereqs("FIRST_PANTHEON_C");
	item:SetUITriggers("LaunchBar", "TutorialOpenReligionScreen" );
	item:SetEnabledControls(UITutorialManager:GetHash("ReligionButton"));
	item:SetIsDoneEvents("PantheonPanelOpened");
	item:SetNextTutorialItemId("FIRST_PANTHEON_E");

	-- =============================== FIRST_PANTHEON_E =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_E");
	item:SetPrereqs("FIRST_PANTHEON_D");
	item:SetAdvisorMessage("LOC_META_129c");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("FIRST_PANTHEON_F");

	-- =============================== FIRST_PANTHEON_F =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_F");
	item:SetPrereqs("FIRST_PANTHEON_E");
	item:SetAdvisorMessage("LOC_META_129d");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );

	-- =============================== FIRST_PANTHEON_G =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_G");
	item:SetPrereqs("FIRST_PANTHEON_F");
	item:SetRaiseEvents("PantheonFounded");
	item:SetAdvisorMessage("LOC_META_130_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("FIRST_PANTHEON_H");

	-- =============================== FIRST_PANTHEON_H =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_H");
	item:SetPrereqs("FIRST_PANTHEON_G");
	item:SetAdvisorMessage("LOC_META_131_BODY");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetNextTutorialItemId("FIRST_PANTHEON_I");

	-- =============================== FIRST_PANTHEON_I =====================================
	local item:TutorialItem = TutorialItem:new("FIRST_PANTHEON_I");
	item:SetPrereqs("FIRST_PANTHEON_H");
	item:SetIsEndOfChain(true);
	item:SetUITriggers("PantheonChooser", "TutorialCloseReligionScreenPointer" );
	item:SetEnabledControls(UITutorialManager:GetHash("ModalControls"));
	item:SetIsDoneEvents("ReligionPanelClosed","PantheonPanelClosed");

	-- =============================== ILLEGAL_RESEARCH_CHANGE_A =====================================
	local item:TutorialItem = TutorialItem:new("ILLEGAL_RESEARCH_CHANGE_A");
	item:SetIsQueueable(true)
	item:SetShouldMarkSeen(false)
	item:SetRaiseEvents("IllegalResearchChange");
	item:SetAdvisorMessage("ADVISOR_LINE_5_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_5_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			ResetResearch();
			UI.PlaySound("Stop_ADVISOR_LINE_5_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)

	-- =============================== ILLEGAL_PRODUCTION_CHANGE_A =====================================
	local item:TutorialItem = TutorialItem:new("ILLEGAL_PRODUCTION_CHANGE_A");
	item:SetIsQueueable(true)
	item:SetShouldMarkSeen(false)
	item:SetRaiseEvents("IllegalProductionChange");
	item:SetAdvisorMessage("ADVISOR_LINE_6_ALT");
	item:SetAdvisorAudio("Play_ADVISOR_LINE_6_ALT");
	item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
		function( advisorInfo )
			ResetProduction();
			UI.PlaySound("Stop_ADVISOR_LINE_6_ALT")
			LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		end );
	item:SetIsDoneFunction(
		function()
			return false;
		end );
	item:SetShowPortrait(true)

-- =============================== AI_DECLARED_WAR_A =====================================
local item:TutorialItem = TutorialItem:new("AI_DECLARED_WAR_A");
item:SetIsQueueable(true);
item:SetRaiseEvents("DiploScene_SceneClosed");
item:SetRaiseFunction(
	function()
		local pDiplomacy:table	= GetPlayer():GetDiplomacy();
		for i, pPlayer in ipairs(PlayerManager.GetAliveMajors()) do			
			local iPlayer :number = pPlayer:GetID();
			if pDiplomacy:IsAtWarWith( iPlayer ) then
				return true;		-- At war, let's raise this event!
			end
		end
		return false;
	end);			
item:SetAdvisorMessage("ADVISOR_LINE_FTUE_43_ALT");
item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_43_ALT");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
	function( advisorInfo )
		UI.PlaySound("Stop_ADVISOR_LINE_FTUE_43_ALT")
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetShowPortrait(true)
item:SetNextTutorialItemId("AI_DECLARED_WAR_B");

-- =============================== AI_DECLARED_WAR_B =====================================
local item:TutorialItem = TutorialItem:new("AI_DECLARED_WAR_B");
item:SetPrereqs("AI_DECLARED_WAR_A");
item:SetAdvisorMessage("LOC_META_89_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetNextTutorialItemId("AI_DECLARED_WAR_C");

-- =============================== AI_DECLARED_WAR_C =====================================
local item:TutorialItem = TutorialItem:new("AI_DECLARED_WAR_C");
item:SetPrereqs("AI_DECLARED_WAR_B");
item:SetAdvisorMessage("LOC_META_90_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetNextTutorialItemId("AI_DECLARED_WAR_D");

-- =============================== AI_DECLARED_WAR_D =====================================
local item:TutorialItem = TutorialItem:new("AI_DECLARED_WAR_D");
item:SetPrereqs("AI_DECLARED_WAR_C");
item:SetAdvisorMessage("LOC_META_91_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );

-- =============================== FIRST_TRADE_ROUTE_A =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_ROUTE_A");
item:SetIsQueueable(true);
item:SetRaiseEvents("TradeRouteAdded");
item:SetAdvisorMessage("ADVISOR_LINE_LISTENER_6");
item:SetAdvisorAudio("Play_ADVISOR_LINE_LISTENER_6");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_VERY_GOOD",
	function( advisorInfo )
		UI.PlaySound("Stop_ADVISOR_LINE_LISTENER_6")
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetShowPortrait(true);
item:SetNextTutorialItemId("FIRST_TRADE_ROUTE_B");

-- =============================== FIRST_TRADE_ROUTE_B =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_ROUTE_B");
item:SetPrereqs("FIRST_TRADE_ROUTE_A");
item:SetAdvisorMessage("LOC_META_169_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );

-- =============================== FIRST_TRADE_UNIT_A =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_A");
item:SetIsQueueable(true);
item:SetRaiseEvents("TradeUnitCreated");
item:SetAdvisorMessage("ADVISOR_LINE_FTUE_51_ALT");
item:SetAdvisorAudio("Play_ADVISOR_LINE_FTUE_51_ALT");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_VERY_GOOD",
	function( advisorInfo )
		UI.PlaySound("Stop_ADVISOR_LINE_FTUE_51_ALT")
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
		local traderUnit = GetFirstUnitOfType("UNIT_TRADER");
		if (traderUnit ~= nil) then
			UI.SelectUnit(traderUnit);
			UI.LookAtPlot(traderUnit:GetX(), traderUnit:GetY());
		end
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetShowPortrait(true);
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_B");

-- =============================== FIRST_TRADE_UNIT_B =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_B");
item:SetPrereqs("FIRST_TRADE_UNIT_A");
item:SetAdvisorMessage("LOC_META_141_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_C");

-- =============================== FIRST_TRADE_UNIT_C =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_C");
item:SetPrereqs("FIRST_TRADE_UNIT_B");
item:SetAdvisorMessage("LOC_META_142_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetAdvisorUITriggers("TopPanel", "TutorialTradeRoutes");
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_E");

--[[
-- =============================== FIRST_TRADE_UNIT_D =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_D");
item:SetPrereqs("FIRST_TRADE_UNIT_C");
item:SetUITriggers("UnitPanel", "TutorialTradeRouteAction");
item:SetEnabledControls(UITutorialManager:GetHash("UnitPanel"), UnitOperationTypes.MAKE_TRADE_ROUTE);
item:SetOverlayEnabled( false );
item:SetIsDoneEvents("TradeRouteChooserOpened");
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_E");
--]]

-- =============================== FIRST_TRADE_UNIT_E =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_E");
item:SetPrereqs("FIRST_TRADE_UNIT_C");
item:SetAdvisorMessage("LOC_META_144_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_CONTINUE",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetAdvisorUITriggers("TradeRouteChooser", "TutorialTradePanel");
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_F");

-- =============================== FIRST_TRADE_UNIT_F =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_F");
item:SetPrereqs("FIRST_TRADE_UNIT_E");
item:SetAdvisorMessage("LOC_META_145_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_G");

-- =============================== FIRST_TRADE_UNIT_G =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_G");
item:SetPrereqs("FIRST_TRADE_UNIT_F");
item:SetUITriggers("TradeRouteChooser", "TutorialTradeRoute");
item:SetEnabledControls(UITutorialManager:GetHash("TradeRouteChooser"));
--item:SetOverlayEnabled( false );
item:SetIsDoneEvents("TradeRouteConsidered");
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_H");

-- =============================== FIRST_TRADE_UNIT_H =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_H");
item:SetPrereqs("FIRST_TRADE_UNIT_G");
item:SetUITriggers("TradeRouteChooser", "TutorialBeginRoute");
item:SetEnabledControls(UITutorialManager:GetHash("TradeRouteChooser"));
--item:SetOverlayEnabled( false );
item:SetIsDoneEvents("TradeRouteAddedToMap");
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_I");

-- =============================== FIRST_TRADE_UNIT_I =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_I");
item:SetPrereqs("FIRST_TRADE_UNIT_H");
item:SetAdvisorMessage("LOC_META_146_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );
item:SetNextTutorialItemId("FIRST_TRADE_UNIT_J");

-- =============================== FIRST_TRADE_UNIT_J =====================================
local item:TutorialItem = TutorialItem:new("FIRST_TRADE_UNIT_J");
item:SetPrereqs("FIRST_TRADE_UNIT_I");
item:SetAdvisorMessage("LOC_META_147_BODY");
item:AddAdvisorButton("LOC_ADVISOR_BUTTON_OK",
	function( advisorInfo )
		LuaEvents.AdvisorPopup_ClearActive( advisorInfo );
	end );
item:SetIsDoneFunction(
	function()
		return false;
	end );



end


-- ===========================================================================
--
--	HELPER Functions
--
-- ===========================================================================

-- ===========================================================================
function GetPlayer()
	local playerID = Game.GetLocalPlayer();
	if (playerID == PlayerTypes.NONE) then
		return nil;
	end
	return Players[playerID];
end

-- ===========================================================================
-- Obtain # of cities the current player has
function GetCityCount()
	local playerID = Game.GetLocalPlayer();
	if (playerID == PlayerTypes.NONE) then
		return -1;
	end
	local pPlayer = Players[playerID];
	local cities = pPlayer:GetCities();
	return cities:GetCount();
end

-- ===========================================================================
function IsUnitVaild()
	local pUnit = UI.GetHeadSelectedUnit();
	if pUnit == nil then 
		return false;
	end
	return true;
end

-- ===========================================================================
function IsAbleToBuildFirstCity()
	local pUnit = UI.GetHeadSelectedUnit();
	if pUnit == nil then 
		return false;
	end
	if ( UnitManager.CanStartOperation(pUnit, UnitOperationTypes.FOUND_CITY) and GetCityCount() == 0) then
		return true;
	end

	return false;
end

-- ===========================================================================
function HasFoundedFirstCity()
	local cityCount = GetCityCount();
	if ( GetCityCount() == 1 ) then
		return true;
	end

	return false;
end

-- ===========================================================================
function UnitNotCityBuilder()
	local pUnit = UI.GetHeadSelectedUnit();
	if pUnit == nil then 
		return false;
	end
	if ( UnitManager.CanStartOperation(pUnit, UnitOperationTypes.FOUND_CITY) ) then
		return false;
	end

	return true;
end

-- ===========================================================================
function UnitHasMovesLeft()
	local pUnit = UI.GetHeadSelectedUnit();
	if ( pUnit ~= nil ) then 
		if ( UnitManager.CanStartOperation(pUnit, UnitOperationTypes.MOVE_TO) ) then
			return true;
		end
	end
	return false;
end

-- ===========================================================================
function CenterOnFirstUnit( bHighLightHex:boolean )
	local pPlayer = GetPlayer();
	if ( pPlayer ~= nil )  then
		local pUnit = pPlayer:GetUnits():GetFirstReadyUnit();
		if ( pUnit ~= nil ) then
			local pPlot = Map.GetPlot(pUnit:GetX(), pUnit:GetY());
			UI.LookAtPlot(pPlot);
			if bHighLightHex then
				local kHexIndexes:table = { pPlot:GetIndex() };
				DimHexes( kHexIndexes );
			end
			return pUnit;
		end
	end
end

-- ===========================================================================
--	Use the mask lens layer to dim hexes not in the list.
-- ===========================================================================
function DimHexes( kHexIndexes:table )
	local mapHexMask : number = UILens.CreateLensLayerHash("Map_Hex_Mask");
	UILens.SetLayerHexesArea( mapHexMask, Game.GetLocalPlayer(), kHexIndexes );
end

-- ===========================================================================
function ClearDimHexes()
	local mapHexMask : number = UILens.CreateLensLayerHash("Map_Hex_Mask");
	UILens.ClearLayerHexes( mapHexMask );
end

-- ===========================================================================
function GetUnitType( playerID: number, unitID : number )
	if( playerID == Game.GetLocalPlayer() ) then
		local pPlayer	:table = Players[playerID];
		local pUnit		:table = pPlayer:GetUnits():FindID(unitID);
		if pUnit ~= nil then
			return GameInfo.Units[pUnit:GetUnitType()].UnitType;
		end
	end
	return nil;
end

-- ===========================================================================
function IsTurnFinished()
	local pPlayer = GetPlayer();
	if ( pPlayer ~= nil ) then
		local endTurnBlockingType = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
		if (endTurnBlockingType == EndTurnBlockingTypes.NO_ENDTURN_BLOCKING) then
			return true;
		end
	end
	return false;
end

-- ===========================================================================
function IsBlockedOnProduction()
	local pPlayer = GetPlayer();
	if ( pPlayer ~= nil )  then
		local endTurnBlockingType = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
		if (endTurnBlockingType == EndTurnBlockingTypes.ENDTURN_BLOCKING_PRODUCTION) then
			return true;
		end
	end
	return false;
end

-- ===========================================================================
function IsBlockedOnResearch()
	local pPlayer = GetPlayer();
	if ( pPlayer ~= nil )  then
		local endTurnBlockingType = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
		if (endTurnBlockingType == EndTurnBlockingTypes.ENDTURN_BLOCKING_RESEARCH) then
			return true;
		end
	end
	return false;
end

-- ===========================================================================
--	Tell world input to only accept a plot as a target movement
-- ===========================================================================
function BeginMovementRestriction( pPlot:table )
	local hexIndex:number = pPlot:GetIndex();
	DimHexes( {hexIndex} );	
	LuaEvents.Tutorial_ConstrainMovement( hexIndex );	
end

-- ===========================================================================
function EndMovementRestriction()
	ClearDimHexes();
	-- tell worldinput to allow all movement
	LuaEvents.Tutorial_ConstrainMovement( 0 );
end

-- ===========================================================================
function ForceMoveUnitOnePlot()
	local pPlayer = GetPlayer();
	if ( pPlayer ~= nil )  then
		local pUnit = pPlayer:GetUnits():GetFirstReadyUnit();
		if ( pUnit ~= nil ) then
			local adjacentPlot;
			for direction = 1, DirectionTypes.NUM_DIRECTION_TYPES - 1, 1 do
				adjacentPlot = Map.GetAdjacentPlot(pUnit:GetX(), pUnit:GetY(), direction);
				if (adjacentPlot ~= nil) then
					local bIsValid:boolean = not ( adjacentPlot:IsWater() or adjacentPlot:IsImpassable() );
					if bIsValid then
						BeginMovementRestriction( adjacentPlot );
						break;
					end
				end
			end
		end
	end
end

-- ===========================================================================
function ForceMoveUnitDirection(direction)
	local pUnit = UI.GetHeadSelectedUnit()

	if pUnit ~= nil then
		local adjacentPlot = Map.GetAdjacentPlot(pUnit:GetX(), pUnit:GetY(), direction)

		if adjacentPlot ~= nil then
			local bIsValid:boolean = not (adjacentPlot:IsWater() or adjacentPlot:IsImpassable())

			if bIsValid then
				BeginMovementRestriction(adjacentPlot)
			end
		end
	end
end

-- ===========================================================================
function ForceMoveUnitRelative(x, y)
	local pUnit = UI.GetHeadSelectedUnit()

	if pUnit ~= nil then
		local relativePlot :table = Map.GetPlot(pUnit:GetX() + x, pUnit:GetY() + y);
		if relativePlot ~= nil then
			local bIsValid:boolean = not (relativePlot:IsWater() or relativePlot:IsImpassable())
			if bIsValid then
				BeginMovementRestriction(relativePlot)
			end
		end
	end
end

-- ===========================================================================
function ForceMoveUnitToCapital()
	local playerID = Game.GetLocalPlayer();
	local player = Players[playerID];
	local playerCities = player:GetCities();
	local capitalCity = playerCities:GetCapitalCity();
	local plotX = capitalCity:GetX();
	local plotY = capitalCity:GetY();
	local plot = Map.GetPlot(plotX, plotY);

	if plot ~= nil then
		BeginMovementRestriction(plot);
	end
end

function ForceMoveUnitEastward()
	local playerID = Game.GetLocalPlayer();
	local player = Players[playerID];
	local playerCities = player:GetCities();
	local capitalCity = playerCities:GetCapitalCity();
	local plotX = capitalCity:GetX() + 4;
	local plotY = capitalCity:GetY() - 1;
	local plot = Map.GetPlot(plotX, plotY);

	if plot ~= nil then
		BeginMovementRestriction(plot);
	end
end

function GetFirstUnitOfType(typeName)
	local localPlayer = Game.GetLocalPlayer()
	local player = Players[localPlayer]
	local playerUnits = player:GetUnits()

	for i, unit in playerUnits:Members() do
		local unitTypeName = UnitManager.GetTypeName(unit)

		if typeName == unitTypeName then
			return unit
		end
	end

	return nil
end

-- ===========================================================================
--	Return a plot object for a given unit.
-- ===========================================================================
function GetPlotOfUnit( pUnit:table)
	if (pUnit ~= nil) then
		return Map.GetPlot(pUnit:GetX(), pUnit:GetY());
	end
end


-- ===========================================================================
--	If a player has opened a sub-screen, close it.
-- ===========================================================================
function CloseScreensIfOpen()
	LuaEvents.Tutorial_CloseAllPartialScreens();
	LuaEvents.Tutorial_CloseAllLaunchBarScreens();
end

-- ===========================================================================
--	If any dynamically allocated tree (civics / tech) is open, reparent
--	the tutorial tree nodes to ensure they draw on top of all the things.
-- ===========================================================================
function ReparentTutorialTreeNodes()

	local pCivicsTree:table = ContextPtr:LookUpControl( "/InGame/CivicsTree/" );
	if pCivicsTree then
		local kTutorialControlNames:table = {"NodePointer"};
		for _,controlName in ipairs(kTutorialControlNames) do
			local pControl:table = ContextPtr:LookUpControl( "/InGame/CivicsTree/"..controlName);
			if pControl then
				pControl:Reparent();
			else
				UI.DataError("Tutorial was unable to reparent the Civics Tree control '"..controlName.."' because it doesn't exist.");
			end
		end
	end

	local pTechTree:table = ContextPtr:LookUpControl( "/InGame/TechTree/" );
	if pTechTree then
		local kTutorialControlNames:table = {"CompletedTechNodePointer","IncompleteTechNodePointer","UnavailableTechNodePointer","ChooseWritingPointer","ActiveTechNodePointer","TechUnlocksPointer"};
		for _,controlName in ipairs(kTutorialControlNames) do
			local pControl:table = ContextPtr:LookUpControl( "/InGame/TechTree/"..controlName);
			if pControl then
				pControl:Reparent();
			else
				UI.DataError("Tutorial was unable to reparent the Tech Tree control '"..controlName.."' because it doesn't exist.");
			end
		end
	end
	
end