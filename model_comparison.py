import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.impute import SimpleImputer
import joblib

plt.style.use('default')
sns.set_theme(style="whitegrid")

# 1. LOAD RAW DATASET 
df = pd.read_csv('raw_user_behavior_dataset.csv')

# 2. DATA PREPROCESSING
# A. Handling Missing Values (Imputation)
# We use the Median because it is robust to outliers.
imputer = SimpleImputer(strategy='median')
num_cols = df.columns.drop('is_suspicious')
df[num_cols] = imputer.fit_transform(df[num_cols])
# print       ----  Imputation Complete: All NULL values resolved.")

# 2. Outlier Detection and Capping (IQR Method)
# print("Detecting and Clipping Outliers using IQR Method...")

for col in ['transaction_amount', 'time_spent']:
    # IQR calculation
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # Capping outliers to boundaries
    df[col] = np.clip(df[col], lower_bound, upper_bound)

# print(f"Outlier Handling Complete: Extreme values capped to {upper_bound:.2f}")
# print("Data Preprocessing Phase: SUCCESS\n")

# Save Preprocessing Tools for API
joblib.dump(imputer, 'imputer.pkl')

# 3. SPLIT AND SCALE
X = df.drop('is_suspicious', axis=1)
y = df['is_suspicious']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
joblib.dump(scaler, 'scaler.pkl')

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
import joblib

# ... [Steps 1-3 remain same] ...

# 4. MODEL COMPARISON
# Step 4: Benchmarking 4 Modern ML Models with Multi-Metric Evaluation...
# print("Step 4: Benchmarking 4 Modern ML Models with Multi-Metric Evaluation...")

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
    "XGBoost": XGBClassifier(n_estimators=50, max_depth=4, eval_metric='logloss', random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
}

# Results storage for multiple metrics
results_data = []
detailed_reports = {}
best_acc = 0
best_model_name = ""

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    
    # Calculate all metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    results_data.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1-Score": f1
    })
    
    detailed_reports[name] = {
        "acc": acc,
        "report": classification_report(y_test, y_pred)
    }
    
    print(f"Model: {name} | Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f}")
    
    if acc > best_acc:
        best_acc = acc
        best_model_name = name
        joblib.dump(model, 'best_model.pkl')


print(f"\nFinal Selection: {best_model_name} (Accuracy: {best_acc:.4f})\n")

# 5. VISUALIZATION - MULTI-METRIC COMPARISON
# Convert results to DataFrame for easier plotting
results_df = pd.DataFrame(results_data)
results_df_melted = results_df.melt(id_vars="Model", var_name="Metric", value_name="Score")

plt.figure(figsize=(12, 7))
sns.barplot(data=results_df_melted, x="Model", y="Score", hue="Metric", palette="magma")

plt.title('Cognitive AI Firewall - Comprehensive Performance Benchmarks', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Metric Score (0 to 1)', fontsize=12)
plt.xlabel('Machine Learning Model', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.ylim(0.7, 1.05)
plt.grid(axis='y', alpha=0.2)

# Add value labels on top of bars
for p in plt.gca().patches:
    if p.get_height() > 0:
        plt.gca().annotate(f'{p.get_height():.2f}', 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 9), 
                       textcoords='offset points',
                       fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('model_comparison_results.png', dpi=300)
# print("Comparison chart (All Metrics) saved as 'model_comparison_results.png'.")

# B & C. Visualizations for ALL Models
print("Generating Confusion Matrices and Feature Importance charts for all models...")

for name, model in models.items():
    clean_name = name.replace(" ", "_").lower()
    
    # Heatmap setup
    y_pred = model.predict(X_test_scaled)
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix: {name}')
    plt.ylabel('Actual Behavior (0=Safe, 1=Threat)')
    plt.xlabel('AI Predicted Behavior')
    plt.savefig(f'confusion_matrix_{clean_name}.png')
    plt.close() # Close to prevent memory leak
    
    # Feature Importance setup (Only models that support it)
    if hasattr(model, 'feature_importances_'):
        plt.figure(figsize=(10, 6))
        importances = model.feature_importances_
        indices = np.argsort(importances)
        plt.barh(range(len(indices)), importances[indices], color='#2ed573')
        plt.yticks(range(len(indices)), [X.columns[i].replace('_', ' ').title() for i in indices])
        plt.title(f'{name} - Risk Feature Prioritization')
        plt.xlabel('Statistical Weighting')
        plt.tight_layout()
        plt.savefig(f'feature_importance_{clean_name}.png')
        plt.close()

# Final Print to match requested format for each model
print("\n" + "="*50)
for name, data in detailed_reports.items():
    if name == best_model_name:
        print(f"Best Model: {name} with Accuracy {data['acc']:.4f}")
        print("Comparison chart saved as 'model_comparison_results.png'.\n")
        print(f"Classification Report for Best Model:")
        print(data['report'])
    else:
        print(f"Model: {name} with Accuracy {data['acc']:.4f}")
        print("Comparison chart saved as 'model_comparison_results.png'.\n")
        print(f"Classification Report for {name}:")
        print(data['report'])
