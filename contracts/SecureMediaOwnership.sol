// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SecureMediaOwnership {
    struct Record {
        address owner;
        uint256 registeredAt;
    }

    mapping(bytes32 => Record) private records;

    event ImageRegistered(bytes32 indexed imageKey, string imageHash, address indexed owner);

    function registerImage(string calldata imageHash) external {
        bytes32 imageKey = keccak256(bytes(imageHash));
        require(records[imageKey].owner == address(0), "Image already registered");

        records[imageKey] = Record({
            owner: msg.sender,
            registeredAt: block.timestamp
        });

        emit ImageRegistered(imageKey, imageHash, msg.sender);
    }

    function getOwner(string calldata imageHash) external view returns (address) {
        return records[keccak256(bytes(imageHash))].owner;
    }

    function verifyOwnership(string calldata imageHash, address claimant) external view returns (bool) {
        return records[keccak256(bytes(imageHash))].owner == claimant;
    }
}
