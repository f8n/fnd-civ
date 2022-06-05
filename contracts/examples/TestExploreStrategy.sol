// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "./BasicStrategy.sol";

contract TestExploreStrategy is BasicStrategy {

    // Explore every turn
    function handleTurn(PlayerState calldata state) external override {
        IWorld(msg.sender).explore();
    }
}
