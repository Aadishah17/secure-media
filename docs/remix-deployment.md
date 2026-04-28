# SecureMedia Ownership Deployment

## Recommended chain

Use Polygon Amoy for a hackathon build. It keeps gas low and works cleanly with Remix and standard EVM tooling.

## Remix steps

1. Open Remix and create `contracts/SecureMediaOwnership.sol`.
2. Compile with Solidity `0.8.20` or newer.
3. Open `Deploy & Run Transactions`.
4. Select `Injected Provider - MetaMask`.
5. Connect MetaMask to Polygon Amoy or an Ethereum testnet.
6. Deploy `SecureMediaOwnership`.
7. Copy the deployed contract address into `backend/.env.example` values or your real environment.

## Contract methods

- `registerImage(string imageHash)`: stores the hash with `msg.sender`
- `getOwner(string imageHash)`: returns the owner address
- `verifyOwnership(string imageHash, address claimant)`: returns `true` when the claimant owns the hash

## Backend setup

Install optional dependencies when needed:

```bash
python -m pip install -r backend/requirements-ai.txt
python -m pip install -r backend/requirements-web3.txt
```

For fast hackathon inference, use `openai/clip-vit-base-patch32`. Hugging Face documents CLIP as a standard image-feature model, and the `patch32` checkpoint is a practical speed/quality balance for CPU-first demos.
