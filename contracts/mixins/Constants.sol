// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

uint constant DEFENSE_CULTURE_BONUS = 5;
uint constant MAX_FORTIFICATION = 10;
uint constant FOOD_PER_FARM = 5;
uint constant POP_PER_SCIENCE = 10;
uint constant HANDLE_TURN_GAS_LIMIT = 5000000;
uint constant HANDLE_ATTACK_GAS_LIMIT = 5000000;
uint constant HANDLE_TRADE_GAS_LIMIT = 5000000;

// To be used in future versions
enum Event {
    Earthquake,
    Volcano,
    Barbarians,
    Plague,
    CivilWar,
    CultureWar,
    Immigration
}

enum AttackResponse {
    Retreat,
    Fight,
    Fortify
}

struct PlayerState {
    address player;
    uint currentTurn;

    // Primary attributes, directly impacted by actions
    uint land;
    uint farms;
    uint science;
    uint culture;
    uint soldiers;

    // Secondary attributes, impacted by primary attributes and production rates
    uint population;
    uint resources;
}
