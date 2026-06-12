from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel
import time
import json
import os
from blockchain import BlockchainManager

app = FastAPI(title="Secure Transportation API")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load AI Firewall components
try:
    model = joblib.load('best_model.pkl')
    scaler = joblib.load('scaler.pkl')
    imputer = joblib.load('imputer.pkl')
except Exception as e:
    print(f"Error loading AI models: {e}")
bm = BlockchainManager()

class UserBehavior(BaseModel):
    user_id: str
    password: str
    login_hour: int = 12
    login_frequency: int = 5
    location_id: int = 1
    device_id: int = 1
    transaction_amount: float = 0.0
    time_spent: float = 30.0
    failed_attempts: int = 0
    
    # New 5 features added for the new 16k ML Dataset
    is_vpn: int = 0
    request_rate: float = 1.0
    last_login_diff: float = 24.0
    os_type: int = 0
    browser_id: int = 1

class BookingRequest(BaseModel):
    user_id: str
    source: str
    destination: str
    date: str
    amount: float

class UpdateRequest(BaseModel):
    user_id: str
    original_ticket_hash: str
    new_source: str
    new_destination: str
    amount: float
    
class AuthRequest(BaseModel):
    user_id: str
    password: str



# Centralized User DB has been officially deprecated.
# All user identities are now strictly minted onto the Identity Blockchain Ledger.

@app.post("/register")
async def register_user(request: AuthRequest):
    # Attempt to mint the new identity block
    success = bm.record_identity(request.user_id, request.password)
    
    if not success:
        raise HTTPException(status_code=400, detail="User ID already exists on Blockchain.")
        
    return {"message": "User Permanently Minted to Identity Blockchain"}

@app.post("/login")
async def login_user(request: AuthRequest):
    is_valid = bm.verify_identity(request.user_id, request.password)
    
    if not is_valid:
        return {"success": False, "message": "Incorrect credentials or Identity not found."}
    return {"success": True, "message": "Login successful"}

@app.post("/firewall/analyze")
async def analyze_behavior(behavior: UserBehavior):
    # 1. Strict Brute Force Threshold Detection (Edge Firewall Rule)
    # A true Cognitive Firewall checks for flood/brute-force attacks BEFORE querying the secure database.
    if behavior.failed_attempts > 10:
        bm.record_blocked_transaction(
            behavior.user_id, 
            {"reason": "Brute Force Attack / Multiple Auth Failures", "risk_score": 99.9}
        )
        return {"status": "Suspicious", "reason": "Brute Force Locked"}

    # 2. Verification of Password Authenticity against Identity Blockchain
    is_password_correct = bm.verify_identity(behavior.user_id, behavior.password)

    if not is_password_correct:
        return {"status": "Wrong_Password", "reason": "System Rejection"}

    # Prepare data for prediction using a DataFrame to maintain feature names
    features_df = pd.DataFrame([{
        'login_hour': behavior.login_hour,
        'login_frequency': behavior.login_frequency,
        'location_id': behavior.location_id,
        'device_id': behavior.device_id,
        'transaction_amount': behavior.transaction_amount,
        'time_spent': behavior.time_spent,
        'failed_attempts': behavior.failed_attempts,
        'is_vpn': behavior.is_vpn,
        'request_rate': behavior.request_rate,
        'last_login_diff': behavior.last_login_diff,
        'os_type': behavior.os_type,
        'browser_id': behavior.browser_id
    }])
    
    # 3. Apply the Data Preprocessing Pipeline (Imputer -> Scaler)
    # The imputer was trained on all 12 columns in the new dataset methodology
    features_imputed = imputer.transform(features_df)
    scaled_features = scaler.transform(features_imputed)
    prediction = model.predict(scaled_features)[0]
    probability = model.predict_proba(scaled_features)[0][1] # Prob of being suspicious
    
    status = "Suspicious" if prediction == 1 else "Safe"
    
    # --- DETERMINISTIC OVERRIDE RULES ---
    # Guarantee that 0 payments are explicitly caught regardless of ML clustering
    if behavior.transaction_amount <= 0:
        status = "Suspicious"
        probability = 0.99

    # Securely append to quarantine ledger if suspicious
    if status == "Suspicious":
        bm.record_blocked_transaction(
            behavior.user_id, 
            {"reason": "AI Cognitive Threat (or Deterministic Rule Violation)", "risk_score": round(float(probability) * 100, 2)}
        )

    return {
        "user_id": behavior.user_id,
        "status": status,
        "risk_score": round(float(probability) * 100, 2),
        "timestamp": time.time()
    }

@app.post("/book")
async def book_ticket(request: BookingRequest):
    # In a real app, we'd run the firewall check here too.
    # For this demo, we'll record the booking on both blockchains.
    
    tx_data = {
        "type": "TICKET_BOOKING",
        "source": request.source,
        "destination": request.destination,
        "date": request.date,
        "amount": request.amount,
        "timestamp": time.time()
    }
    
    result = bm.record_transaction(request.user_id, tx_data)
    
    return {
        "message": "Ticket booked successfully",
        "blockchain_status": "Recorded on User and Global Chains",
        "details": tx_data
    }

@app.post("/update_ticket")
async def update_ticket(request: UpdateRequest):
    tx_data = {
        "type": "TICKET_UPDATED",
        "linked_hash": request.original_ticket_hash,
        "source": request.new_source,
        "destination": request.new_destination,
        "amount": request.amount,
        "timestamp": time.time()
    }
    
    result = bm.record_transaction(request.user_id, tx_data)
    
    return {
        "message": "Journey Update Appended to Blockchain",
        "status": "Immutable Record Created",
        "details": tx_data
    }

@app.get("/blockchain/history")
async def get_history(user_id: str = None):
    # Returns the chain. If user_id is provided, returns user-specific chain.
    history = bm.get_all_history(user_id)
    return {"chain": history, "count": len(history)}

@app.get("/blockchain/global")
async def get_global_history():
    history = bm.get_all_history()
    return {"chain": history, "count": len(history)}

@app.get("/blockchain/blocked")
async def get_blocked_history():
    history = bm.get_blocked_history()
    return {"chain": history, "count": len(history)}

# Serve all static files (HTML, CSS) from the frontend folder
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
