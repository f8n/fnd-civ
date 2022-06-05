// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "./BasicStrategy.sol";

contract TestResearchStrategy is BasicStrategy {

    // Research every turn if possible, otherwise produce
    function handleTurn(PlayerState calldata state) external override {
        IWorld(msg.sender).research();
    }
}
