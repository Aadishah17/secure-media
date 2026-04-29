// SecureMedia Web3 integration utility
// Intended for future frontend wallet integrations (e.g. MetaMask)

export const CONTRACT_ADDRESS = '0x7f31d7CE7BA746aeb36E4d651BfD66f9B56D8641' // Example Sepolia address
export const CHAIN_ID = 11155111

export const CONTRACT_ABI = [
  "event ImageRegistered(bytes32 indexed imageKey, string imageHash, address indexed owner)",
  "function registerImage(string calldata imageHash) external",
  "function getOwner(string calldata imageHash) external view returns (address)",
  "function verifyOwnership(string calldata imageHash, address claimant) external view returns (bool)"
]

export async function checkProvider() {
  if (typeof window.ethereum !== 'undefined') {
    return true;
  }
  return false;
}

export async function requestAccount() {
  if (!await checkProvider()) return null;
  
  try {
    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
    return accounts[0];
  } catch (error) {
    console.error("Error requesting account:", error);
    return null;
  }
}
