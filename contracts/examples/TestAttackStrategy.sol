// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "../mixins/Constants.sol";
import "./BasicStrategy.sol";

contract TestAttackStrategy is BasicStrategy {

    struct DefenseDetails {
        uint defenders;
        uint fortifications;
    }

    mapping(address => address) public target;
    mapping(address => uint) public trainTarget;

    mapping(address => AttackResponse) public attackResponse;
    mapping(address => DefenseDetails) public defenseDetails;

    // Setters

    function setAttackTarget(address _target) public {
        target[msg.sender] = _target;
    }

    function setTrainTarget(uint _target) public {
        trainTarget[msg.sender] = _target;
    }

    function setAttackResponse(AttackResponse _response, uint defenders, uint fortifications) public {
        attackResponse[msg.sender] = _response;
        defenseDetails[msg.sender] = DefenseDetails(defenders, fortifications);
    }

    // Attack target
    function handleTurn(PlayerState calldata state) external override {
        IWorld world = IWorld(msg.sender);
        address _target = target[state.player];

        // Attack with all soldiers if there's a target
        if (target[state.player] != address(0)) {
            world.attack(target[state.player], state.soldiers);

        // Train if there's a training goal
        } else if (trainTarget[state.player] > 0) {
            world.train(trainTarget[state.player]);
        }
    }

    // Handle attacks

    function handleAttack(
        PlayerState calldata attackerState,
        PlayerState calldata selfState,
        uint attackers
    ) external override returns (AttackResponse response, uint defenders, uint fortifications) {
        DefenseDetails memory _defense = defenseDetails[selfState.player];
        response = attackResponse[selfState.player];
        defenders = _defense.defenders;
        fortifications = _defense.fortifications;
    }
}
