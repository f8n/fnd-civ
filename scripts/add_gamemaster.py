from brownie import World, accounts
from civ.metadata import GM, WORLDS

def main():
    account = accounts.load("1")
    World.at(WORLDS[-1]).addGameMaster(GM, { 'from': accounts[0] })
