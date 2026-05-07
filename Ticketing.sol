// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TicketingSystem {
    
    struct Transaction {
        string userId;
        string source;
        string destination;
        uint256 amount;
        uint256 timestamp;
        string txType;
    }
    
    // Global ledger to store all ticket bookings
    Transaction[] public globalTransactions;
    
    // User-specific ledger map
    mapping(string => Transaction[]) private userTransactions;
    
    // Event to emit when a ticket is stored
    event TransactionRecorded(string userId, string source, string destination, uint256 amount);
    
    // Function to record a new ticket booking
    function recordTransaction(
        string memory _userId,
        string memory _source,
        string memory _destination,
        uint256 _amount,
        string memory _txType
    ) public {
        
        // Create the transaction block
        Transaction memory newTx = Transaction({
            userId: _userId,
            source: _source,
            destination: _destination,
            amount: _amount,
            timestamp: block.timestamp, // Uses the Blockchain's internal clock
            txType: _txType
        });
        
        // Save to Global Ledger
        globalTransactions.push(newTx);
        
        // Save to User's Private Ledger
        userTransactions[_userId].push(newTx);
        
        // Anchor to the blockchain securely
        emit TransactionRecorded(_userId, _source, _destination, _amount);
    }
    
    // View all transactions (For Government/Admin Audit)
    function getGlobalTransactions() public view returns (Transaction[] memory) {
        return globalTransactions;
    }
    
    // View specific user transaction history
    function getUserTransactions(string memory _userId) public view returns (Transaction[] memory) {
        return userTransactions[_userId];
    }
}
