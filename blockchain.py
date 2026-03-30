from web3 import Web3
import json
import time

# Mocking the ABI for the TicketingSystem Solidity contract
# In a real scenario, this is generated after compiling the Solidarity code.
TICKETING_ABI = json.loads("""
[
	{
		"anonymous": false,
		"inputs": [
			{ "indexed": false, "internalType": "string", "name": "userId", "type": "string" },
			{ "indexed": false, "internalType": "string", "name": "source", "type": "string" },
			{ "indexed": false, "internalType": "string", "name": "destination", "type": "string" },
			{ "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" }
		],
		"name": "TransactionRecorded",
		"type": "event"
	},
	{
		"inputs": [
			{ "internalType": "string", "name": "_userId", "type": "string" },
			{ "internalType": "string", "name": "_source", "type": "string" },
			{ "internalType": "string", "name": "_destination", "type": "string" },
			{ "internalType": "uint256", "name": "_amount", "type": "uint256" },
			{ "internalType": "string", "name": "_txType", "type": "string" }
		],
		"name": "recordTransaction",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getGlobalTransactions",
		"outputs": [
			{
				"components": [
					{ "internalType": "string", "name": "userId", "type": "string" },
					{ "internalType": "string", "name": "source", "type": "string" },
					{ "internalType": "string", "name": "destination", "type": "string" },
					{ "internalType": "uint256", "name": "amount", "type": "uint256" },
					{ "internalType": "uint256", "name": "timestamp", "type": "uint256" },
					{ "internalType": "string", "name": "txType", "type": "string" }
				],
				"internalType": "struct TicketingSystem.Transaction[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [ { "internalType": "string", "name": "_userId", "type": "string" } ],
		"name": "getUserTransactions",
		"outputs": [
			{
				"components": [
					{ "internalType": "string", "name": "userId", "type": "string" },
					{ "internalType": "string", "name": "source", "type": "string" },
					{ "internalType": "string", "name": "destination", "type": "string" },
					{ "internalType": "uint256", "name": "amount", "type": "uint256" },
					{ "internalType": "uint256", "name": "timestamp", "type": "uint256" },
					{ "internalType": "string", "name": "txType", "type": "string" }
				],
				"internalType": "struct TicketingSystem.Transaction[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
""")

class EthereumBlockchainManager:
    def __init__(self, provider_url="http://127.0.0.1:8545"):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = None
        self.contract = None
        
        # In a real demo, the user should provide the deployed contract address.
        # For this simulation, we'll try to connect or use a fallback.
        if self.w3.is_connected():
            print(f"Connected to Ethereum at {provider_url}")
            # Mock address for the simulation
            self.contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3" 
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=TICKETING_ABI)
        else:
            print("Warning: ETH node not connected. Using Local Mock Simulation.")
            self.mock_db = {"global": [], "users": {}, "blocked": []}

    def record_blocked_transaction(self, user_id, tx_data):
        if self.w3.is_connected() and self.contract:
            # Placeholder for Smart Contract call handling malicious activity
            return True
        else:
            entry = {**tx_data, "user_id": user_id, "timestamp": time.time()}
            self.mock_db["blocked"].append(entry)
            return True

    def get_blocked_history(self):
        if self.w3.is_connected() and self.contract:
            return []
        else:
            return self.mock_db.get("blocked", [])

    def record_transaction(self, user_id, tx_data):
        if self.w3.is_connected() and self.contract:
            # In a real app, we'd sign and send a transaction.
            print(f"Blockchain: Calling Smart Contract for {user_id}")
            # Simplified for demo: return success immediately
            return True
        else:
            # Mock behavior
            entry = {**tx_data, "user_id": user_id, "timestamp": time.time()}
            self.mock_db["global"].append(entry)
            if user_id not in self.mock_db["users"]:
                self.mock_db["users"][user_id] = []
            self.mock_db["users"][user_id].append(entry)
            return True

    def get_all_history(self, user_id=None):
        if self.w3.is_connected() and self.contract:
            # Fetch from Smart Contract
            return [] # Placeholder for real call
        else:
            # Fetch from Mock
            if user_id:
                return self.mock_db["users"].get(user_id, [])
            return self.mock_db["global"]

# Alias for main.py compatibility
BlockchainManager = EthereumBlockchainManager
