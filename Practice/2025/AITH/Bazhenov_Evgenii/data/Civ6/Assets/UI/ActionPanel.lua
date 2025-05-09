-- ===========================================================================
--	Action Panel
--	Main area of game to advance turns and show what is currently blocking.
--	Tabs set to 4 spaces; retaining tab.
-- ===========================================================================

include( "InstanceManager" );
include( "SupportFunctions" );
include( "Civ6Common" ); -- IsTutorialRunning()
include( "PopupDialog" );
include( "GameCapabilities" );

-- ===========================================================================
--	CONSTANTS
-- ===========================================================================
local NO_FLASHING					:number = 0;
local FLASHING_END_TURN				:number = 1;
local FLASHING_SCIENCE				:number = 2;
local FLASHING_PRODUCTION			:number = 3;
local FLASHING_FREE_TECH			:number = 4;
local FLASHING_NEEDS_ORDERS			:number = 5;

local TURN_TIMER_BAR_ACTIVE_COLOR = UI.GetColorValue("COLOR_WHITE");
local TURN_TIMER_BAR_INACTIVE_COLOR = UI.GetColorValue(1,0,0,1);

local MAX_BLOCKER_BUTTONS			:number = 4;	-- Number of buttons around big action button
local autoEndTurnOptionHash			:number = DB.MakeHash("AutoEndTurn");
local cityRangeAttackTurnOptionHash	:number = DB.MakeHash("CityRangeAttackTurnBlocking");

local MAX_BEFORE_TRUNC_TURN_STRING	:number = 150;

local START_TURN_TIMER_TICK_SOUND	:number	= 7;  -- Start making turn timer ticking sounds when the turn timer is lower than this seconds.

local NO_PLAYER						:number = -1;

local CloudTurnStates = {
	CLOUDTURN_NONE			= 0,
	CLOUDTURN_UPLOADING		= 1,
	CLOUDTURN_UPLOADED		= 2,
};

-- End Turn Button Strings
local pleaseWaitString 				:string	= Locale.Lookup("LOC_ACTION_PANEL_PLEASE_WAIT");
local pleaseWaitTip					:string	= Locale.Lookup("LOC_ACTION_PANEL_PLEASE_WAIT_TOOLTIP");
local skipTurnString 				:string	= Locale.Lookup("LOC_ACTION_PANEL_SKIP_TURN");
local skipTurnTip 					:string	= Locale.Lookup("LOC_ACTION_PANEL_SKIP_TURN_TOOLTIP");
local moveStackedUnitString 		:string	= Locale.Lookup("LOC_ACTION_PANEL_STACKED_UNIT");
local moveStackedUnitTip 			:string	= Locale.Lookup("LOC_ACTION_PANEL_STACKED_UNIT_TOOLTIP");
local unitNeedsOrdersString 		:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_ORDERS");
local unitNeedsOrdersTip 			:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_ORDERS_TOOLTIP");
local waitForPlayersString 			:string	= Locale.Lookup("LOC_ACTION_PANEL_WAITING_FOR_PLAYERS");
local waitForPlayersTip 			:string	= Locale.Lookup("LOC_ACTION_PANEL_WAITING_FOR_PLAYERS_TOOLTIP");
local waitForPlayerTurnString		:string = "LOC_ACTION_PANEL_WAITING_FOR_PLAYER_TURN";
local nextTurnString 				:string	= Locale.Lookup("LOC_ACTION_PANEL_NEXT_TURN");
local nextTurnTip					:string	= Locale.Lookup("LOC_ACTION_PANEL_NEXT_TURN_TOOLTIP");
local needResearchString			:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_RESEARCH");
local needResearchTip				:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_RESEARCH_TOOLTIP");
local needCivicString				:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_CIVIC");
local needCivicTip					:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_CIVIC_TOOLTIP");
local fillCivicString				:string	= Locale.Lookup("LOC_ACTION_PANEL_FILL_CIVIC_SLOT");
local fillCivicTip					:string	= Locale.Lookup("LOC_ACTION_PANEL_FILL_CIVIC_SLOT_TOOLTIP");
local considerGovernmentString		:string	= Locale.Lookup("LOC_ACTION_PANEL_CONSIDER_GOVERNMENT_CHANGE");
local considerGovernmentTip			:string	= Locale.Lookup("LOC_ACTION_PANEL_CONSIDER_GOVERNMENT_CHANGE_TOOLTIP");
local considerRazeCityString		:string	= Locale.Lookup("LOC_ACTION_PANEL_CONSIDER_RAZE_CITY");
local considerRazeCityTip			:string	= Locale.Lookup("LOC_ACTION_PANEL_CONSIDER_RAZE_CITY_TOOLTIP");
local needProductionString			:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_PRODUCTION");
local needProductionTip				:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_PRODUCTION_TOOLTIP");
local needPantheonString			:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_PANTHEON");
local needPantheonTip				:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_PANTHEON_TOOLTIP");
local needReligionString			:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_RELIGION");
local needReligionTip				:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_RELIGION_TOOLTIP");
local needBeliefString				:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_BELIEF");
local needBeliefTip					:string	= Locale.Lookup("LOC_ACTION_PANEL_NEEDS_BELIEF_TOOLTIP");
local giveInfluenceTokenString		:string = Locale.Lookup("LOC_ACTION_PANEL_GIVE_INFLUENCE_TOKEN");
local giveInfluenceTokenTip			:string = Locale.Lookup("LOC_ACTION_PANEL_GIVE_INFLUENCE_TOKEN_TOOLTIP");
local claimGreatPersonString		:string = Locale.Lookup("LOC_ACTION_PANEL_CLAIM_GREAT_PERSON");
local claimGreatPersonTip			:string = Locale.Lookup("LOC_ACTION_PANEL_CLAIM_GREAT_PERSON_TOOLTIP");
local unitsHaveMovesString			:string	= Locale.Lookup("LOC_ACTION_PANEL_UNIT_MOVES_REMAINING");
local unitsHaveMovesTip				:string	= Locale.Lookup("LOC_ACTION_PANEL_UNIT_MOVES_REMAINING_TOOLTIP");
local chooseEscapeRouteString		:string = Locale.Lookup("LOC_ACTION_PANEL_CHOOSE_ESCAPE_ROUTE");
local chooseEscapeRouteTip			:string = Locale.Lookup("LOC_ACTION_PANEL_CHOOSE_ESCAPE_ROUTE_TOOLTIP");
local chooseDragnetPriorityString	:string = Locale.Lookup("LOC_ACTION_PANEL_CHOOSE_DRAGNET_PRIORITY");
local chooseDragnetPriorityTip		:string = Locale.Lookup("LOC_ACTION_PANEL_CHOOSE_DRAGNET_PRIORITY_TOOLTIP");
local needArtifactPlayerString		:string	= Locale.Lookup("LOC_ACTION_PANEL_CHOOSE_ARTIFACT_PLAYER");
local needArtifactPlayerTip			:string	= Locale.Lookup("LOC_ACTION_PANEL_CHOOSE_ARTIFACT_PLAYER_TOOLTIP");
local cityRangedAttackString		:string	= Locale.Lookup("LOC_ACTION_PANEL_CITY_RANGED_ATTACK");
local cityRangedAttackTip			:string	= Locale.Lookup("LOC_ACTION_PANEL_CITY_RANGED_ATTACK_TOOLTIP");
local cloudTurnUploadingString		:string	= Locale.Lookup("LOC_ACTION_PANEL_CLOUD_TURN_UPLOADING");
local cloudTurnUploadingTip			:string	= Locale.Lookup("LOC_ACTION_PANEL_CLOUD_TURN_UPLOADING_TOOLTIP");
local cloudTurnUploadedString		:string	= Locale.Lookup("LOC_ACTION_PANEL_CLOUD_TURN_UPLOADED");
local cloudTurnUploadedTip			:string	= Locale.Lookup("LOC_ACTION_PANEL_CLOUD_TURN_UPLOADED_TOOLTIP");
local yourTurnToolStr				:string = Locale.Lookup("LOC_KEY_YOUR_TURN_TIME_TOOLTIP");
local estTilTurnToolStr				:string = Locale.Lookup("LOC_KEY_ESTIMATED_TIME_TIL_YOUR_TURN_TIME_TOOLTIP");
local estTimeElapsedToolStr			:string = Locale.Lookup("LOC_KEY_ESTIMATED_TIME_ELAPSED_TOOLTIP");
local canUnreadyTurnTip				:string = Locale.Lookup("LOC_ACTION_PANEL_CAN_UNREADY_TOOLTIP");
													  
-- ===========================================================================
g_kMessageInfo = {};
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_UNITS]						= {Message = unitNeedsOrdersString,			ToolTip = unitNeedsOrdersTip	, Icon="ICON_NOTIFICATION_COMMAND_UNITS"		}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_STACKED_UNITS]				= {Message = moveStackedUnitString,			ToolTip = moveStackedUnitTip	, Icon="ICON_NOTIFICATION_COMMAND_UNITS"		}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_UNIT_NEEDS_ORDERS]			= {Message = unitNeedsOrdersString,			ToolTip = unitNeedsOrdersTip	, Icon="ICON_NOTIFICATION_COMMAND_UNITS"		}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_RESEARCH]					= {Message = needResearchString,			ToolTip = needResearchTip		, Icon="ICON_NOTIFICATION_CHOOSE_TECH"		}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_CIVIC]						= {Message = needCivicString,				ToolTip = needCivicTip			, Icon="ICON_NOTIFICATION_CHOOSE_CIVIC",	Sound="Notification_New_Civic" }
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_FILL_CIVIC_SLOT]			= {Message = fillCivicString ,				ToolTip = fillCivicTip			, Icon="ICON_NOTIFICATION_CHOOSE_CIVIC"		}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_CONSIDER_GOVERNMENT_CHANGE]= {Message = considerGovernmentString,		ToolTip = considerGovernmentTip	, Icon="ICON_NOTIFICATION_CONSIDER_GOVERNMENT_CHANGE"	}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_CONSIDER_RAZE_CITY]		= {Message = considerRazeCityString,		ToolTip = considerRazeCityTip	, Icon="ICON_NOTIFICATION_CONSIDER_RAZE_CITY"	}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_PRODUCTION]				= {Message = needProductionString,			ToolTip = needProductionTip		, Icon="ICON_NOTIFICATION_CHOOSE_CITY_PRODUCTION"	}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_PANTHEON]					= {Message = needPantheonString,			ToolTip = needPantheonTip		, Icon="ICON_NOTIFICATION_CHOOSE_PANTHEON",	Sound="Notification_New_Religion" }
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_RELIGION]					= {Message = needReligionString,			ToolTip = needReligionTip		, Icon="ICON_NOTIFICATION_CHOOSE_RELIGION",	Sound="Notification_New_Religion" }
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_BELIEF]					= {Message = needBeliefString,				ToolTip = needBeliefTip			, Icon="ICON_NOTIFICATION_CHOOSE_RELIGION",	Sound="Notification_New_Religion" }
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_GIVE_INFLUENCE_TOKEN]		= {Message = giveInfluenceTokenString,		ToolTip = giveInfluenceTokenTip	, Icon="ICON_NOTIFICATION_GIVE_INFLUENCE_TOKEN"	}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_CLAIM_GREAT_PERSON]		= {Message = claimGreatPersonString,		ToolTip = claimGreatPersonTip	, Icon="ICON_NOTIFICATION_CLAIM_GREAT_PERSON",	Sound="Notification_Great_Person_Available" }
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_SPY_CHOOSE_ESCAPE_ROUTE]	= {Message = chooseEscapeRouteString,		ToolTip = chooseEscapeRouteTip	, Icon="ICON_NOTIFICATION_SPY_CHOOSE_ESCAPE_ROUTE"	}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_SPY_CHOOSE_DRAGNET_PRIORITY]={Message = chooseDragnetPriorityString,	ToolTip = chooseDragnetPriorityTip	, Icon="ICON_NOTIFICATION_SPY_CHOOSE_DRAGNET_PRIORITY"}
g_kMessageInfo[EndTurnBlockingTypes.ENDTURN_BLOCKING_ARTIFACT]                   ={Message = needArtifactPlayerString,		ToolTip = needArtifactPlayerTip	, Icon="ICON_NOTIFICATION_DISCOVER_ARTIFACT"}

g_kEras	= {};

-- ===========================================================================
--	MEMBERS
-- ===========================================================================
local m_overflowIM			: table = InstanceManager:new( "TurnBlockerInstance",  "TurnBlockerButton", Controls.OverflowStack );
local m_activeBlockerId		: number	= EndTurnBlockingTypes.NO_ENDTURN_BLOCKING;	-- Blocking notification receiving attention
local m_kSoundsPlayed		: table		= {};										-- Track which notifications have had their associate sound played
local m_EndTurnId			: number	= Input.GetActionId("EndTurn");				-- Hotkey
local m_lastTurnTickTime	: number	= 0;										-- When did we last make a tick sound for the turn timer?
local m_numberVisibleBlockers	:number	= 0;
local m_visibleBlockerTypes	: table		= {};
local m_isSlowTurnEnable	: boolean	= false;									-- Tutorial: when active slow to allow clicks when turn raises.
local m_unreadiedTurn		: boolean   = false;									-- Did the local player unready their turn during the current game turn?
local m_cloudTurnState		: number	= CloudTurnStates.CLOUDTURN_NONE;			-- State of PlayByCloud turn upload process.
local m_kPopupDialog		: table		= {};
local m_rememberCloudChoice : boolean	= false;
local m_isProdQueueOpen		: boolean	= false;

-- ===========================================================================
--	UI Event
--	The View()
-- ===========================================================================
function OnRefresh()

	ContextPtr:ClearRequestRefresh();
	
	m_numberVisibleBlockers = 1; -- Start at 1 to account for current main blocker
	m_visibleBlockerTypes = {};

	local pPlayer : object = Players[Game.GetLocalPlayer()];
	if (pPlayer == nil or not pPlayer:IsAlive()) then
		return;
	end

	if not pPlayer:IsTurnActiveComplete() or UI.IsProcessingMessages() then
		SetEndTurnWaiting();			
		return;
	end
	
	Controls.EndTurnButton:SetDisabled( false );
	Controls.EndTurnButtonLabel:SetDisabled( false );	
	
	local message				:string;
	local icon					:string;
	local toolTipString			:string;
	local soundName				:string;
	local iFlashingState		:number	= NO_FLASHING;	
	local m_activeBlockerId		:number = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
	local kAllBlockingTypes		:table	= NotificationManager.GetAllEndTurnBlocking( Game.GetLocalPlayer() );

	-- If there are any blockers shown, there will be at least 1
	table.insert(m_visibleBlockerTypes, m_activeBlockerId);

	-- Loop through all sounds that have just played.
	for _,blockingTypeSoundPlayed in ipairs(m_kSoundsPlayed) do 				
		-- If the blocking type is no longer in the block list
		local isStillInList:boolean = false;
		for _,blockingType in ipairs(kAllBlockingTypes) do
			if blockingType == blockingTypeSoundPlayed then
				isStillInList = true;
				break;
			end
		end
		-- If not found in list, remove it from the just played list.
		if not isStillInList then
			m_kSoundsPlayed[blockingTypeSoundPlayed] = nil;
		end
	end

	-- Play the ticker animation
	Controls.TickerAnim:SetToBeginning();
	Controls.TickerAnim:Play();

	-- Populate current blocker
	local kInfo	:table	= g_kMessageInfo[m_activeBlockerId];
	if kInfo ~= nil then
		message			= kInfo.Message;
		icon			= kInfo.Icon;
		toolTipString	= kInfo.ToolTip;
		iFlashingState	= FLASHING_END_TURN;
		soundName		= kInfo.Sound;
	elseif (CheckUnitsHaveMovesState()) then
		-- Special "Units Have Moves" state for when there are no end turn blockers but 
		-- there are units with partial movement remaining in 'auto end turn mode'.
		icon			= "ICON_NOTIFICATION_COMMAND_UNITS"
		message			= unitsHaveMovesString;
		toolTipString	= unitsHaveMovesTip;
		iFlashingState	= FLASHING_END_TURN;	
	elseif (CheckCityRangeAttackState()) then
		-- Special "City Ranged Attack" state for when there are no end turn blockers but 
		-- there is a city can that perform a ranged attack in 'auto end turn mode'.
		message			= cityRangedAttackString;
		icon            = "ICON_NOTIFICATION_CITY_RANGE_ATTACK";
		toolTipString	= cityRangedAttackTip;
		iFlashingState	= FLASHING_END_TURN;
	else
		message			= nextTurnString;	
		icon			= "ICON_NOTIFICATION_NEXT_TURN";		
		toolTipString	= nextTurnTip;
		iFlashingState	= FLASHING_END_TURN;
	end	

	-- Show controls and setup callbacks based on the notifications.

	local blockersInUIMax	:number = math.min( table.count(kAllBlockingTypes), MAX_BLOCKER_BUTTONS);
	local iControlNum		:number = 2;
	local iBlocker			:number = 0;
	for iBlocker = 1, blockersInUIMax, 1 do
		local endTurnBlockingId:number = kAllBlockingTypes[iBlocker];
		-- We only want to add blocker buttons for blockers that aren't represented already
		if  endTurnBlockingId ~= m_activeBlockerId and (not BlockerIsVisible(endTurnBlockingId)) then			
			local kAlphaControl:table = Controls["TurnBlockerAlpha"..tostring(iControlNum)];
			local kSlideControl:table = Controls["TurnBlockerSlide"..tostring(iControlNum)];
			local kButtonControl:table= Controls["TurnBlockerButton"..tostring(iControlNum)];

			if kAlphaControl:IsHidden() then
				kAlphaControl:SetHide(false);		
				kAlphaControl:SetToBeginning();
				kSlideControl:SetToBeginning();
				kAlphaControl:Play();
				kSlideControl:Play();
			end
			if g_kMessageInfo[endTurnBlockingId] then
				local tooltip:string = g_kMessageInfo[endTurnBlockingId].ToolTip;
				local icon:string	= g_kMessageInfo[endTurnBlockingId].Icon;
				if(icon ~= nil) then
					local textureOffsetX, textureOffsetY, textureSheet = IconManager:FindIconAtlas(icon,40);
					kButtonControl:SetTexture( textureOffsetX, textureOffsetY, textureSheet );
				end
				kButtonControl:SetToolTipString( tooltip );
				kButtonControl:RegisterCallback( Mouse.eLClick, 
					function()					
						DoEndTurn( endTurnBlockingId );
					end
				);
				iControlNum = iControlNum + 1;
				m_numberVisibleBlockers = m_numberVisibleBlockers + 1;
				table.insert(m_visibleBlockerTypes, endTurnBlockingId);
			else
				UI.DataError("Attempted to show turn blocking icon in ActionPanel but NIL in message info. id: "..tostring(endTurnBlockingId));
			end
		end		
	end

	-- Go through remaining controls (if any) and hide them if no longer showing.
	for iControlNum = iControlNum, MAX_BLOCKER_BUTTONS, 1 do
		local kAlphaControl:table = Controls["TurnBlockerAlpha"..tostring(iControlNum)];
		if not kAlphaControl:IsHidden() and not kAlphaControl:IsReversing() then
			local kSlideControl:table = Controls["TurnBlockerSlide"..tostring(iControlNum)];
			kAlphaControl:Reverse();
			kSlideControl:Reverse();
			kAlphaControl:Play();
			kSlideControl:Play();
		end
	end


	-- If there are more blockers than room, then add to "+" area:
	if m_numberVisibleBlockers > MAX_BLOCKER_BUTTONS then
		Controls.OverflowCheckboxGroup:SetHide(false);
		m_overflowIM:ResetInstances();
		for iBlocker = MAX_BLOCKER_BUTTONS+1, table.count(kAllBlockingTypes), 1 do
			-- We only want to add blocker buttons for blockers that aren't represented already
			local endTurnBlockingId	:number = kAllBlockingTypes[iBlocker];
			if not BlockerIsVisible(endTurnBlockingId) then
				local title				:string = g_kMessageInfo[endTurnBlockingId].Message;
				local kInst				:table  = m_overflowIM:GetInstance();			
				local tooltip			:string = g_kMessageInfo[endTurnBlockingId].ToolTip;
				local icon				:string = g_kMessageInfo[endTurnBlockingId].Icon;

				if(icon ~= nil) then
					local textureOffsetX, textureOffsetY, textureSheet = IconManager:FindIconAtlas(icon,40);
					kInst.TurnBlockerIcon:SetTexture( textureOffsetX, textureOffsetY, textureSheet );
				end

				kInst.TurnBlockerLabel:SetText( title );			
				kInst.TurnBlockerLabel:SetToolTipString( tooltip );
				kInst.TurnBlockerButton:RegisterCallback( Mouse.eLClick, 
					function()					
						DoEndTurn( endTurnBlockingId );
					end
				);
				table.insert(m_visibleBlockerTypes, endTurnBlockingId);
			end
		end
	else
		Controls.OverflowCheckboxGroup:SetHide(true);
	end

	-- Play associated sound if there is one (and it hasn't played yet; which can happen
	-- if a player chooses another action rather than the immediate blocking action.)
	if soundName ~= nil and soundName ~= "" then
		if m_kSoundsPlayed[m_activeBlockerId] == nil then
			UI.EnqueueNotificationSound( soundName );
			m_kSoundsPlayed[m_activeBlockerId] = true;
		end
	end

	TruncateStringWithTooltip(Controls.EndTurnText, MAX_BEFORE_TRUNC_TURN_STRING, message); 
	Controls.EndTurnButton:SetToolTipString( toolTipString );
	
	-- Set big icon
	if(icon ~= nil) then
		local countActiveType	:number = 0;
		Controls.CurrentTurnBlockerIcon:SetHide(false);
		Controls.CurrentTurnBlockerIcon:SetIcon(icon);
		
		countActiveType = GetNumNotificationsOfActiveBlocker();
		if  countActiveType >= 2 then
			Controls.Count:SetText(countActiveType);
			Controls.CountImage:SetHide(false);
		else
			Controls.CountImage:SetHide(true);
		end
	end

	SetEndTurnFlashing(iFlashingState);

	RealizeEraIndicator();
end


-- ===========================================================================
-- Set the era rotation and tooltip.
-- ===========================================================================
function RealizeEraIndicator()

	if HasCapability("CAPABILITY_ERAS")==false then
		Controls.EraIndicator:SetHide( true );
		return;
	end

	local displayEra :number = 1;	
	local pPlayer = Players[Game.GetLocalPlayer()];
	if pPlayer ~= nil then
		displayEra = pPlayer:GetEra() + 1;	-- Engine is 0 Based
	end	
	for _,kEra in pairs(g_kEras) do
		if kEra.Index == displayEra then
			local description:string = Locale.Lookup("LOC_GAME_ERA_DESC", kEra.Description );
			Controls.EraToolTipArea1:SetToolTipString( description );
			Controls.EraToolTipArea2:SetToolTipString( description );
			Controls.EraIndicator:Rotate( kEra.Degree + 90 );	-- 0 degree in art points "left"
			break;
		end		
	end
end


-- ===========================================================================
function SetEndTurnFlashing( iFlashingState:number )
	
	-- default behavior
	local isHideEndTurnFlash    :boolean = true;
	local isHideScienceFlash    :boolean = true;
	local isHideFreeTechFlash   :boolean = true;
	local isHideProductionFlash :boolean = true;
	local isHideNormalMouseover :boolean = false;
	
	-- set behavior based on flashing type
	if	   iFlashingState == FLASHING_END_TURN then		isHideEndTurnFlash = false;	isHideNormalMouseover = true;
	elseif iFlashingState == FLASHING_SCIENCE then		isHideScienceFlash = false;
	elseif iFlashingState == FLASHING_PRODUCTION then	isHideProductionFlash = false;
	elseif iFlashingState == FLASHING_FREE_TECH then	isHideFreeTechFlash = false;
	elseif iFlashingState == FLASHING_NEEDS_ORDERS then	isHideNormalMouseover = false;
	elseif iFlashingState == NO_FLASHING then	
		-- Stay with defaults if no flashing.
	end
	
	-- realize
	Controls.EndTurnButtonEndTurnAlpha:SetHide(isHideEndTurnFlash);
	Controls.EndTurnButtonScienceAlpha:SetHide(isHideScienceFlash);
	Controls.EndTurnButtonFreeTechAlpha:SetHide(isHideFreeTechFlash);
	Controls.EndTurnButtonProductionAlpha:SetHide(isHideProductionFlash);	
end

-- ===========================================================================
-- utility functions
function GetPlayer ()
	local iPlayerID = Game.GetLocalPlayer();
	if (iPlayerID < 0) then
		return nil;
	end

	if (not Players[iPlayerID]:IsHuman()) then
		return nil;
	end;

	return Players[iPlayerID];
end

-- ===========================================================================
function GetPlayerByID (iPlayerID)
	if (iPlayerID < 0) then
		return nil;
	end

	return Players[iPlayerID];
end

-- ===========================================================================
function UnitsHaveMovesStateEnabled()
	-- When is the "Units Have Moves" end turn button enabled?
	return 	(UserConfiguration.IsAutoEndTurn()) and Game.IsAllowTacticalCommands(Game.GetLocalPlayer());
end

-- ===========================================================================
function HaveCityRangeAttackStateEnabled()
	-- When is the "City Ranged Attack" end turn button enabled?
	return 	(UserConfiguration.IsCityRangeAttackTurnBlocking()) and Game.IsAllowTacticalCommands(Game.GetLocalPlayer());
end

-- ===========================================================================
function CheckUnitsHaveMovesState()
	-- Are we in the Units Have Moves state?
	local pPlayer = Players[Game.GetLocalPlayer()];
	if (pPlayer == nil) then
		return false;
	end

	local unitsNeedMovesState :boolean = UnitsHaveMovesStateEnabled() and pPlayer:GetUnits():GetFirstReadyUnit() ~= nil;
	return unitsNeedMovesState;
end

-- ===========================================================================
function CheckCityRangeAttackState()
	-- Are we in the "City Ranged Attack" state?
	local pPlayer = Players[Game.GetLocalPlayer()];
	if (pPlayer == nil) then
		return false;
	end

	if(not HaveCityRangeAttackStateEnabled()) then
		return false;
	end

	local pNotification :table = NotificationManager.FindType(NotificationTypes.CITY_RANGE_ATTACK, Game.GetLocalPlayer());
	if pNotification == nil or pNotification:IsDismissed() then
		return false;
	end

	return true;
end

-- ===========================================================================
--	Get the number notifications that are the same type as the currently active blocker
-- ===========================================================================
function GetNumNotificationsOfActiveBlocker()
	local count				:number = 0;
	local iBlocker			:number;
	local kAllBlockingTypes	:table = NotificationManager.GetAllEndTurnBlocking( Game.GetLocalPlayer() );
	local m_activeBlockerId	:number = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());

	for iBlocker = 1, table.count(kAllBlockingTypes), 1 do
		if (kAllBlockingTypes[iBlocker] == m_activeBlockerId) then
			count = count + 1;
		end
	end
	return count;
end

-- ===========================================================================
--	Used to make sure there aren't duplicate blocker notifications
-- ===========================================================================
function BlockerIsVisible(iBlocker:number)
	local currentType:number;

	for currentType=1, table.count(m_visibleBlockerTypes), 1 do
		if m_visibleBlockerTypes[currentType] == iBlocker then
			return true;
		end
	end

	return false;
end

-- ===========================================================================
--	Check if the turn can be automatically ended.
-- ===========================================================================
function CheckAutoEndTurn( eCurrentEndTurnBlockingType:number )
	local pPlayer = Players[Game.GetLocalPlayer()];
	if pPlayer ~= nil then
		if not m_unreadiedTurn -- If the player intentionally unreadied their turn, do not auto end turn.
			and eCurrentEndTurnBlockingType == EndTurnBlockingTypes.NO_ENDTURN_BLOCKING 
			and	(UserConfiguration.IsAutoEndTurn() and not UI.SkipNextAutoEndTurn())
			-- In tactical phases, all units must have orders or used up their movement points.
			and (not CheckUnitsHaveMovesState() and not CheckCityRangeAttackState()) 
			-- Not already send turn complete for this turn.
			and not UI.HasSentTurnComplete()
			-- Expansion content is ok with auto ending the turn.
			and AllowAutoEndTurn_Expansion() then 
				if not UI.CanEndTurn() then
					UI.DataError("CheckAutoEndTurn thinks that we can't end turn, but the notification system disagrees!");
				end
			UI.RequestAction(ActionTypes.ACTION_ENDTURN);
		end
	end
end

-- Overridable function for additional AutoEndTurn checks for expansion content.
-- Return true when the user should be able to auto end their turn based on additional expansion conditions.
function AllowAutoEndTurn_Expansion()
	return true;
end

-- ===========================================================================
--	Attempt to end the turn or execute the most current blocking notification
-- ===========================================================================
function DoEndTurn( optionalNewBlocker:number )

	local pPlayer = Players[Game.GetLocalPlayer()];
	if (pPlayer == nil) then
		return;
	end

	-- If the player can unready their turn, request that.
	-- CanUnreadyTurn() only checks the gamecore state. IsTurnTimerElapsed() is also required to ensure the local player still has turn time remaining.
	if pPlayer:CanUnreadyTurn()
		and not UI.IsTurnTimerElapsed(Game.GetLocalPlayer()) then
		UI.RequestAction(ActionTypes.ACTION_UNREADYTURN);	
		return;
	end

	if UI.IsProcessingMessages() then
		print("ActionPanel:DoEndTurn() The game is busy processing messages");
		return;
	end

	-- If not in selection mode; reset mode before performing the action.
	if UI.GetInterfaceMode() ~= InterfaceModeTypes.SELECTION then
		UI.SetInterfaceMode(InterfaceModeTypes.SELECTION);
	end


	-- Make sure if an active blocker is not set, to do one more check from the engine/authority.
	if optionalNewBlocker ~= nil then
		m_activeBlockerId = optionalNewBlocker;
	else
		m_activeBlockerId = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
	end
	
	if m_activeBlockerId == EndTurnBlockingTypes.NO_ENDTURN_BLOCKING then
		if (CheckUnitsHaveMovesState()) then
			UI.SelectNextReadyUnit();
		elseif(CheckCityRangeAttackState()) then
			local attackCity = pPlayer:GetCities():GetFirstRangedAttackCity();
			if(attackCity ~= nil) then
				UI.SelectCity(attackCity);
				UI.SetInterfaceMode(InterfaceModeTypes.CITY_RANGE_ATTACK);
			else
				UI.DataError( "Unable to find selectable attack city while in CheckCityRangeAttackState()" );
			end
		else
			UI.RequestAction(ActionTypes.ACTION_ENDTURN);		
			UI.PlaySound("Stop_Unit_Movement_Master");
		end
	
	elseif (   m_activeBlockerId == EndTurnBlockingTypes.ENDTURN_BLOCKING_STACKED_UNITS
			or m_activeBlockerId == EndTurnBlockingTypes.ENDTURN_BLOCKING_UNIT_NEEDS_ORDERS
			or m_activeBlockerId == EndTurnBlockingTypes.ENDTURN_BLOCKING_UNITS)	then

		UI.SelectNextReadyUnit();

	else		

		-- generic turn blocker, trigger the notification associated with the turn blocker.
		local pNotification :table = NotificationManager.FindEndTurnBlocking(m_activeBlockerId, Game.GetLocalPlayer());
		
		if pNotification == nil then
			-- Notification is missing.  Use fallback behavior.
			if not UI.CanEndTurn() then
				UI.DataError("The UI thinks that we can't end turn, but the notification system disagrees.");
				return;
			end				
			UI.RequestAction(ActionTypes.ACTION_ENDTURN);		
			return;
		end

		-- Raise the event across the UI which may be listening for this particular notification.
		LuaEvents.ActionPanel_ActivateNotification( pNotification );
	end

end

-- ===========================================================================
--	UI Callback
-- ===========================================================================
function OnEndTurnClicked()
	DoEndTurn();
end

-- ===========================================================================
--	ENGINE Event
-- ===========================================================================
function OnEndTurnBlockingChanged( ePrevEndTurnBlockingType:number, eNewEndTurnBlockingType:number )
	
	local pPlayer :table = Players[Game.GetLocalPlayer()];
	if pPlayer == nil then
		return;
	end
		
	if pPlayer:IsTurnActive()==false then
		return;
	end

	local blockingType:number  = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer()); 
	if (eNewEndTurnBlockingType ~= blockingType) then
		UI.DataError("ActionPanel received mismatched blocking types.  EventType: "..tostring(eNewEndTurnBlockingType)..", EngineType: "..tostring(blockingType));
		return;
	end

	-- If our production queue is open don't auto-cycle to the next turn blocking unit
	if m_isProdQueueOpen == true then
		return;
	end

	-- If in the midst of managing a city (plot purchase, citizen management, etc...) don't auto-cycle.
	local mode:number = UI.GetInterfaceMode();
	if (mode == InterfaceModeTypes.CITY_MANAGEMENT) then
		return;
	end

	CheckAutoEndTurn( blockingType );
			
	if ShouldUnitAutoSelect() then
		-- Obtain first unit with moves remaining (that isn't automated or about to die).			
		local pUnit:table = pPlayer:GetUnits():GetFirstReadyUnit();
		if pUnit ~= nil then
			UI.DeselectAllUnits();
			UI.DeselectAllCities();
			UI.SelectClosestReadyUnit();	-- This will select the closest ready unit to the last selected unit, or, if none, the first ready unit
		end		
	end
end
	

-- ===========================================================================
function ShouldUnitAutoSelect()
	-- If they have auto-unit-cycling off, then don't change the selection.
	if (not UserConfiguration.IsAutoUnitCycle()) then
		return false;
	end

	-- Just exit, the app side UI manager will cycle to the next unit if it is ready to do so.
	local pSelectedUnit:table = UI.GetHeadSelectedUnit();
	if (pSelectedUnit ~= nil) then				
		return false;	
	end

	-- If this was signaled from a plot purchase, due to a (building or
	-- district) placement, do not select a unit, stick to the city.
	local pSelectedCity:table = UI.GetHeadSelectedCity();
	if (pSelectedCity ~= nil) then 
		local eMode:number = UI.GetInterfaceMode();
		if eMode == InterfaceModeTypes.BUILDING_PLACEMENT then return false; end
		if eMode == InterfaceModeTypes.DISTRICT_PLACEMENT then return false; end
	end
	return true;
end


-- ===========================================================================
--	RIGHT CLICK
-- ===========================================================================
function OnEndTurnRightClicked()
	local pPlayer = Players[Game.GetLocalPlayer()];
	if (pPlayer == nil) then
		return;
	end;

	if not pPlayer:IsTurnActive() then
		print("Player's turn not active");
		return;
	end

	local activeBlockerId = NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
	if activeBlockerId == EndTurnBlockingTypes.NO_ENDTURN_BLOCKING then
		if (CheckUnitsHaveMovesState()) then
			-- Do Nothing
		elseif(CheckCityRangeAttackState()) then
			-- Remove the city range attack notification so the turn can proceed.
			local pNotification :table = NotificationManager.FindType(NotificationTypes.CITY_RANGE_ATTACK, Game.GetLocalPlayer());
			if pNotification ~= nil and not pNotification:IsDismissed() then
				NotificationManager.Dismiss( pNotification:GetPlayerID(), pNotification:GetID() );
			end
		else
			-- Do Nothing
		end
	end
end

-- ===========================================================================
function OnOverflowClick()
	Controls.OverflowContainer:SetSizeY( Controls.OverflowStack:GetSizeY() + 22 );
	if(Controls.OverflowCheckbox:IsChecked()) then
		Controls.EndTurnButtonLabel:SetHide(true);
		Controls.TurnBlockerContainerAlpha:SetHide(false);
		Controls.TurnBlockerContainerAlpha:SetToBeginning();
		Controls.TurnBlockerContainerSlide:SetToBeginning();
		Controls.TurnBlockerContainerAlpha:Play();
		Controls.TurnBlockerContainerSlide:Play();
	else
		Controls.EndTurnButtonLabel:SetHide(false);
		Controls.TurnBlockerContainerAlpha:Reverse();
		Controls.TurnBlockerContainerSlide:Reverse();
	end
end

function HideOverflowContainer()
	if (Controls.TurnBlockerContainerAlpha:IsReversing()) then 
		Controls.TurnBlockerContainerAlpha:SetHide(true);
	end
end
-- ===========================================================================
function SetEndTurnWaiting()
	-- The local player is waiting for their next turn.  Set the button state based on conditions.
	-- localized tooltip string for end turn button
	local endButtonTooltip : string = waitForPlayersTip; 
	local turnActiveHumanName : string = nil; -- player name of a human player who is turn active.
	local playersWaiting : number = 0;
	local iActivePlayer = Game.GetLocalPlayer();

	if(m_cloudTurnState == CloudTurnStates.CLOUDTURN_UPLOADING) then
		Controls.EndTurnText:SetText( cloudTurnUploadingString );
		Controls.EndTurnButton:SetToolTipString( cloudTurnUploadingTip );
		SetEndTurnFlashing(NO_FLASHING);
		return;
	-- Show "EXITING" when the cloud turn has been updated if we are going to exit to the main menu.
	elseif(m_cloudTurnState == CloudTurnStates.CLOUDTURN_UPLOADED
		and UserConfiguration.GetPlayByCloudEndTurnBehavior() == PlayByCloudEndTurnBehaviorType.PBC_ENDTURN_EXIT_MAINMENU) then

		-- [TTP 42975] Only show if there is another alive human in the match.
		local players = Game.GetPlayers{Human = true, Major = true};
		for _, player in ipairs(players) do
			local iPlayer = player:GetID();
			if(iPlayer ~= iActivePlayer and player:IsAlive()) then
				Controls.EndTurnText:SetText( cloudTurnUploadedString );
				Controls.EndTurnButton:SetToolTipString( cloudTurnUploadedTip );
				SetEndTurnFlashing(NO_FLASHING);
				return;
			end
		end
	end
		
	local players = Game.GetPlayers{Human = true, Major = true};
	for _, player in ipairs(players) do
		local iPlayer = player:GetID();
		if(iPlayer ~= iActivePlayer and player:IsTurnActive()) then
			local pPlayer:table = Players[iPlayer];
			local pPlayerConfig = PlayerConfigurations[iPlayer];
			if(pPlayerConfig ~= nil) then
				local playerName = Locale.Lookup(pPlayerConfig:GetPlayerName());

				if GameConfiguration.IsAnyMultiplayer() and pPlayer:IsHuman() then
					if(iPlayer ~= iActivePlayer and not Players[iActivePlayer]:GetDiplomacy():HasMet(iPlayer)) then
						endButtonTooltip = endButtonTooltip .. "[NEWLINE]" .. Locale.Lookup("LOC_DIPLOPANEL_UNMET_PLAYER") .. " (" .. playerName .. ")";
					else
						endButtonTooltip = endButtonTooltip .. "[NEWLINE]" .. Locale.Lookup(pPlayerConfig:GetCivilizationDescription()) .. " (" .. playerName .. ")";
					end
				else
					endButtonTooltip = endButtonTooltip .. "[NEWLINE]" .. "(" .. playerName .. ") ";
				end

				playersWaiting = playersWaiting + 1;

				-- Remember the name of the first turn active human we find so we can display it on
				-- the end turn button.
				if(turnActiveHumanName == nil) then
					turnActiveHumanName = playerName;
				end
			end
		end
	end	

	-- If players can unready their turn, indicate that in the tooltip. 
	local pLocalPlayer = Players[Game.GetLocalPlayer()];
	if (pLocalPlayer ~= nil and pLocalPlayer:CanUnreadyTurn()) then
		endButtonTooltip = endButtonTooltip .. "[NEWLINE]" .. canUnreadyTurnTip;
	end
		
	Controls.CurrentTurnBlockerIcon:SetHide(true);
	if(playersWaiting == 0) then
		-- Not waiting on other human players.  Just show "Please Wait".
		Controls.EndTurnText:LocalizeAndSetText( pleaseWaitString );
		endButtonTooltip = pleaseWaitTip;
	else
		-- Waiting on human players. 
		if(turnActiveHumanName ~= nil) then
			local textToSet : string = Locale.Lookup(waitForPlayerTurnString, string.upper(turnActiveHumanName));
			TruncateStringWithTooltip(Controls.EndTurnText, MAX_BEFORE_TRUNC_TURN_STRING, textToSet);
		else
			-- couldn't find the name of the player we're waiting on, use generic message
			Controls.EndTurnText:LocalizeAndSetText(waitForPlayersString);
		end
	end
	Controls.EndTurnButton:SetToolTipString( endButtonTooltip );
	
	SetEndTurnFlashing(NO_FLASHING);
end

-- ===========================================================================
function OnUnitOperationSegmentComplete( player:number, unitID:number, hCommand, iData1)
	-- When using "Units Have Moves" state, having a unit complete a unit operation segment 
	-- can affect your end turn state and auto end turns.
	if UnitsHaveMovesStateEnabled() and player == Game.GetLocalPlayer() then
		local pPlayer		:table = Players[Game.GetLocalPlayer()];
		local blockingType	:number= NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
		
		CheckAutoEndTurn( blockingType );
		ContextPtr:RequestRefresh();
	end
end

-- ===========================================================================
function OnUnitOperationsCleared( player:number, unitID:number, hCommand, iData1)
	-- When using "Units Have Moves" state, having a unit complete all their unit operations 
	-- can affect your end turn state and auto end turns.
	if UnitsHaveMovesStateEnabled() and player == Game.GetLocalPlayer() then
		local pPlayer		:table = Players[Game.GetLocalPlayer()];
		local blockingType	:number= NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
		CheckAutoEndTurn( blockingType );
		ContextPtr:RequestRefresh();
	end
end

-- ===========================================================================
function OnCityCommandStarted( cityOwnerID: number, cityID :number, districtOwnerID :number, districtID :number, commandType :number, iData1 :number )
	-- When the local player starts a city command (ranged attack), that might end the turn for them.
	if(cityOwnerID == Game.GetLocalPlayer() and HaveCityRangeAttackStateEnabled()) then
		local blockingType	:number= NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
		CheckAutoEndTurn( blockingType );
	end
end

-- ===========================================================================
function OnUserOptionChanged(eOptionSet, hOptionKey, iNewOptionValue)
	-- If we enable certain user options, we need to check auto end turns because our auto end turn status might be affected.
	if(hOptionKey == autoEndTurnOptionHash or hOptionKey == cityRangeAttackTurnOptionHash) then
		if(UserConfiguration.IsAutoEndTurn()) then
			local blockingType	:number= NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
			CheckAutoEndTurn( blockingType );
		end
		-- Changing these user options can result in a different end turn state.
		ContextPtr:RequestRefresh();
	end
end

-- ===========================================================================
function OnUploadCloudEndTurnStart()
	if(m_cloudTurnState ~= CloudTurnStates.CLOUDTURN_UPLOADING) then
		m_cloudTurnState = CloudTurnStates.CLOUDTURN_UPLOADING;
		if(not ContextPtr:IsHidden()) then
			ContextPtr:RequestRefresh();
		end
	end
end

-- ===========================================================================
function OnUploadCloudEndTurnComplete()
	if(m_cloudTurnState ~= CloudTurnStates.CLOUDTURN_UPLOADED) then
		m_cloudTurnState = CloudTurnStates.CLOUDTURN_UPLOADED;
		if(not ContextPtr:IsHidden()) then
			ContextPtr:RequestRefresh();
			if(UserConfiguration.GetPlayByCloudEndTurnBehavior() == PlayByCloudEndTurnBehaviorType.PBC_ENDTURN_ASK_ME) then
				if(Game.GetLocalPlayer() == NO_PLAYER) then
					-- No local player.
					return;
				end
				
				local pLocalPlayer		:table = Players[Game.GetLocalPlayer()];
				if(pLocalPlayer == nil) then
					return;
				end
				
				if(pLocalPlayer:IsTurnActive()) then
					-- Local player is already turn active again.  This happens if the local player is the solo remaining human player.
					-- We should simply not show the Ask Me popup in this case.
					return;
				end

				m_rememberCloudChoice = false;
				m_kPopupDialog:Close();
				m_kPopupDialog:AddTitle( Locale.Lookup("LOC_ACTION_PANEL_END_TURN_ASK_ME_TITLE") );
				m_kPopupDialog:AddText( Locale.Lookup("LOC_ACTION_PANEL_END_TURN_ASK_ME_TEXT"))
				m_kPopupDialog:AddCheckBox(Locale.Lookup("LOC_REMEMBER_MY_CHOICE"), false, OnRememberChoice);
				m_kPopupDialog:AddButton( Locale.Lookup("LOC_OPTIONS_PLAYBYCLOUD_END_TURN_BEHAVIOR_DO_NOTHING"), OnChoiceDoNothing );
				m_kPopupDialog:AddButton( Locale.Lookup("LOC_OPTIONS_PLAYBYCLOUD_END_TURN_BEHAVIOR_EXIT_TO_MAINMENU"), OnChoiceExitToMainMenu );
				m_kPopupDialog:Open();
			end
		end
	end
end

function OnRememberChoice(checked : boolean)
	m_rememberCloudChoice = checked;
end

function OnChoiceDoNothing()
	if(m_rememberCloudChoice == true) then
		Options.SetUserOption("Interface", "PlayByCloudEndTurnBehavior", PlayByCloudEndTurnBehaviorType.PBC_ENDTURN_DO_NOTHING);
		Options.SaveOptions();
	end	
end

function OnChoiceExitToMainMenu()
	if(m_rememberCloudChoice == true) then
		Options.SetUserOption("Interface", "PlayByCloudEndTurnBehavior", PlayByCloudEndTurnBehaviorType.PBC_ENDTURN_EXIT_MAINMENU);
		Options.SaveOptions();
	end

	Events.ExitToMainMenu();
end

-- ===========================================================================
function OnLocalPlayerTurnBegin()
	-- If the player is dead (observing), then automatically end their turn
	local pPlayerConfig :table	= PlayerConfigurations[Game.GetLocalPlayer()];
	if(not pPlayerConfig:IsAlive())then
		DoEndTurn();
	else
		-- Standard disable is set to false in the refresh.
		-- This extra level of input catching is done when tutorial has raised
		-- this boolean and will prevent spam clicking through; as the tutorial
		-- system itself sets ENABLED as it's hiding all controls.
		if m_isSlowTurnEnable then
			Controls.TutorialSlowTurnEnableAnim:SetHide(false);
			Controls.TutorialSlowTurnEnableAnim:SetToBeginning();
			Controls.TutorialSlowTurnEnableAnim:RegisterEndCallback(
				function()
					Controls.TutorialSlowTurnEnableAnim:SetHide(true);
				end
			);
			Controls.TutorialSlowTurnEnableAnim:Play();
		end

		ContextPtr:RequestRefresh();

		-- if auto-cycle is OFF, play this sound to indicate "start of turn"
		if (not UserConfiguration.IsAutoUnitCycle()) then
			UI.PlaySound("SP_Turn_Start");
		end
	end
end

-- ===========================================================================
function OnLocalPlayerTurnEnd()
	local pPlayerConfig :table	= PlayerConfigurations[Game.GetLocalPlayer()];
	if(pPlayerConfig:IsAlive())then
		-- Only disable if not in multi-player, so turns can "unend"...
		if not GameConfiguration.IsAnyMultiplayer() then
			Controls.EndTurnButton:SetDisabled(true);
			Controls.EndTurnButtonLabel:SetDisabled(true);
		end

		SetEndTurnWaiting();
		UI.SetInterfaceMode(InterfaceModeTypes.SELECTION);
		m_kSoundsPlayed = {};
	end
end

-- ===========================================================================
function OnLocalPlayerTurnUnready()
	m_unreadiedTurn = true;
end

-- ===========================================================================
function OnRemotePlayerTurnEnd()
	-- Refresh as the "Waiting for " player might have changed.
	ContextPtr:RequestRefresh();
end

-- ===========================================================================
function OnLocalPlayerChanged( iLocalPlayer:number , iPrevLocalPlayer:number )
	ContextPtr:RequestRefresh();
end

-- ===========================================================================
--	GAME Event
-- ===========================================================================
function OnCityProductionChanged( ePlayer:number, cityID:number )
	if ePlayer == Game.GetLocalPlayer() then
		ContextPtr:RequestRefresh();
	end
end

-- ===========================================================================
--	GAME Event
-- ===========================================================================
function OnEndTurnDirty()
	ContextPtr:RequestRefresh();
end

-- ===========================================================================
--	GAME Event
-- ===========================================================================
function OnNotificationAdded( playerID:number, notificationID:number )
	if playerID == Game.GetLocalPlayer() then
		local pNotification:table = NotificationManager.Find( playerID, notificationID );
		if pNotification == nil then
			-- It is possible, that by the time we get this event, the notification was 'expired' by some other action in the game.
			-- UI.DataError( "Unable to find player ("..tostring(playerID).." notification ("..tostring(notificationID)..")" );
		end
	end
end

-- ===========================================================================
--	GAME Event
-- ===========================================================================
function OnNotificationDismissed( playerID:number, notificationID:number )
	if playerID == Game.GetLocalPlayer() then
		ContextPtr:RequestRefresh();
		
		-- Need to check auto end turn if this was a NotificationTypes.CITY_RANGE_ATTACK
		local wasCityRangeNotification = false;
		local pNotification:table = NotificationManager.Find( playerID, notificationID );
		if pNotification == nil then
			-- It is possible, that by the time we get this event, the notification was 'expired' by some other action in the game.
			-- To be safe, assume it was a NotificationTypes.CITY_RANGE_ATTACK.
			wasCityRangeNotification = true;
		elseif(pNotification:GetType() == NotificationTypes.CITY_RANGE_ATTACK) then
			wasCityRangeNotification = true;
		end

		if (wasCityRangeNotification and HaveCityRangeAttackStateEnabled()) then
			local pPlayer		:table = Players[Game.GetLocalPlayer()];
			local blockingType	:number= NotificationManager.GetFirstEndTurnBlocking(Game.GetLocalPlayer());
			CheckAutoEndTurn( blockingType );
		end		
	end
end

-- ===========================================================================
--	Game Event
--	Player just picked a research
-- ===========================================================================
function OnResearchChanged( ePlayer:number, eTech:number )	
	if ePlayer == Game.GetLocalPlayer() then
		ContextPtr:RequestRefresh();
	end
end

-- ===========================================================================
--	Game Engine Event
-- ===========================================================================
function OnInterfaceModeChanged(eOldMode:number, eNewMode:number)
	if eNewMode == InterfaceModeTypes.VIEW_MODAL_LENS then
		ContextPtr:SetHide(true);
	end
	if eOldMode == InterfaceModeTypes.VIEW_MODAL_LENS then
		ContextPtr:SetHide(false);
	end
end

-- ===========================================================================
--	Game Event
--	Game Turn Began
-- ===========================================================================
function OnTurnBegin()
	m_unreadiedTurn = false;
end

-- ===========================================================================
--	UI Event
-- ===========================================================================
function OnInit( isReload:boolean )
	LateInitialize();
	if isReload then	
		NotificationManager.RestoreVisualState(Game.GetLocalPlayer());	-- Restore the notifications
	end
	ContextPtr:RequestRefresh();
end

-- ===========================================================================
--	UI Event
-- ===========================================================================
function OnInputHandler( pInputStruct:table )
	local uiMsg:number = pInputStruct:GetMessageType();
	if uiMsg == KeyEvents.KeyUp then 
		if pInputStruct:GetKey() == Keys.VK_RETURN then
			if pInputStruct:IsShiftDown() and not IsTutorialRunning() then
				-- Forcing a turn via SHIFT + ENTER.  Unsupported.
				UI.RequestAction(ActionTypes.ACTION_ENDTURN, { REASON = "UserForced" } );
			else				
				DoEndTurn();									-- Enter = Normal End Turn
			end
			return true;
		end
	end
	return false;
end


-- ===========================================================================
--	LUA Event
--	When autoplay first starts; kicked off from the Tuner.
-- ===========================================================================
function OnAutoPlayStart()
	Controls.EndTurnText:SetText( Locale.Lookup("LOC_ACTION_PANEL_AUTOPLAY_ACTIVE") );
	Controls.EndTurnButton:SetToolTipString( Locale.Lookup("LOC_ACTION_PANEL_AUTOPLAY_ACTIVE_TOOLTIP") );
end

-- ===========================================================================
--	LUA Event
--	When autoplay completes.
-- ===========================================================================
function OnAutoPlayEnd()
	ContextPtr:RequestRefresh();
end

-- ===========================================================================
--	LUA Event
--	An additional input shield to prevent click-spamming which, can 
--	potentially skip to the next item before the tutorial manager has sent
--	the event to it's handler.
-- ===========================================================================
function OnTutorialSlowTurnEnable( isEnabled:boolean )
	if isEnabled == nil then
		isEnabled = true;
	end
	m_isSlowTurnEnable = isEnabled;
end



-- ===========================================================================
--	Setup and allocate any User Interfaces.
-- ===========================================================================
function AllocateUI()
	-- When an animation finishes playing in reverse; hide it (and it's children)
	function OnAnimEnd( kControl:table ) 
		if kControl:IsReversing() then
			kControl:SetHide( true );
		end
	end
	Controls.TurnBlockerAlpha4:RegisterEndCallback( OnAnimEnd );
	Controls.TurnBlockerAlpha3:RegisterEndCallback( OnAnimEnd );
	Controls.TurnBlockerAlpha2:RegisterEndCallback( OnAnimEnd );	
end


-- ===========================================================================
--	Create a hash table of EraType to its chronological index.
-- ===========================================================================
function PopulateEraData()
	g_kEras = {};
	for row:table in GameInfo.Eras() do
		g_kEras[row.EraType] = { 
			Description	= Locale.Lookup(row.Name),
			Index		= row.ChronologyIndex,
		}
	end

	local degreeStart	:number = 14;
	local degreeEnd		:number = 115;

	-- Draw PIPs for the number of eras.
	local max	:number = table.count(g_kEras);

	for _,kEra in pairs(g_kEras) do
		local uiControl :table = {};
		ContextPtr:BuildInstanceForControl( "EraPipInstance", uiControl, Controls.EraContainer );
		if kEra.Index == 1 then
			uiControl.PipImage:SetTexture("ActionPanel_EraPipStart");
		elseif kEra.Index == max then
			uiControl.PipImage:SetTexture("ActionPanel_EraPipEnd");
		end		
		local halfWidth	:number = uiControl.PipImage:GetSizeX()/2;
		local halfHeight:number = uiControl.PipImage:GetSizeY()/2;		
		local degree	:number = degreeStart + ((kEra.Index/max)*(degreeEnd-degreeStart));
		degree = degree - 90;		

		local x,y = PolarToCartesian(79, degree);
		x = (x + 80) - halfWidth;
		y = (y + 80) - halfHeight;

		uiControl.PipImage:SetOffsetVal(x,y);

		-- Cache the degree associated with the era for the indicator.
		-- Slightly less than 90 to account for art offset.
		kEra["Degree"] = degree+88;		
	end

	-- Reparent to ensure draw is on top of pips.
	Controls.EraIndicator:ChangeParent(Controls.EraContainer);	
end

-- ===========================================================================
--	Update turn timer meter
-- ===========================================================================
function OnTurnTimerUpdated(elapsedTime :number, maxTurnTime :number)
	if(maxTurnTime <= 0) then
		-- We're in a state where there isn't a turn time, hide all the turn timer elements.
		Controls.TurnTimerContainer:SetHide(true);
	else
		local localPlayerID:number;
		if GameConfiguration.IsHotseat() then
			localPlayerID = Game.GetLocalPlayer();
		else
			localPlayerID = Network.GetLocalPlayerID();
			if (localPlayerID == -1) then
				localPlayerID = Game.GetLocalPlayer();
			end
		end

		-- Make sure we have a valid local player.  The timer may have fired as the game was exiting.
		if (localPlayerID == -1) then
			return;
		end

		local pPlayer = Players[localPlayerID];

		Controls.TurnTimerContainer:SetHide(false);

		-- Update turn timer bar progress
		local progress : number = 0;
		if(elapsedTime < maxTurnTime) then
			progress = 1 - (elapsedTime/maxTurnTime);
		end
		Controls.TurnTimerMeter:SetPercent(progress);

		local timeRemaining : number = maxTurnTime - elapsedTime;

		-- Update turn timer bar color
		if(pPlayer:IsTurnActive()) then
			Controls.TurnTimerMeter:SetColor(TURN_TIMER_BAR_ACTIVE_COLOR);
			Controls.TurnTimerLabelBG:SetToolTipString(yourTurnToolStr);
		else
			Controls.TurnTimerMeter:SetColor(TURN_TIMER_BAR_INACTIVE_COLOR);
			if(timeRemaining > 0) then
				Controls.TurnTimerLabelBG:SetToolTipString(estTilTurnToolStr);
			else
				Controls.TurnTimerLabelBG:SetToolTipString(estTimeElapsedToolStr);
			end
		end

		-- Update turn timer label 
		if(timeRemaining > 0) then
			-- Update countdown tick sound.
			-- Round the remaining time so the audio syncs up with the numerial countdown.
			local roundedTime = SoftRound(timeRemaining); 
			if( roundedTime <= START_TURN_TIMER_TICK_SOUND) then
				if(roundedTime > m_lastTurnTickTime -- last tick was for previous countdown
					or roundedTime <= (m_lastTurnTickTime-1)) then -- last tick was more than a 1 second ago.
					m_lastTurnTickTime = roundedTime;
					UI.PlaySound("Play_MP_Game_Launch_Timer_Beep");
				end
			end
			Controls.TurnTimerLabel:SetText(FormatTimeRemaining(timeRemaining, pPlayer:IsTurnActive()));
		else
			Controls.TurnTimerLabel:LocalizeAndSetText("-");
		end
	end
end

-- ===========================================================================
function OnIsProdQueueOpen( isQueueOpen:boolean )
	m_isProdQueueOpen = isQueueOpen;
end

-- ===========================================================================
function ChangePleaseWaitTooltip(newTooltip:string)
	pleaseWaitTip = Locale.Lookup(newTooltip);
end

-- ===========================================================================
function OnStartObserverMode()
	ChangePleaseWaitTooltip(Locale.Lookup("LOC_ACTION_PANEL_END_OBSERVER_MODE"));
	Controls.EndTurnButton:SetToolTipString(Locale.Lookup("LOC_ACTION_PANEL_END_OBSERVER_MODE"));
	Controls.ObserverButtonLabel:SetHide(false);
	Controls.EndObserverModeButton:SetHide(false);
	DoEndTurn();
end

-- ===========================================================================
--	Input Hotkey Event
-- ===========================================================================
function OnInputActionTriggered( actionId )
	if m_EndTurnId ~= nil and actionId == m_EndTurnId then
        UI.PlaySound("Play_UI_Click");
		DoEndTurn();
	end
end

-- ===========================================================================
function LateInitialize()
	AllocateUI();

	-- Only init the rotating era pointer if this game mode supports eras.
	if HasCapability("CAPABILITY_ERAS") then
		PopulateEraData();
	end

	-- It is possible to start with automation already active, test for that
	if Automation.IsActive() then
		OnAutoPlayStart();
	end

	-- UI Events
	Controls.EndTurnButton:RegisterCallback(		Mouse.eLClick, OnEndTurnClicked );
	Controls.EndTurnButton:RegisterCallback(		Mouse.eRClick, OnEndTurnRightClicked );
	Controls.EndTurnButtonLabel:RegisterCallback(	Mouse.eLClick, OnEndTurnClicked );
	Controls.OverflowCheckbox:RegisterCallback(		Mouse.eLClick, OnOverflowClick);
	Controls.TurnBlockerContainerAlpha:RegisterEndCallback( HideOverflowContainer );

	Controls.ObserverButtonLabel:RegisterCallback(Mouse.eLClick, function() LuaEvents.ActionPanel_EndObserverMode() end);
	Controls.EndObserverModeButton:RegisterCallback(Mouse.eLClick, function() LuaEvents.ActionPanel_EndObserverMode() end);

	-- Engine Events
	Events.CityCommandStarted.Add(			OnCityCommandStarted);
	Events.CityProductionChanged.Add(		OnCityProductionChanged );	
	Events.EndTurnBlockingChanged.Add(		OnEndTurnBlockingChanged );
	Events.EndTurnDirty.Add(				OnEndTurnDirty );
	Events.InputActionTriggered.Add(		OnInputActionTriggered );
	Events.InterfaceModeChanged.Add(		OnInterfaceModeChanged );
	Events.TurnBegin.Add(					OnTurnBegin);	
	Events.LocalPlayerChanged.Add(			OnLocalPlayerChanged );
	Events.LocalPlayerTurnBegin.Add(		OnLocalPlayerTurnBegin );
	Events.LocalPlayerTurnEnd.Add(			OnLocalPlayerTurnEnd );
	Events.LocalPlayerTurnUnready.Add(		OnLocalPlayerTurnUnready );
	Events.RemotePlayerTurnEnd.Add(			OnRemotePlayerTurnEnd );
	Events.NotificationAdded.Add(			OnNotificationAdded );
	Events.NotificationDismissed.Add(		OnNotificationDismissed );
	Events.ResearchChanged.Add(				OnResearchChanged );	
	Events.TurnTimerUpdated.Add(			OnTurnTimerUpdated );
	Events.UnitOperationSegmentComplete.Add(OnUnitOperationSegmentComplete);
	Events.UnitOperationsCleared.Add(		OnUnitOperationsCleared);
	Events.UserOptionChanged.Add(			OnUserOptionChanged);	
	Events.UploadCloudEndTurnStart.Add(		OnUploadCloudEndTurnStart);
	Events.UploadCloudEndTurnComplete.Add(		OnUploadCloudEndTurnComplete);

	-- LUA Events
	LuaEvents.AutoPlayStart.Add(				OnAutoPlayStart );		-- Raised by engine AutoPlay_Manager!
	LuaEvents.AutoPlayEnd.Add(					OnAutoPlayEnd );		-- Raised by engine AutoPlay_Manager!	
	LuaEvents.Tutorial_SlowNextTurnEnable.Add(	OnTutorialSlowTurnEnable );
	LuaEvents.ProductionPanel_IsQueueOpen.Add(	OnIsProdQueueOpen );
	LuaEvents.EndGameMenu_StartObserverMode.Add(OnStartObserverMode);

	m_kPopupDialog = PopupDialog:new( "ActionPanelPopupDialog" );
end


-- ===========================================================================
--	Initialize
-- ===========================================================================
function Initialize()
	ContextPtr:SetInitHandler( OnInit );
	ContextPtr:SetInputHandler( OnInputHandler, true );
	ContextPtr:SetRefreshHandler( OnRefresh );	
end
Initialize();
