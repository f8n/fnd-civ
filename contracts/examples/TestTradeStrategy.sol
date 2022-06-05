// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "./BasicStrategy.sol";

contract TestTradeStrategy is BasicStrategy {

    mapping(address => address) public tradePartner;

    // Public setter for testing purposes
    function setTradePartner(address newPartner) public {
        tradePartner[msg.sender] = newPartner;
    }

    // Trade with trade partner
    function handleTurn(PlayerState calldata state) external override {
        if (tradePartner[state.player] != address(0)) {
            IWorld(msg.sender).trade(tradePartner[state.player]);
        }
    }

    // Only accept trades from trade partner
    function handleTrade(
        PlayerState calldata requesterState,
        PlayerState calldata selfState
    ) external override returns (bool approve) {
        if (requesterState.player == tradePartner[selfState.player]) {
            approve = true;
        }
    }
}
