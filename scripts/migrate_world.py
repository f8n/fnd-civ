from brownie import World, accounts
from civ.metadata import PLAYERS, WORLDS


def main():
    accounts.load("1")
    players = list(PLAYERS.values())

    old_world = World.at(WORLDS[-2])
    new_world = World.at(WORLDS[-1])

    new_world.migrateWorld(old_world.address, { 'from': accounts[0] })
    new_world.migratePlayers(old_world.address, players, { 'from': accounts[0] })
