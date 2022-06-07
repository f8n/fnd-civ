import math

import pytest
from brownie import accounts, reverts
from civ.helpers import *
from errors import *

# Gameplay tests

def test_turn_progression(world, create_strategy):
    player = accounts[1]
    world.registerStrategy(create_strategy.address, { 'from': player })
    assert world.getStrategy(player) == create_strategy.address

    # Start game
    assert world.currentTurn() == 0
    world.startGame()
    assert world.currentTurn() == 1
    assert world.currentTurnCompleted() == 0

    # Play turn
    for turn in range(1, 11):
        world.playTurn(player)
        state = parse_player_state(world.getState(player))
        assert state['player'] == player
        assert world.currentTurn() == turn + 1
        assert state['current_turn'] == turn

def test_multiplayer_turn_progression(world, create_strategy):
    player, partner = accounts[1:3]
    world.registerStrategy(create_strategy.address, { 'from': player })
    world.registerStrategy(create_strategy.address, { 'from': partner })
    world.startGame()

    # Play turn
    for turn in range(1, 11):
        world.playTurn(player)
        # Assert turn does NOT progress before last player goes
        assert world.currentTurn() == turn
        world.playTurn(partner)

        # Make sure turn is properly updated for both players
        for _player in [player, partner]:
            state = parse_player_state(world.getState(_player))
            assert state['current_turn'] == turn

        # Assert turn progression after last player
        assert world.currentTurn() == turn + 1

def test_prevents_action_outside_turn(world):
    rando = accounts[1]
    world.startGame()

    with reverts(ERROR_ONLY_ACTIVE_STRATEGY):
        world.create({ 'from': rando })

def test_prevents_multiple_actions(world, multi_action_strategy):
    player = accounts[1]
    world.registerStrategy(multi_action_strategy.address, { 'from': player })
    world.startGame()

    # Assert no state changes
    world.playTurn(player)
    assert_player_state(world, player, 'culture', 0)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + INITIAL_LAND)

# Basic production test

def test_base_resource_production(world, basic_strategy):
    player = accounts[1]
    world.registerStrategy(basic_strategy.address, { 'from': player })
    world.startGame()

    for turn in range(1, 11):
        world.playTurn(player)
        assert_player_state(world, player, 'resources', INITIAL_RESOURCES + (INITIAL_LAND * turn))

# Basic action tests

def test_explore(world, explore_strategy):
    player = accounts[1]
    world.registerStrategy(explore_strategy.address, { 'from': player })
    world.startGame()

    for turn in range(1, 11):
        tx = world.playTurn(player)
        assert_player_state(world, player, 'land', INITIAL_LAND + turn)
        assert_turn_action(tx, 'action', 'explore')
        assert_turn_summary(tx, 'land', INITIAL_LAND + turn)

def test_create(world, create_strategy):
    player = accounts[1]
    world.registerStrategy(create_strategy.address, { 'from': player })
    world.startGame()

    for turn in range(1, 11):
        tx = world.playTurn(player)
        assert_player_state(world, player, 'culture', 10 * turn)
        assert_turn_action(tx, 'action', 'create')
        assert_turn_summary(tx, 'culture', 10 * turn)

def test_research(world, research_strategy):
    player = accounts[1]
    world.registerStrategy(research_strategy.address, { 'from': player })
    world.startGame()

    # Should have enough resources to research to L3 (20 + 30)
    resources = INITIAL_RESOURCES
    for turn in range(1, 3):
        tx = world.playTurn(player)

        # Need to add 10 back because first science was free
        science = turn + 1
        resources = resources + INITIAL_LAND - (science * 10)
        assert_player_state(world, player, 'science', science)
        assert_player_state(world, player, 'resources', resources)
        assert_turn_action(tx, 'action', 'research')
        assert_turn_summary(tx, 'science', science)

    # Should not progress when there are insufficient resources
    world.playTurn(player)
    assert_player_state(world, player, 'science', 3)

def test_produce(world, produce_strategy):
    player = accounts[1]
    world.registerStrategy(produce_strategy.address, { 'from': player })
    world.startGame()

    resources = INITIAL_RESOURCES
    for turn in range(1, 11):
        tx = world.playTurn(player)
        resources = resources + INITIAL_LAND + INITIAL_POP
        assert_player_state(world, player, 'resources', resources)
        assert_turn_action(tx, 'action', 'produce')
        assert_turn_summary(tx, 'resources', resources)

def test_farm(world, farm_strategy):
    player = accounts[1]
    world.registerStrategy(farm_strategy.address, { 'from': player })
    world.startGame()

    # Assert farm increase
    assert_player_state(world, player, 'farms', 0)
    tx = world.playTurn(player)
    assert_player_state(world, player, 'farms', 4)
    assert_turn_action(tx, 'action', 'farm')

    # Assert produce
    world.playTurn(player)
    assert_player_state(world, player, 'resources', INITIAL_LAND + 11 + INITIAL_POP)

    # Assert research
    world.playTurn(player)
    assert_player_state(world, player, 'science', 2)

    # Assert population growth
    population = INITIAL_POP
    assert_player_state(world, player, 'population', population)
    for turn in range(4, 13):
        tx = world.playTurn(player)
        population += 1
        assert_player_state(world, player, 'population', population)
        assert_turn_summary(tx, 'population', population)

def test_farm_insufficient_land(world, farm_strategy):
    player = accounts[1]
    world.registerStrategy(farm_strategy.address, { 'from': player })
    world.startGame()

    # Assert farms capped at available land
    farm_strategy.setFarmTarget(10)
    assert_player_state(world, player, 'farms', 0)
    world.playTurn(player)
    assert_player_state(world, player, 'farms', 5)

def test_train(world, attack_strategy):
    player = accounts[1]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.startGame()

    attack_strategy.setTrainTarget(5, { 'from': player })
    assert_player_state(world, player, 'soldiers', 0)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES)
    world.playTurn(player)
    assert_player_state(world, player, 'soldiers', 5)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + INITIAL_LAND - 5)

def test_train_insufficient_population(world, attack_strategy):
    player = accounts[1]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.startGame()

    # Assert soldiers capped at available civilian population
    attack_strategy.setTrainTarget(20, { 'from': player })
    assert_player_state(world, player, 'soldiers', 0)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES)
    world.playTurn(player)
    assert_player_state(world, player, 'soldiers', 10)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + INITIAL_LAND - 10)
