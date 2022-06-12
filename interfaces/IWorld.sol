// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "../contracts/mixins/Constants.sol";

interface IWorld {

    // Setup
    function registerStrategy(address strategy) external;
    function updateStrategy(address strategy) external;

    // Gameplay functions
    function startGame() external;
    function playTurn(address player) external;
    function endGame() external;

    // Views
    function getStrategy(address player) external view returns(address);
    function getState(address player) external view returns(PlayerState memory);
    function getCivilianPopulation(address player) external view returns(uint);
    function getNextScienceCost(PlayerState memory state) external returns(uint);

    // Internal actions
    function explore() external;
    function research() external;
    function produce() external;
    function farm(uint farms) external;
    function create() external;
    function train(uint soldiers) external;

    // External actions
    function trade(address player) external;
    function attack(address player, uint soldiers) external;
}
