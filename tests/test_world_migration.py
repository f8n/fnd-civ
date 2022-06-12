import pytest
from brownie import World, accounts, reverts
from errors import *


def test_world_migration(world, create_strategy):
    players = accounts[1:11]

    # Start game and play 1 round on World 1
    for player in players:
        world.registerStrategy(create_strategy, { 'from': player })

    world.startGame()
    for player in players[1:]:
        world.playTurn(player)

    assert world.numActivePlayers() == 9
    assert world.gameNumber() == 1
    assert world.currentTurn() == 1
    assert world.currentTurnCompleted() == 8

    # Deploy World 2 & import
    new_world = accounts[0].deploy(World)
    new_world.migrateWorld(world)
    new_world.migratePlayers(world, players)

    # Validate import
    assert new_world.validateMigration(world)
    assert new_world.numActivePlayers() == 9
    assert new_world.gameNumber() == 1
    assert new_world.currentTurn() == 1
    assert new_world.currentTurnCompleted() == 8

    # Validate turn finishes on World 2
    new_world.playTurn(players[0])
    assert new_world.currentTurn() == 2
    assert new_world.currentTurnCompleted() == 0

    # Validate a new turn can be run on World 2
    for player in players:
        new_world.playTurn(player)
    assert new_world.currentTurn() == 3
