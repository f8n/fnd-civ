// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "./BasicStrategy.sol";

contract TestMultiActionStrategy is BasicStrategy {

    // Try doing multiple things in a turn
    function handleTurn(PlayerState calldata state) external override {
        IWorld world = IWorld(msg.sender);
        world.create();
        world.produce();
    }
}
