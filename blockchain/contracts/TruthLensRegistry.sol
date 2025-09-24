// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract TruthLensRegistry {
    struct HashInfo {
        string uploader;
        uint256 timestamp;
        bool exists;
    }
    
    mapping(bytes32 => HashInfo) public hashRegistry;
    address public owner;
    
    event HashStored(bytes32 indexed fileHash, string uploader, uint256 timestamp);
    
    constructor() {
        owner = msg.sender;
    }
    
    function storeHash(bytes32 _fileHash, string memory _uploader) public {
        require(!hashRegistry[_fileHash].exists, "Hash already exists");
        
        hashRegistry[_fileHash] = HashInfo({
            uploader: _uploader,
            timestamp: block.timestamp,
            exists: true
        });
        
        emit HashStored(_fileHash, _uploader, block.timestamp);
    }
    
    function getHashInfo(bytes32 _fileHash) public view returns (string memory, uint256) {
        require(hashRegistry[_fileHash].exists, "Hash not found");
        
        HashInfo memory info = hashRegistry[_fileHash];
        return (info.uploader, info.timestamp);
    }
    
    function hashExists(bytes32 _fileHash) public view returns (bool) {
        return hashRegistry[_fileHash].exists;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
}