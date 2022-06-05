// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

uint constant DEFENSE_CULTURE_BONUS = 5;
uint constant MAX_FORTIFICATION = 10;
uint constant FOOD_PER_FARM = 5;
uint constant POP_PER_SCIENCE = 10;

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
