import random

from brownie import World, accounts
from civ.metadata import PLAYERS, WORLDS


def main():
    account = accounts.load("1")
    world = World.at(WORLDS[-1])
    print("Playing in World:", world.address)
    turn = world.currentTurn()

    players = list(PLAYERS.values())
    random.shuffle(players)

    for player in players:
        if world.isPlayerActive(player):
            print("Active:", player)

            state = world.getState(player)
            _turn = state[1]

            if _turn < turn:
                print("> Playing turn...")
                tx = world.playTurn(player, { 'from': accounts[0] })
            else:
                print("> Already played this turn, skipping")
        else:
            print("Not active:", player)
