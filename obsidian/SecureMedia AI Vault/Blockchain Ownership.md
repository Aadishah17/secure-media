# Blockchain Ownership

The blockchain layer is designed to store and verify image ownership using an EVM-compatible testnet such as Polygon Amoy or Ethereum Sepolia.

## Smart Contract

The contract stores:

- image hash
- owner address
- registration timestamp

## Important Files

- `contracts/SecureMediaOwnership.sol`
- `backend/app/services/blockchain_ownership.py`
- `docs/remix-deployment.md`

## Current Limitation

Live blockchain verification depends on a valid deployed contract address, funded wallet, and private key stored outside Git.

## Required Env Values

- `WEB3_PROVIDER_URI`
- `CONTRACT_ADDRESS`
- `OWNER_ADDRESS`
- `PRIVATE_KEY`
- `CHAIN_ID`

