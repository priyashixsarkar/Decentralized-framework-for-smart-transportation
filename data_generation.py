import pandas as pd
import numpy as np
import os

def generate_unbiased_dataset(n_samples=5000):
    np.random.seed(42)
    
    # Features:
    # 1. login_hour (0-23)
    # 2. login_frequency (per day)
    # 3. location_id (proxy for geographic consistency)
    # 4. device_id (proxy for device consistency)
    # 5. transaction_amount
    # 6. time_spent_on_page (seconds)
    # 7. failed_login_attempts
    
    data = {
        'login_hour': np.random.randint(0, 24, n_samples),
        'login_frequency': np.random.randint(1, 15, n_samples),
        'location_id': np.random.randint(1, 20, n_samples),
        'device_id': np.random.randint(1, 10, n_samples),
        'transaction_amount': np.random.uniform(10, 5000, n_samples),
        'time_spent': np.random.uniform(5, 600, n_samples),
        'failed_attempts': np.random.randint(0, 10, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Logic for "Suspicious" (1) vs "Safe" (0)
    # Suspicious if:
    # - Many failed attempts (> 3)
    # - High login frequency (> 10)
    # - Unusual login hour (midnight to 4 AM) AND high amount
    # - Extremely short time spent for a high amount transaction (bot-like)
    
    df['is_suspicious'] = (
        (df['failed_attempts'] > 3) | 
        (df['login_frequency'] > 12) | 
        ((df['login_hour'] >= 0) & (df['login_hour'] <= 4) & (df['transaction_amount'] > 3000)) |
        ((df['time_spent'] < 10) & (df['transaction_amount'] > 2000))
    ).astype(int)
    
    # Add some noise to make it realistic
    noise = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
    df['is_suspicious'] = (df['is_suspicious'] ^ noise)
    
    df.to_csv('user_behavior_dataset.csv', index=False)
    print(f"Dataset generated with {n_samples} samples. Saved to 'user_behavior_dataset.csv'.")
    print(df['is_suspicious'].value_counts())

if __name__ == "__main__":
    generate_unbiased_dataset()
