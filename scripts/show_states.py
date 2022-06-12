import random

from brownie import World, accounts
from civ.helpers import PLAYER_STATE_KEYS, parse_player_state
from civ.metadata import PLAYERS, WORLDS


def main():
    world = World.at(WORLDS[-1])
    for player, wallet in PLAYERS.items():
        state = world.getState(wallet)
        print(player, "->")
        print(parse_player_state(state))
        print("\n")
