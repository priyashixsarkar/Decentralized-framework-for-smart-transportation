import joblib
import numpy as np

print("="*50)
print(" INITIATING COGNITIVE FIREWALL AI ENGINE...")
print("="*50)

# 1. Load the trained AI brain and the scaler
print("[SYSTEM] Loading Random Forest Model and Scaler...")
model = joblib.load('best_model.pkl')
scaler = joblib.load('scaler.pkl')
print("[SYSTEM] Cognitive Firewall is Online!\n")

# 2. Define a "Fake" User Login to test the firewall
# Order: [login_hour, login_frequency, location_id, device_id, transaction_amount, time_spent, failed_attempts]
print(" Intercepting Incoming Transaction Request...")

# Test Case 1: A completely normal user
test_data_safe = np.array([[14, 2, 10, 4, 350.0, 120.0, 0]])

# Test Case 2: A suspicious hacker (Logged in at 3 AM, 20 failed attempts, trying to book a $5,000 extreme ticket instantly)
test_data_hacker = np.array([[3, 1, 10, 4, 5000.0, 5.0, 20]])

# --- CHOOSE WHICH ONE TO TEST HERE ---
data_to_test = test_data_hacker  # Change to test_data_safe to test a good user!

# 3. Process data through the AI
print(" Scanning Data vectors through AI Model...\n")
scaled_data = scaler.transform(data_to_test)
verdict = model.predict(scaled_data)[0]
risk_percentage = model.predict_proba(scaled_data)[0][1] * 100

# 4. Enforce the ruling
print("="*50)
if verdict == 1:
    print(f" ALERT! MALICIOUS ACTIVITY DETECTED.")
    print(f"   Risk Score: {risk_percentage:.2f}%")
    print(f"   Action: Transaction Blocked. User isolated from system.")
else:
    print(f" VERDICT: SAFE.")
    print(f"   Risk Score: {risk_percentage:.2f}%")
    print(f"   Action: User allowed to proceed to Blockchain Booking.")
print("="*50)
