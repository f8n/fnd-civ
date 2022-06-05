import math

import pytest
from brownie import accounts, reverts
from civ.helpers import *
from errors import *

# Advanced action tests

def test_trade_approved(world, trade_strategy):
    player, partner = accounts[1:3]
    world.registerStrategy(trade_strategy.address, { 'from': player })
    world.registerStrategy(trade_strategy.address, { 'from': partner })
    world.startGame()

    # Set both sides to be trade partners
    trade_strategy.setTradePartner(partner, { 'from': player })
    trade_strategy.setTradePartner(player, { 'from': partner })
    tx = world.playTurn(player)

    # Assert logs
    new_resources = INITIAL_RESOURCES + INITIAL_POP + INITIAL_LAND
    new_culture = INITIAL_POP
    assert_turn_action(tx, 'action', 'trade')
    assert_turn_action(tx, 'opponent', partner)
    assert_turn_summary(tx, 'resources', new_resources)
    assert_turn_summary(tx, 'culture', new_culture)

    # Assert both sides get resources + culture production (+normal resource production for player)
    assert_player_state(world, player, 'resources', new_resources)
    assert_player_state(world, player, 'culture', new_culture)
    assert_player_state(world, partner, 'resources', INITIAL_RESOURCES + INITIAL_POP)
    assert_player_state(world, partner, 'culture', INITIAL_POP)


def test_trade_rejected(world, trade_strategy):
    player, partner = accounts[1:3]
    world.registerStrategy(trade_strategy.address, { 'from': player })
    world.registerStrategy(trade_strategy.address, { 'from': partner })
    world.startGame()

    # Don't set partner so they reject
    trade_strategy.setTradePartner(partner, { 'from': player })
    world.playTurn(player)

    # Assert neither side gets resources - player has wasted their turn
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + INITIAL_LAND)
    assert_player_state(world, player, 'culture', 0)
    assert_player_state(world, partner, 'resources', INITIAL_RESOURCES)
    assert_player_state(world, partner, 'culture', 0)

def test_attack_retreat(world, attack_strategy):
    player, defender = accounts[1:3]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.registerStrategy(attack_strategy.address, { 'from': defender })
    world.startGame()

    # Set attacker, retreat strategy from defender
    attack_strategy.setAttackTarget(defender, { 'from': player })
    attack_strategy.setAttackResponse(0, 0, 0, { 'from': defender })

    # Ensure attacker gets land + resources
    tx = world.playTurn(player)
    assert_turn_action(tx, 'action', 'attack')
    assert_turn_action(tx, 'opponent', defender)
    assert_turn_summary(tx, 'land', INITIAL_LAND + 1)
    assert_player_state(world, player, 'land', INITIAL_LAND + 1)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + INITIAL_LAND + compute_loot())
    assert_player_state(world, defender, 'land', INITIAL_LAND - 1)
    assert_player_state(world, defender, 'resources', INITIAL_RESOURCES - compute_loot())
    assert_player_state(world, defender, 'culture', 0)

def test_attack_fight_win(world, attack_strategy):
    player, defender = accounts[1:3]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.registerStrategy(attack_strategy.address, { 'from': defender })
    world.startGame()

    # Train a few soldiers to test for casualties
    attack_strategy.setTrainTarget(5, { 'from': player })
    attack_strategy.setTrainTarget(1, { 'from': defender })
    world.playTurn(player)
    world.playTurn(defender)
    assert_player_state(world, player, 'soldiers', 5)
    assert_player_state(world, player, 'population', 10)
    assert_player_state(world, defender, 'soldiers', 1)
    assert_player_state(world, defender, 'population', 10)

    # Set attacker, retreat strategy from defender
    attack_strategy.setAttackTarget(defender, { 'from': player })
    attack_strategy.setAttackResponse(1, 1, 0, { 'from': defender })

    # Assert winner gets land, loot, both sides lose casulties
    world.playTurn(player)
    assert_player_state(world, player, 'land', INITIAL_LAND + 1)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + (INITIAL_LAND * 2) - 5 + compute_loot())
    assert_player_state(world, player, 'soldiers', 0)
    assert_player_state(world, player, 'population', 5)
    assert_player_state(world, defender, 'land', INITIAL_LAND - 1)
    assert_player_state(world, defender, 'resources', INITIAL_RESOURCES + INITIAL_LAND - 1 - compute_loot())
    assert_player_state(world, defender, 'soldiers', 0)
    assert_player_state(world, defender, 'population', 9)
    assert_player_state(world, defender, 'culture', 0)

def test_attack_fight_lose(world, attack_strategy):
    player, defender = accounts[1:3]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.registerStrategy(attack_strategy.address, { 'from': defender })
    world.startGame()

    # Train a few soldiers to test for casualties
    attack_strategy.setTrainTarget(1, { 'from': player })
    attack_strategy.setTrainTarget(5, { 'from': defender })
    world.playTurn(player)
    world.playTurn(defender)
    assert_player_state(world, player, 'soldiers', 1)
    assert_player_state(world, player, 'population', 10)
    assert_player_state(world, defender, 'soldiers', 5)
    assert_player_state(world, defender, 'population', 10)

    # Set attacker, retreat strategy from defender
    attack_strategy.setAttackTarget(defender, { 'from': player })
    attack_strategy.setAttackResponse(1, 5, 0, { 'from': defender })

    # Assert no land transfer or loot, both sides lose casulties
    world.playTurn(player)
    assert_player_state(world, player, 'land', INITIAL_LAND)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + (INITIAL_LAND * 2) - 1)
    assert_player_state(world, player, 'soldiers', 0)
    assert_player_state(world, player, 'population', 9)
    assert_player_state(world, defender, 'land', INITIAL_LAND)
    assert_player_state(world, defender, 'resources', INITIAL_RESOURCES + INITIAL_LAND - 5)
    assert_player_state(world, defender, 'soldiers', 0)
    assert_player_state(world, defender, 'population', 5)
    assert_player_state(world, defender, 'culture', 5)

def test_attack_fortify_win(world, attack_strategy):
    player, defender = accounts[1:3]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.registerStrategy(attack_strategy.address, { 'from': defender })
    world.startGame()

    attack_strategy.setTrainTarget(9, { 'from': player })
    world.playTurn(player)
    world.playTurn(defender)

    # Set attacker, retreat strategy from defender
    attack_strategy.setAttackTarget(defender, { 'from': player })
    attack_strategy.setAttackResponse(2, 0, 8, { 'from': defender })

    # Assert winner gets land, loot, both sides lose casulties
    world.playTurn(player)
    loot = compute_loot(1, -8) # account for additional turn, resources paid for fortification
    assert_player_state(world, player, 'land', INITIAL_LAND + 1)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + (INITIAL_LAND * 2) - 9 + loot)
    assert_player_state(world, player, 'soldiers', 0)
    assert_player_state(world, player, 'population', 1)
    assert_player_state(world, defender, 'land', INITIAL_LAND - 1)
    assert_player_state(world, defender, 'resources', INITIAL_RESOURCES + INITIAL_LAND - 8 - loot)
    assert_player_state(world, defender, 'soldiers', 0)
    assert_player_state(world, defender, 'population', 10)
    assert_player_state(world, defender, 'culture', 0)

def test_attack_fortify_lose(world, attack_strategy):
    player, defender = accounts[1:3]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.registerStrategy(attack_strategy.address, { 'from': defender })
    world.startGame()

    attack_strategy.setTrainTarget(9, { 'from': player })
    world.playTurn(player)
    world.playTurn(defender)

    # Set attacker, retreat strategy from defender
    attack_strategy.setAttackTarget(defender, { 'from': player })
    attack_strategy.setAttackResponse(2, 0, 10, { 'from': defender })

    # Assert no land transfer or loot, both sides lose casulties
    world.playTurn(player)
    assert_player_state(world, player, 'land', INITIAL_LAND)
    assert_player_state(world, player, 'resources', INITIAL_RESOURCES + (INITIAL_LAND * 2) - 9)
    assert_player_state(world, player, 'soldiers', 0)
    assert_player_state(world, player, 'population', 1)
    assert_player_state(world, defender, 'land', INITIAL_LAND)
    assert_player_state(world, defender, 'resources', INITIAL_RESOURCES + INITIAL_LAND - 10)
    assert_player_state(world, defender, 'soldiers', 0)
    assert_player_state(world, defender, 'population', 10)
    assert_player_state(world, defender, 'culture', 5)

def test_defeat_no_population(world, attack_strategy):
    player, defender = accounts[1:3]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.registerStrategy(attack_strategy.address, { 'from': defender })
    world.startGame()

    attack_strategy.setTrainTarget(10, { 'from': player })
    attack_strategy.setTrainTarget(1, { 'from': defender })
    world.playTurn(player)
    world.playTurn(defender)

    # Set attacker, retreat strategy from defender
    attack_strategy.setAttackTarget(defender, { 'from': player })
    attack_strategy.setAttackResponse(2, 1, 10, { 'from': defender })

    # Assert no land transfer or loot, both sides lose casulties
    assert world.numActivePlayers() == 2
    assert world.isPlayerActive(player)
    assert world.isPlayerActive(defender)
    tx = world.playTurn(player)
    assert_resign_event(tx, 'reason', RESIGN_MESSAGE_POP)
    assert world.numActivePlayers() == 1
    assert not world.isPlayerActive(player)
    assert world.isPlayerActive(defender)

def test_defeat_no_land(world, attack_strategy):
    player, defender = accounts[1:3]
    world.registerStrategy(attack_strategy.address, { 'from': player })
    world.registerStrategy(attack_strategy.address, { 'from': defender })
    world.startGame()

    attack_strategy.setTrainTarget(5, { 'from': player })
    world.playTurn(player)
    world.playTurn(defender)

    attack_strategy.setAttackTarget(defender, { 'from': player })
    attack_strategy.setAttackResponse(0, 0, 0, { 'from': defender })

    assert world.numActivePlayers() == 2
    assert world.isPlayerActive(player)
    assert world.isPlayerActive(defender)

    # Attack 5 times to take all land
    for x in range(5):
        tx = world.playTurn(player)
        if (world.isPlayerActive(defender)):
            world.playTurn(defender)

    assert_resign_event(tx, 'reason', RESIGN_MESSAGE_LAND)
    assert world.numActivePlayers() == 1
    assert world.isPlayerActive(player)
    assert not world.isPlayerActive(defender)
