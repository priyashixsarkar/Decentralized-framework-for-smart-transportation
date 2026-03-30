import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Load dataset
df = pd.read_csv('user_behavior_dataset.csv')
X = df.drop('is_suspicious', axis=1)
y = df['is_suspicious']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model definitions
models = {
    "Logistic Regression": LogisticRegression(),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
    "SVM": SVC(probability=True)
}

results = {}
best_acc = 0
best_model_name = ""

print("Comparing 4 models for the Cognitive Firewall...")

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    results[name] = acc
    
    print(f"\n==========================================")
    print(f"Evaluation Metrics for: {name}")
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))
    print(f"==========================================\n")
    
    if acc > best_acc:
        best_acc = acc
        best_model_name = name
        joblib.dump(model, 'best_model.pkl')
        joblib.dump(scaler, 'scaler.pkl')

print(f"\nBest Model: {best_model_name} with Accuracy {best_acc:.4f}")

# Visualization
plt.figure(figsize=(10,6))
sns.barplot(x=list(results.keys()), y=list(results.values()), hue=list(results.keys()), palette="viridis")
plt.title('Cognitive Firewall - Model Comparison for MCA Research')
plt.ylabel('Accuracy Score')
plt.xlabel('Algorithm')
plt.ylim(0.8, 1.0)
plt.savefig('model_comparison_results.png')
print("Comparison chart saved as 'model_comparison_results.png'.")

# Final verification of best model
best_model = joblib.load('best_model.pkl')
y_pred_best = best_model.predict(X_test_scaled)
print("\nClassification Report for Best Model:")
print(classification_report(y_test, y_pred_best))
