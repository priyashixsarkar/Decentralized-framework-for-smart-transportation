from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
from pydantic import BaseModel
import time
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
model = joblib.load('best_model.pkl')
scaler = joblib.load('scaler.pkl')
bm = BlockchainManager()

class UserBehavior(BaseModel):
    user_id: str
    login_hour: int
    login_frequency: int
    location_id: int
    device_id: int
    transaction_amount: float
    time_spent: float
    failed_attempts: int

class BookingRequest(BaseModel):
    user_id: str
    source: str
    destination: str
    amount: float
    
@app.get("/")
def home():
    return {"message": "Secure AI-Blockchain Ticketing System API"}

@app.post("/firewall/analyze")
async def analyze_behavior(behavior: UserBehavior):
    # Prepare data for prediction
    features = np.array([[
        behavior.login_hour,
        behavior.login_frequency,
        behavior.location_id,
        behavior.device_id,
        behavior.transaction_amount,
        behavior.time_spent,
        behavior.failed_attempts
    ]])
    
    scaled_features = scaler.transform(features)
    prediction = model.predict(scaled_features)[0]
    probability = model.predict_proba(scaled_features)[0][1] # Prob of being suspicious
    
    status = "Suspicious" if prediction == 1 else "Safe"
    
    return {
        "user_id": behavior.user_id,
        "status": status,
        "risk_score": round(float(probability) * 100, 2),
        "timestamp": time.time()
    }

@app.post("/login")
async def secure_login(behavior: UserBehavior):
    # 1. COGNITIVE FIREWALL CHECK
    features = np.array([[
        behavior.login_hour, behavior.login_frequency, behavior.location_id,
        behavior.device_id, behavior.transaction_amount, behavior.time_spent, behavior.failed_attempts
    ]])
    scaled_features = scaler.transform(features)
    prediction = model.predict(scaled_features)[0]
    risk_percentage = model.predict_proba(scaled_features)[0][1] * 100
    
    if prediction == 1:
        # 1.1 Store the malicious attempt in the Blocked Blockchain
        tx_data = {
            "type": "MALICIOUS_LOGIN_BLOCKED",
            "location_id": behavior.location_id,
            "device_id": behavior.device_id,
            "timestamp": time.time()
        }
        bm.record_blocked_transaction(behavior.user_id, tx_data)
        
        # 1.2 Firewall completely blocks the login process
        raise HTTPException(status_code=403, detail=f"Malicious activity detected! AI Risk Score: {risk_percentage:.2f}%. Login Blocked.")
    
    # 2. SUCCESSFUL LOGIN -> BLOCKCHAIN STORAGE (User Chain & Global Chain)
    tx_data = {
        "type": "USER_LOGIN_SUCCESS",
        "location_id": behavior.location_id,
        "device_id": behavior.device_id,
        "timestamp": time.time()
    }
    
    # bm.record_transaction automatically creates 1 log for the specific user and 1 log for the global chain
    result = bm.record_transaction(behavior.user_id, tx_data)
    
    return {
        "message": f"Login Successful. AI Risk Score: {risk_percentage:.2f}% (Passed Cognitive Firewall).",
        "blockchain_status": f"Login event permanently logged on the Global Blockchain and {behavior.user_id}'s personal Blockchain.",
        "transaction_details": tx_data
    }


@app.post("/book")
async def book_ticket(request: BookingRequest):
    # In a real app, we'd run the firewall check here too.
    # For this demo, we'll record the booking on both blockchains.
    
    tx_data = {
        "type": "TICKET_BOOKING",
        "source": request.source,
        "destination": request.destination,
        "amount": request.amount,
        "timestamp": time.time()
    }
    
    result = bm.record_transaction(request.user_id, tx_data)
    
    return {
        "message": "Ticket booked successfully",
        "blockchain_status": "Recorded on User and Global Chains",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
