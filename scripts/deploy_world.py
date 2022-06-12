from brownie import World, accounts


def main():
    account = accounts.load("1")
    world = World.deploy({ 'from': accounts[0] }, publish_source=True)
    print("A new world is possible:", world.address)
