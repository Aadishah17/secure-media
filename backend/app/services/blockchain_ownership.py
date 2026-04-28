import json
from pathlib import Path


CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}],
        "name": "registerImage",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "imageHash", "type": "string"}],
        "name": "getOwner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]


class BlockchainOwnershipService:
    def __init__(
        self,
        provider_uri=None,
        contract_address=None,
        owner_address=None,
        private_key=None,
        chain_id=None,
        registry_path=None,
    ):
        self.provider_uri = provider_uri
        self.contract_address = contract_address
        self.owner_address = owner_address
        self.private_key = private_key
        self.chain_id = chain_id
        self.registry_path = Path(registry_path) if registry_path else None

    def _load_registry(self):
        if self.registry_path is None or not self.registry_path.exists():
            return {}

        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
        return {}

    def _save_registry(self, data):
        if self.registry_path is None:
            return

        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _load_contract(self):
        try:
            from web3 import Web3
        except ImportError:
            return None, None

        if not self.provider_uri or not self.contract_address:
            return None, None

        web3 = Web3(Web3.HTTPProvider(self.provider_uri))
        if not web3.is_connected():
            return None, None

        contract = web3.eth.contract(address=Web3.to_checksum_address(self.contract_address), abi=CONTRACT_ABI)
        return web3, contract

    def register_hash(self, image_hash):
        web3, contract = self._load_contract()
        if web3 is None or contract is None:
            registry = self._load_registry()
            if image_hash not in registry:
                registry[image_hash] = {
                    "owner": self.owner_address or "Unverified",
                    "blockchain_verified": False,
                }
                self._save_registry(registry)
            return None

        if not self.private_key or not self.owner_address or not self.chain_id:
            return None

        owner = contract.functions.getOwner(image_hash).call()
        if owner and owner != "0x0000000000000000000000000000000000000000":
            return None

        nonce = web3.eth.get_transaction_count(self.owner_address)
        transaction = contract.functions.registerImage(image_hash).build_transaction(
            {
                "from": self.owner_address,
                "nonce": nonce,
                "chainId": int(self.chain_id),
            }
        )
        signed = web3.eth.account.sign_transaction(transaction, self.private_key)
        return web3.eth.send_raw_transaction(signed.raw_transaction).hex()

    def verify_hash(self, image_hash):
        web3, contract = self._load_contract()
        if web3 is None or contract is None:
            registry = self._load_registry()
            stored = registry.get(
                image_hash,
                {"owner": "Unverified", "blockchain_verified": False},
            )
            return {
                "owner": stored.get("owner", "Unverified"),
                "blockchain_verified": bool(stored.get("blockchain_verified", False)),
            }

        owner = contract.functions.getOwner(image_hash).call()
        is_verified = owner and owner != "0x0000000000000000000000000000000000000000"
        return {
            "owner": owner if is_verified else "Unverified",
            "blockchain_verified": bool(is_verified),
        }
