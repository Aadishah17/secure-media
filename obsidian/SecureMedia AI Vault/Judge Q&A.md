# Judge Q&A

## What problem does SecureMedia AI solve?

SecureMedia AI helps identify whether an uploaded image is original or likely duplicated. It is aimed at creators, journalists, marketplaces, and moderators who need fast media trust checks.

## How does the system work?

The user uploads an image through the React interface. Flask receives the file, generates a perceptual hash, optionally runs AI similarity, checks ownership status, and returns similarity, duplicate status, owner, and blockchain verification.

## What makes this project different?

It combines three trust signals in one workflow:

- image hashing for fast duplicate detection
- optional AI similarity for stronger comparison
- blockchain-ready ownership verification

## Why Google Cloud?

The app is deployed on Google Cloud Run as a single service. This keeps the demo simple while still making the project scalable and accessible through a public URL.

## Where does Gemini fit?

Gemini is wired as an optional similarity provider. It can describe image content and support comparison workflows, while the hash-based system remains the fallback if Gemini is unavailable.

## Is blockchain verification fully live?

The smart contract and backend integration exist, but live verification still needs a valid deployed contract, funded wallet, and real private key stored securely outside Git.

## What are the main risks?

- API keys must be rotated and stored securely.
- Local JSON storage should be replaced with managed production storage.
- Blockchain verification needs final production credentials.

## What is the next improvement?

The next practical improvement is production-grade persistence for image hashes, embeddings, and ownership metadata.

