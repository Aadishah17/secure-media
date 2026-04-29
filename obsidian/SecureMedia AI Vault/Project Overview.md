# Project Overview

SecureMedia AI helps users upload an image and check whether it is original or similar to media already seen by the system.

## Problem

Creators, journalists, marketplaces, and moderators need a quick way to detect reused media and verify ownership before content is published, sold, or distributed.

## Solution

The app provides a simple upload workflow:

1. User selects an image.
2. Backend generates a perceptual image hash.
3. Optional AI similarity compares the image against stored embeddings.
4. Optional blockchain ownership checks the registered owner.
5. Frontend displays similarity, duplicate status, owner, and verification result.

## Current Status

- React upload UI is implemented.
- Flask upload API is implemented.
- Hash-based duplicate detection works.
- Gemini, Hugging Face, and Vertex AI providers are wired as optional similarity paths.
- Blockchain ownership module is present with fallback behavior.
- Google Cloud Run deployment is live.
- PPT, PDF, and demo video are created.

