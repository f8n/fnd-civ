import random

from brownie import World, accounts
from civ.metadata import WORLDS


def main():
    account = accounts.load("1")
    World.at(WORLDS[-1]).startGame({ 'from': accounts[0] })
