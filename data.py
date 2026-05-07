import pandas as pd
import numpy as np
import os

def generate_advanced_noisy_dataset(n_samples=16000):
    np.random.seed(42)
    
    # Core Features
    hours = np.random.randint(0, 24, n_samples)
    frequencies = np.random.randint(1, 30, n_samples)
    locations = np.random.randint(1, 100, n_samples)
    devices = np.random.randint(1, 20, n_samples)
    amounts = np.random.gamma(shape=2.0, scale=100.0, size=n_samples) + 10.0
    times = np.random.gamma(shape=3.0, scale=60.0, size=n_samples) + 5.0
    failures = np.random.choice([0, 1, 2, 3, 5, 10, 20], size=n_samples, p=[0.8, 0.1, 0.05, 0.02, 0.01, 0.01, 0.01])
    
    # New Features for MCA Standards
    is_vpn = np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15])
    request_rate = np.random.uniform(0.1, 15.0, n_samples)
    last_login_diff = np.random.exponential(scale=48.0, size=n_samples) # Hours since last login
    browser_id = np.random.randint(1, 6, n_samples) # 1: Chrome, 2: Safari, 3: Firefox, 4: Edge, 5: Others
    os_type = np.random.randint(0, 4, n_samples) # 0: Windows, 1: Linux, 2: Android, 3: iOS
    
    data = {
        'login_hour': hours,
        'login_frequency': frequencies,
        'location_id': locations,
        'device_id': devices,
        'transaction_amount': amounts,
        'time_spent': times,
        'failed_attempts': failures,
        'is_vpn': is_vpn,
        'request_rate': request_rate,
        'last_login_diff': last_login_diff,
        'os_type': os_type,
        'browser_id': browser_id
    }
    
    df = pd.DataFrame(data)
    
    # Logic for Suspicious behavior
    # We create a logic that the AI will learn from
    df['is_suspicious'] = (
        (df['failed_attempts'] > 5) | 
        ((df['is_vpn'] == 1) & (df['transaction_amount'] > 2000)) |
        ((df['login_hour'] < 5) & (df['request_rate'] > 10.0)) |
        (df['login_frequency'] > 25)
    ).astype(int)
    
    # Add Noise to Labels (6% flip)
    noise_idx = np.random.choice(df.index, size=int(n_samples * 0.06), replace=False)
    df.loc[noise_idx, 'is_suspicious'] = 1 - df.loc[noise_idx, 'is_suspicious']
    
    # --- DATA PREPROCESSING DEMONSTRATION: NULL INJECTION ---
    # Randomly inject NaNs (Nulls) to demonstrate Imputation skills
    cols_with_nulls = ['login_hour', 'transaction_amount', 'time_spent', 'request_rate']
    for col in cols_with_nulls:
        null_idx = np.random.choice(df.index, size=int(n_samples * 0.05), replace=False)
        df.loc[null_idx, col] = np.nan
        
    # --- NOISE INJECTION (OUTLIERS) ---
    # Add extreme outliers to 'transaction_amount' and 'time_spent'
    outlier_idx = np.random.choice(df.index, size=50, replace=False)
    df.loc[outlier_idx, 'transaction_amount'] = df.loc[outlier_idx, 'transaction_amount'] * 50 # Extreme high amount
    df.loc[outlier_idx, 'time_spent'] = -999 # Corrupt negative noise
    
    # Save Raw (Dirty) Dataset
    df.to_csv('raw_user_behavior_dataset.csv', index=False)
    
    print(f"Dataset generated: 16,000 samples.")
    print(f"Features (12): {list(df.columns)[:-1]}")
    print(f"Nulls injected in: {cols_with_nulls}")
    print(f"Outliers injected for Demonstration.")
    print(f"Target distribution:\n{df['is_suspicious'].value_counts()}")

if __name__ == "__main__":
    generate_advanced_noisy_dataset()
