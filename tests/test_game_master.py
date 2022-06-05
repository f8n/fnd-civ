import pytest

from brownie import accounts, reverts
from errors import *

# Game master role

def test_gm_on_deploy(world):
    assert world.isGameMaster(accounts[0])

def test_add_gm_as_gm(world):
    sender, new_gm = accounts[0:2]
    assert not world.isGameMaster(new_gm)
    world.addGameMaster(new_gm, { 'from': sender })
    assert world.isGameMaster(new_gm)

def test_add_gm_as_not_gm(world):
    _, new_gm = accounts[0:2]
    assert not world.isGameMaster(new_gm)
    with reverts(ERROR_NOT_GM):
        world.addGameMaster(new_gm, { 'from': new_gm })

# Game start / end

def test_start_game_success(world):
    assert world.gameNumber() == 0
    assert world.gameStartBlock() == 0
    world.startGame();
    assert world.gameNumber() == 1
    assert world.gameStartBlock() > 0

def test_start_game_as_not_gm(world):
    with reverts(ERROR_NOT_GM):
        world.startGame({ 'from': accounts[1] });

def test_start_game_already_in_progress(world):
    world.startGame();
    with reverts(ERROR_GAME_IN_PROGRESS):
        world.startGame();

def test_end_game_success(world):
    world.startGame()
    assert world.gameEndBlock() == 0
    world.endGame()
    assert world.gameEndBlock() > 0

def test_end_game_not_gm(world):
    world.startGame()
    with reverts(ERROR_NOT_GM):
        world.endGame({ 'from': accounts[1] })

def test_end_game_not_started(world):
    with reverts(ERROR_GAME_NOT_IN_PROGRESS):
        world.endGame()
