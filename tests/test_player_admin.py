import pytest

from brownie import ZERO_ADDRESS, accounts, reverts
from errors import *

# Registration, strategy update, surrender

def test_register_strategy_success(world):
    player, strategy = accounts[0:2]

    assert world.getStrategy(player) == ZERO_ADDRESS
    assert not world.isPlayerActive(player)
    assert world.numActivePlayers() == 0

    world.registerStrategy(strategy)
    assert world.getStrategy(player) == strategy
    assert world.isPlayerActive(player)
    assert world.numActivePlayers() == 1

def test_register_strategy_game_started(world):
    world.startGame()
    with reverts(ERROR_GAME_IN_PROGRESS):
        world.registerStrategy(accounts[1])

def test_update_strategy_success(world):
    player, strategy, strategy_2 = accounts[0:3]
    world.registerStrategy(strategy)
    assert world.isPlayerActive(player)
    assert world.getStrategy(player) == strategy
    world.updateStrategy(strategy_2)
    assert world.getStrategy(player) == strategy_2

def test_update_strategy_not_active(world):
    player, strategy = accounts[0:2]
    with reverts(ERROR_PLAYER_NOT_ACTIVE):
        world.updateStrategy(strategy)
