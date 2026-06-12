# Global Transit Security Architecture 🛡️

A master-level security framework integrating **Machine Learning** for real-time behavioral anomaly detection, backed by an immutable **Ethereum Blockchain** to ensure data integrity and transparency.

This project implements a **Zero-Trust Architecture** for a transit and ticketing system. Even if an attacker compromises a user's password, the AI Cognitive Firewall will block the transaction if the user's behavioral footprint (e.g., login hour, VPN usage, OS type) indicates malicious intent.

---

## 🏗️ Technical Architecture

The system is decoupled into three major components:

1. **AI Cognitive Firewall (Machine Learning)**
   - Utilizes `scikit-learn` and `xgboost` models (`best_model.pkl`) to evaluate 12 different behavioral features in real-time.
   - Assigns a risk score to every authentication and transaction attempt.
2. **Immutable Ledger (Blockchain)**
   - Powered by **Ethereum (Web3.py)** and a custom Solidity Smart Contract (`Ticketing.sol`).
   - Replaces centralized databases by minting user identities and ticketing transactions directly onto the blockchain.
   - Includes graceful degradation: Falls back to a local JSON ledger (`blockchain_ledger.json`) if an active Ethereum node isn't found.
3. **High-Performance REST Backend (FastAPI)**
   - Connects the ML models and the Blockchain layer.
   - Secures passwords using `bcrypt` hashing before storage.
4. **Glassmorphism UI**
   - A modern, responsive frontend portal for passengers and administrators.

---

## 📂 Repository Structure

```text
/
├── .env                        # Environment variables (Provider URL, Contract Address)
├── requirements.txt            # Python dependencies
├── main.py                     # FastAPI entry point & API endpoints
├── blockchain.py               # Web3 manager, cryptographic auth & ledger fallback
├── Ticketing.sol               # Ethereum Smart Contract for ticket storage
├── blockchain_ledger.json      # Fallback database / Mock Ledger
│
├── Machine Learning Artifacts/
│   ├── best_model.pkl          # Trained XGBoost/Scikit-Learn model
│   ├── scaler.pkl              # Data normalizer
│   ├── imputer.pkl             # Missing value handler
│   └── raw_user_behavior_dataset.csv # Original training data
│
└── Frontend /
    ├── index.html              # Architecture Landing Page
    ├── style.css               # Core styling & animations
    ├── user_login.html         # Passenger Portal Auth
    ├── user_dashboard.html     # Passenger internal dashboard
    ├── admin_login.html        # Admin Auth
    ├── admin_dashboard.html    # Unified Admin Console
    └── passenger_booking.html  # Ticket booking interface
```

---

## 🚀 Key Features

*   **Behavioral Threat Detection:** Evaluates login frequency, transaction amount, OS type, VPN usage, and request rate to stop anomalous behavior.
*   **Cryptographic Passwords:** All user credentials are computationally hashed using `bcrypt` before reaching the ledger.
*   **Dual-Ledger Support:** Maintains a global history chain and a specific quarantine/blocked chain for auditing threats.
*   **Immutable Travel Records:** Once a ticket is booked or updated, it is permanently anchored to the blockchain using the `journeyDate` parameter for type safety.

---

## 💻 Getting Started

### Prerequisites
*   Python 3.9+
*   *(Optional)* Ganache or a local Ethereum Node

### 1. Installation

Clone the repository and install the required dependencies:

```bash
git clone <repository_url>
cd ai
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the root directory and configure your Ethereum provider and Smart Contract address:

```env
PROVIDER_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0x224222C7da2329d3d58f11b134C3800b8050ADef
```
*(If you are not running a local Ethereum node, the system will seamlessly fall back to using `blockchain_ledger.json` for storage).*

### 3. Running the API Server

Start the FastAPI application:

```bash
python main.py
```
*The backend API will be available at `http://localhost:8000`*

### 4. Running the Frontend

In a separate terminal, serve the static HTML files:

```bash
python -m http.server 8080
```
*Access the user interface at `http://localhost:8080`*

---

## 📡 Core API Endpoints

Interactive Swagger documentation is available at **`http://localhost:8000/docs`** while the server is running.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/register` | Hashes password via bcrypt and mints identity to the blockchain. |
| `POST` | `/login` | Verifies cryptographic identity against the ledger. |
| `POST` | `/firewall/analyze` | Passes user metrics through the ML pipeline to detect threats. |
| `POST` | `/book` | Appends a new transportation ticket block to the global ledger. |
| `GET` | `/blockchain/global` | Retrieves the entire history of all booked tickets. |
| `GET` | `/blockchain/blocked` | Retrieves the quarantine ledger of blocked attacks/users. |
