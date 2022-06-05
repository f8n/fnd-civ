# Getting Started

### Using [Brownie](https://eth-brownie.readthedocs.io/)

Fork this repo, and start developing your own strategies in `/contracts`.

### Using other build tools

Copy `/contracts` and `/interfaces` into `/contracts` for [hardhat](https://hardhat.org/), or `/src` for [foundry](https://getfoundry.sh/).

### Extending `BasicStrategy.sol`

You should be able to inherit `BasicStrategy.sol` to get started. The test strategies in `/contracts/examples` are also a good starting point. `TestCreateStrategy.sol` in particular establishes a solid baseline if you were to only create culture every single turn.


# Notes

- Function calls fail altogether if there aren't sufficient resources. Civilizations are not smart enough to carry out partial instructions.
- This world is minimally tested. Civilizations beware. Alternatively try to break it to win an award.
- This world is expensive. There are no gas optimizations. Be careful trying to do too much in your strategies.
- This world has no medicine. All soldiers in a fight die.
- This world is not our world. Not everything works as you expect. Go explore and try things!


# Development

Building: `brownie compile`

Testing: `brownie test`
