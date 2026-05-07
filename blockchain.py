import os
from web3 import Web3
import json
import time

LEDGER_FILE = "blockchain_ledger.json"

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
    def __init__(self, provider_url="http://127.0.0.1:7545"):
        self.w3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = "0x224222C7da2329d3d58f11b134C3800b8050ADef"
        self.contract = None
        self.mock_db = self._load_ledger()
        
        # In a real demo, the user should provide the deployed contract address.
        # For this simulation, we'll try to connect or use a fallback.
        if self.w3.is_connected():
            print(f"Connected to Ethereum at {provider_url}")
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=TICKETING_ABI)
        else:
            print("Warning: ETH node not connected. Using Local Permanent JSON Simulation.")


    def _load_ledger(self):
        if os.path.exists(LEDGER_FILE):
            try:
                with open(LEDGER_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
                
        empty_db = {"global": [], "users": {}, "blocked": [], "identities": {}}
        with open(LEDGER_FILE, "w") as f:
            json.dump(empty_db, f, indent=4)
        return empty_db

    def _save_ledger(self):
        with open(LEDGER_FILE, "w") as f:
            json.dump(self.mock_db, f, indent=4)

    def record_identity(self, user_id, password):
        """Mint a new user into the Identity Blockchain layer"""
        # Ensure identities ledger exists for backwards compatibility 
        if "identities" not in self.mock_db:
            self.mock_db["identities"] = {}
            
        if user_id in self.mock_db["identities"]:
            return False # Duplicate identity
            
        self.mock_db["identities"][user_id] = {
            "password": password,
            "timestamp": time.time(),
            "status": "Verified"
        }
        self._save_ledger()
        return True
        
    def verify_identity(self, user_id, password):
        """Perform a cryptographic auth check against the Identity Blockchain"""
        if "identities" not in self.mock_db:
            return False
            
        if user_id in self.mock_db["identities"]:
            return self.mock_db["identities"][user_id]["password"] == password
            
        return False

    def record_blocked_transaction(self, user_id, tx_data):
        if self.w3.is_connected() and self.contract:
            # Placeholder for Smart Contract call handling malicious activity
            return True
        else:
            entry = {**tx_data, "user_id": user_id, "timestamp": time.time()}
            self.mock_db["blocked"].append(entry)
            self._save_ledger()
            return True

    def get_blocked_history(self):
        if self.w3.is_connected() and self.contract:
            return []
        else:
            return self.mock_db.get("blocked", [])

    def record_transaction(self, user_id, tx_data):
        if self.w3.is_connected() and self.contract:
            # Send Real Transaction to Ganache
            account = self.w3.eth.accounts[0] # Use first free Ganache account
            amount = int(tx_data.get('amount', 0))
            
            print(f"Blockchain: Sending Smart Contract Tx for {user_id}")
            # Smart Trick: Use the generic string 'txType' field to store the 'date' string securely on-chain
            # so we don't have to force the user to re-compile their Solidity code for a new column!
            journey_date = str(tx_data.get('date', 'Unknown'))
            k
            tx_hash = self.contract.functions.recordTransaction(
                user_id,
                tx_data.get('source', 'Unknown'),
                tx_data.get('destination', 'Unknown'),
                amount,
                journey_date
            ).transact({'from': account})
            
            # Wait for block to be mined
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Tx Mined Successfully in Block {receipt.blockNumber}!")
            return True
        else:
            # Mock behavior
            entry = {**tx_data, "user_id": user_id, "timestamp": time.time()}
            self.mock_db["global"].append(entry)
            if user_id not in self.mock_db["users"]:
                self.mock_db["users"][user_id] = []
            self.mock_db["users"][user_id].append(entry)
            self._save_ledger()
            return True

    def get_all_history(self, user_id=None):
        if self.w3.is_connected() and self.contract:
            # Fetch directly from the Smart Contract!
            if user_id:
                raw_txs = self.contract.functions.getUserTransactions(user_id).call()
            else:
                raw_txs = self.contract.functions.getGlobalTransactions().call()
                
            formatted_txs = []
            for t in raw_txs:
                formatted_txs.append({
                    "user_id": t[0],
                    "source": t[1],
                    "destination": t[2],
                    "amount": t[3],
                    "timestamp": t[4],
                    "type": "TICKET_BOOKING",
                    "date": t[5] if "-" in t[5] else None # Extract the date back from txType field!
                })
            return formatted_txs
        else:
            # Fetch from Mock
            if user_id:
                return self.mock_db["users"].get(user_id, [])
            return self.mock_db["global"]

# Alias for main.py compatibility
BlockchainManager = EthereumBlockchainManager
