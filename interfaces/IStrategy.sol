// SPDX-License-Identifier: MIT OR Apache-2.0

import "../contracts/mixins/Constants.sol";

pragma solidity ^0.8.0;

interface IStrategy {

    function handleTurn(PlayerState calldata state) external;

    function handleTrade(
        PlayerState calldata requesterState,
        PlayerState calldata selfState
    ) external returns (bool approve);

    function handleAttack(
        PlayerState calldata attackerState,
        PlayerState calldata selfState,
        uint attackers
    ) external returns (AttackResponse, uint defenders, uint fortifications);
}
