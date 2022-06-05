// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "../../interfaces/IStrategy.sol";
import "../../interfaces/IWorld.sol";
import "../mixins/Constants.sol";

contract BasicStrategy is IStrategy {

    // Do nothing
    function handleTurn(PlayerState calldata state) external virtual {}

    // Always trade
    function handleTrade(
        PlayerState calldata opponentState,
        PlayerState calldata selfState
    ) external virtual returns (bool approve) {
        return true;
    }

    // We won't have soldiers, so retreat as default
    // and take the risk on being destroyed
    function handleAttack(
        PlayerState calldata attackerState,
        PlayerState calldata selfState,
        uint attackers
    ) external virtual returns (AttackResponse, uint defenders, uint fortification) {
        return (AttackResponse.Retreat, 0, 0);
    }
}
