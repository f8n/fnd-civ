// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "../mixins/Constants.sol";
import "./BasicStrategy.sol";

contract TestFarmStrategy is BasicStrategy {

    uint public farmTarget = 4;

    function setFarmTarget(uint target) public {
        farmTarget = target;
    }

    // Produce culture every turn
    function handleTurn(PlayerState calldata state) external override {
        IWorld world = IWorld(msg.sender);

        // Use most land and resources to build farms first turn
        // which should give enough food to grow until science 2
        if (state.currentTurn == 1) {
            world.farm(farmTarget);

        // Produce second turn to get resources
        } else if (state.currentTurn == 2) {
            world.produce();

        // Research third turn to start growing
        } else if (state.currentTurn == 3) {
            world.research();

        // After that either research or produce to research
        } else {
            uint researchCost = world.getNextScienceCost(state);

            if (researchCost <= state.resources) {
                world.research();
            } else {
                world.produce();
            }
        }
    }
}
