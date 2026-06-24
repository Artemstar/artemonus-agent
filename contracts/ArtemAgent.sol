// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/**
 * @title ArtemAgent
 * @author artemonus.eth
 * @notice Autonomous AI agent identity contract — on-chain identity and capability registry
 * @dev ERC-8004 compatible identity contract for artemonus.eth
 */
contract ArtemAgent {
    // ─── State ───────────────────────────────────────────────────────────────

    address public owner;
    string  public name;
    string  public ensName;
    string  public version;
    string  public description;
    bool    public active;
    uint256 public deployedAt;

    // ─── Capabilities ────────────────────────────────────────────────────────

    struct Capability {
        string  id;
        string  label;
        string  endpoint;
        bool    enabled;
    }

    mapping(bytes32 => Capability) private _capabilities;
    bytes32[] private _capabilityKeys;

    // ─── Events ──────────────────────────────────────────────────────────────

    event CapabilityAdded(bytes32 indexed key, string id, string label);
    event CapabilityToggled(bytes32 indexed key, bool enabled);
    event StatusChanged(bool active);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    // ─── Modifiers ───────────────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "ArtemAgent: caller is not the owner");
        _;
    }

    // ─── Constructor ─────────────────────────────────────────────────────────

    constructor(
        string memory _name,
        string memory _ensName,
        string memory _description
    ) {
        owner       = msg.sender;
        name        = _name;
        ensName     = _ensName;
        version     = "1.0.0";
        description = _description;
        active      = true;
        deployedAt  = block.timestamp;
    }

    // ─── Owner functions ─────────────────────────────────────────────────────

    function addCapability(
        string calldata id,
        string calldata label,
        string calldata endpoint
    ) external onlyOwner {
        bytes32 key = keccak256(abi.encodePacked(id));
        require(bytes(_capabilities[key].id).length == 0, "ArtemAgent: capability already exists");
        _capabilities[key] = Capability(id, label, endpoint, true);
        _capabilityKeys.push(key);
        emit CapabilityAdded(key, id, label);
    }

    function toggleCapability(string calldata id, bool enabled) external onlyOwner {
        bytes32 key = keccak256(abi.encodePacked(id));
        require(bytes(_capabilities[key].id).length > 0, "ArtemAgent: capability not found");
        _capabilities[key].enabled = enabled;
        emit CapabilityToggled(key, enabled);
    }

    function setActive(bool _active) external onlyOwner {
        active = _active;
        emit StatusChanged(_active);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "ArtemAgent: zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    // ─── View functions ──────────────────────────────────────────────────────

    function getCapability(string calldata id)
        external view
        returns (string memory label, string memory endpoint, bool enabled)
    {
        bytes32 key = keccak256(abi.encodePacked(id));
        Capability storage c = _capabilities[key];
        return (c.label, c.endpoint, c.enabled);
    }

    function capabilityCount() external view returns (uint256) {
        return _capabilityKeys.length;
    }

    function identity() external view returns (
        address _owner,
        string memory _name,
        string memory _ensName,
        string memory _version,
        string memory _description,
        bool   _active,
        uint256 _deployedAt
    ) {
        return (owner, name, ensName, version, description, active, deployedAt);
    }
}
