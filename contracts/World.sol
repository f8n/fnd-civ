// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "../interfaces/IStrategy.sol";
import "../interfaces/IWorld.sol";
import "./mixins/Constants.sol";


contract World is IWorld {

    // Game vars
    mapping(address => bool) public isGameMaster;

    uint public gameNumber;
    uint public gameStartBlock;
    uint public gameEndBlock;

    uint public numActivePlayers;
    mapping(address => bool) public isPlayerActive;

    // Turn vars
    uint public currentTurn;
    uint public currentTurnCompleted;

    address public _activePlayer;
    address public _activeStrategy;
    bool public _hasPlayerActed;

    // Player vars
    mapping(address => address) private _playerStrategy;
    mapping(address => PlayerState) private _playerStates;

    // Events

    event TurnAction(
        address indexed player,
        uint indexed game,
        uint indexed turn,
        string action,
        // Naive assumption on arg types
        address opponent,
        uint param
    );

    event TurnSummary(
        address indexed player,
        uint indexed game,
        uint indexed turn,
        uint land,
        uint farms,
        uint science,
        uint culture,
        uint soldiers,
        uint population,
        uint resources
    );

    event Resign(
        address indexed player,
        uint indexed game,
        uint indexed turn,
        string reason
    );

    // Modifiers

    modifier onlyGameMaster() {
        require(isGameMaster[msg.sender], "Caller must be game master");
        _;
    }

    modifier onlyGameNotInProgress() {
        require(gameStartBlock == 0 || gameEndBlock > 0, "Game is in progress");
        _;
    }

    modifier onlyGameInProgress() {
        require(isGameInProgress(), "Game not in progress");
        _;
    }

    modifier onlyPlayerActive(address player) {
        require(isPlayerActive[player], "Player is not active");
        _;
    }

    modifier onlyActiveStrategy() {
        require(msg.sender == _activeStrategy, "Can only be called by active strategy");
        _;
    }

    modifier onlyPlayerNotActed() {
        require(!_hasPlayerActed, "Player already acted this turn");
        _;
    }

    // Setup, game admin

    constructor () {
        isGameMaster[msg.sender] = true;
    }

    function addGameMaster(address new_gm) external onlyGameMaster {
        isGameMaster[new_gm] = true;
    }

    function removeGameMaster(address gm) external onlyGameMaster {
        isGameMaster[gm] = false;
    }

    function startGame() external onlyGameMaster onlyGameNotInProgress {
        gameStartBlock = block.number;
        gameNumber += 1;
        currentTurn = 1;
    }

    function endGame() external onlyGameMaster onlyGameInProgress {
        currentTurn = 0;
        gameEndBlock = block.number;
    }

    // Player admin

    function registerStrategy(address strategy) external onlyGameNotInProgress {
        _playerStrategy[msg.sender] = strategy;
        _initPlayerState(msg.sender);

        if (!isPlayerActive[msg.sender]) {
            isPlayerActive[msg.sender] = true;
            numActivePlayers += 1;
        }
    }

    function updateStrategy(address strategy) onlyPlayerActive(msg.sender) external {
        _playerStrategy[msg.sender] = strategy;
    }

    function resign() external {
        _resign(msg.sender, "Player resigned");
    }

    // Getters

    function isGameInProgress() public view returns(bool) {
        return gameStartBlock > 0 && gameEndBlock == 0;
    }

    function getStrategy(address player) external view returns(address) {
        return _playerStrategy[player];
    }

    function getState(address player) public view returns(PlayerState memory) {
        return _playerStates[player];
    }

    function getCivilianPopulation(address player) external view returns(uint) {
        return _getCivilianPopulation(_playerStates[player]);
    }

    function getNextScienceCost(PlayerState memory state) external returns(uint) {
        return _computeNextScienceCost(state);
    }

    // Game mechanics

    function playTurn(address player) external onlyGameMaster onlyPlayerActive(player) {
        PlayerState storage state = _playerStates[player];
        require(state.currentTurn < currentTurn, "Player already played this turn");

        _initPlayerTurn(player, state);
        try IStrategy(_playerStrategy[player]).handleTurn{
            gas: HANDLE_TURN_GAS_LIMIT
        }(state) {} catch {}
        _finishPlayerTurn();

        emit TurnSummary(
            player, gameNumber, currentTurn,
            state.land, state.farms, state.science, state.culture, state.soldiers,
            state.population, state.resources
        );

        // Progress turn
        _progressTurn();
    }


    // Domestic actions

    // Increment territory by 1
    function explore() external onlyActiveStrategy onlyPlayerNotActed {
        _playerStates[_activePlayer].land += 1;
        _markPlayerActed();
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "explore", address(0), 0);
    }

    // Increment science level by x, where resource cost is 1 x level
    function research() onlyActiveStrategy onlyPlayerNotActed external {
        PlayerState storage state = _playerStates[_activePlayer];
        uint cost = _computeNextScienceCost(state);

        if (_payResources(state, cost)) {
            state.science += 1;
        }
        _markPlayerActed();
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "research", address(0), 0);
    }

    // Produce additional resources for the turn using population
    function produce() external onlyActiveStrategy onlyPlayerNotActed {
        PlayerState storage state = _playerStates[_activePlayer];
        state.resources += _getCivilianPopulation(state);
        _markPlayerActed();
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "produce", address(0), 0);
    }

    // Convert land into farms for food production
    // Cost is 10 resource per farm
    function farm(uint farms) external onlyActiveStrategy onlyPlayerNotActed {
        PlayerState storage state = _playerStates[_activePlayer];
        uint newFarms = _validateFarms(state, farms);

        if (_payResources(state, newFarms * 10)) {
            state.farms += newFarms;
        }
        _markPlayerActed();
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "farm", address(0), farms);
    }

    // +1 to culture for each civilian population
    function create() external onlyActiveStrategy onlyPlayerNotActed {
        PlayerState storage state = _playerStates[_activePlayer];
        state.culture += _getCivilianPopulation(state);
        _markPlayerActed();
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "create", address(0), 0);
    }

    // Pay resource and trade population for soldier
    function train(uint soldiers) external onlyActiveStrategy onlyPlayerNotActed {
        PlayerState storage state = _playerStates[_activePlayer];
        uint newSoldiers = _validateTrain(state, soldiers);

        if (_payResources(state, newSoldiers)) {
            state.soldiers += newSoldiers;
        }
        _markPlayerActed();
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "train", address(0), soldiers);
    }

    // External actions

    /**
     * Propose a trade with another player.
     *
     * If they agree, each side effectively calls `produce` and `create`
     * using the other's civilian populations.
     */
    function trade(address partner) external onlyActiveStrategy onlyPlayerNotActed {
        PlayerState storage proposerState = _playerStates[_activePlayer];
        PlayerState storage receiverState = _playerStates[partner];

        bool approve;
        try IStrategy(_playerStrategy[partner]).handleTrade{
            gas: HANDLE_TRADE_GAS_LIMIT
        }(proposerState, receiverState) returns (bool _approve) {
            approve = _approve;
        } catch {}

        if (approve) {
            uint proposerCivilians = _getCivilianPopulation(proposerState);
            uint receiverCivilians = _getCivilianPopulation(receiverState);

            proposerState.resources += receiverCivilians;
            proposerState.culture += receiverCivilians;

            receiverState.resources += proposerCivilians;
            receiverState.culture += proposerCivilians;
        }
        _markPlayerActed();
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "trade", partner, 0);
    }

    /**
     * Attack another player with soldiers for a chance of territory and resources.
     *
     * Defender chooses
     * - Fight (no bonus)
     * - Fortify (spends resource for bonus)
     * - Retreat (lose territory and more resources, but no casualties)
     *
     * Defender gets culture bump if they win
     *
     * Both sides loses soldiers unless there's a retreat
     * Player is disqualified if territory drops below 0
     */
    function attack(address target, uint soldiers) external onlyActiveStrategy onlyPlayerNotActed {
        PlayerState storage attackerState = _playerStates[_activePlayer];
        PlayerState storage defenderState = _playerStates[target];

        // Init vars
        AttackResponse resp;
        uint defenders;
        uint fortification;
        bool success;
        bool hasBattle;

        // Get attack response with fallback
        try IStrategy(_playerStrategy[target]).handleAttack{
            gas: HANDLE_ATTACK_GAS_LIMIT
        }(
            attackerState, defenderState, soldiers
        ) returns (AttackResponse _resp, uint _defenders, uint _fortification) {
            resp = _resp;
            defenders = _defenders;
            fortification = _fortification;
        } catch {}

        // Validate attack response
        (resp, defenders, fortification) = _validateAttackResponse(
            defenderState, resp, defenders, fortification
        );

        // Handle attack
        if (resp == AttackResponse.Retreat) {
            success = true;
            hasBattle = false;

        } else if (resp == AttackResponse.Fight) {
            hasBattle = true;
            if (soldiers > defenders) {
                success = true;
            }

        } else if (resp == AttackResponse.Fortify) {
            hasBattle = true;

            if (_payResources(defenderState, fortification)) {
                if (soldiers > defenders + fortification) {
                    success = true;
                }
            } else if (soldiers > defenders) {
                success = true;
            }
        }

        // Handle win/loss rewards
        if (success) {
            _takeLoot(attackerState, defenderState);
            _takeLand(attackerState, defenderState);

        } else if (hasBattle) {
            defenderState.culture += DEFENSE_CULTURE_BONUS;
        }

        // Take casualties
        if (hasBattle) {
            _takeCasualties(attackerState, soldiers);
            _takeCasualties(defenderState, defenders);
        }

        // Clean up, check for defeat
        _markPlayerActed();
        _processDefeatConditions(attackerState);
        _processDefeatConditions(defenderState);
        emit TurnAction(_activePlayer, gameNumber, currentTurn, "attack", target, soldiers);
    }

    // General internal turn functions

    function _initPlayerState(address player) private returns (PlayerState storage) {
        PlayerState storage state = _playerStates[player];
        state.player = player;
        state.currentTurn = 0;

        state.land = 5;
        state.farms = 0;
        state.soldiers = 0;

        state.population = 10;
        state.resources = 50;
        state.science = 1;
        state.culture = 0;

        return state;
    }

    function _initPlayerTurn(address player, PlayerState storage state) private {
        state.currentTurn += 1;
        _activePlayer = player;
        _activeStrategy = _playerStrategy[player];
        _updateProduction();
    }

    function _finishPlayerTurn() private {
        _activePlayer = address(0);
        _activeStrategy = address(0);
        _hasPlayerActed = false;
    }

    function _progressTurn() private {
        currentTurnCompleted += 1;

        if (currentTurnCompleted == numActivePlayers) {
            currentTurn += 1;
            currentTurnCompleted = 0;
        }
    }

    function _markPlayerActed() private {
        _hasPlayerActed = true;
    }

    function _payResources(PlayerState storage state, uint cost) private returns (bool success) {
        if (cost <= state.resources) {
            state.resources -= cost;
            success = true;
        }
    }

    // Internal aciton functions

    function _validateFarms(PlayerState memory state, uint farms) private returns (uint newFarms) {
        uint unfarmedLand = _getUnfarmedLand(state);

        if (farms > unfarmedLand) {
            newFarms = unfarmedLand;
        } else {
            newFarms = farms;
        }
    }

    function _validateTrain(PlayerState memory state, uint soldiers) private returns (uint newSoldiers) {
        uint civilians = _getCivilianPopulation(state);

        if (soldiers > civilians) {
            newSoldiers = civilians;
        } else {
            newSoldiers = soldiers;
        }
    }
    function _validateAttackResponse(
        PlayerState memory state,
        AttackResponse resp,
        uint defenders,
        uint fortifications
    ) private returns (AttackResponse _resp, uint _defenders, uint _fortifications) {
        _resp = resp;

        if (defenders > state.soldiers) {
            _defenders = state.soldiers;
        } else {
            _defenders = defenders;
        }

        if (fortifications > MAX_FORTIFICATION) {
            _fortifications = MAX_FORTIFICATION;
        } else {
            _fortifications = fortifications;
        }
    }

    function _computeLoot(PlayerState memory state) private returns (uint loot) {
        if (state.resources == 0) {
            loot = 0;
        } else if (state.resources < state.land) {
            loot = 1;
        } else {
            loot = state.resources / state.land;
        }
    }

    function _takeLoot(PlayerState storage attackerState, PlayerState storage defenderState) private {
        uint loot = _computeLoot(defenderState);
        attackerState.resources += loot;

        if (loot > defenderState.resources) {
            defenderState.resources = 0;
        } else {
            defenderState.resources -= loot;
        }
    }

    function _takeLand(PlayerState storage attackerState, PlayerState storage defenderState) private {
        if (defenderState.land > 0) {
            attackerState.land += 1;
            defenderState.land -= 1;
        }
    }

    function _takeCasualties(PlayerState storage state, uint soldiers) private {
        // Remove from soldiers
        if (soldiers >= state.soldiers) {
            state.soldiers = 0;
        } else {
            state.soldiers -= soldiers;
        }

        // Remove from general population
        if (soldiers >= state.population) {
            state.population = 0;
        } else {
            state.population -= soldiers;
        }
    }

    function _processDefeatConditions(PlayerState memory state) private {
        if (state.population == 0) {
            _resign(state.player, "Population has gone to 0");
        } else if (state.land == 0) {
            _resign(state.player, "Land has gone to 0");
        }
    }


    function _resign(address player, string memory reason) private {
        if (isPlayerActive[player]) {
            isPlayerActive[player] = false;
            numActivePlayers -= 1;
            emit Resign(player, gameNumber, currentTurn, reason);
        }
    }

    // Internal production functions

    function _getCivilianPopulation(PlayerState memory state) private view returns (uint) {
        return state.population - state.soldiers;
    }

    function _getUnfarmedLand(PlayerState memory state) private view returns (uint) {
        return state.land - state.farms;
    }

    function _updateProduction() private {
        PlayerState storage state = _playerStates[_activePlayer];
        _updatePopulation(state);
        _updateResources(state);
    }


    /**
     * Each farms produce 5 food per turn
     * Population grows by 10% as long as there's more food than population
     * Population cannot grow beyond 10 * science
     */
    function _updatePopulation(PlayerState storage state) private {
        uint food = state.farms * FOOD_PER_FARM;

        // There's sufficient food,  try to grow
        if (food >= state.population) {
            uint newPop = _computeNewPopulation(state.population);

            // Check science cap
            if (newPop <= state.science * POP_PER_SCIENCE) {
                state.population = newPop;
            }
        }
    }

    // Each unfarmed land produces 1 resource per turn
    function _updateResources(PlayerState storage state) private {
        state.resources += _getUnfarmedLand(state);
    }

    // Grow by 10%, with minimum of 1
    function _computeNewPopulation(uint population) private pure returns (uint) {
        if (population < 10) {
            return population + 1;
        } else {
            return population + (population / 10);
        }
    }

    function _computeNextScienceCost(PlayerState memory state) private returns (uint) {
        return (state.science + 1) * 10;
    }
}
