import pandas as pd
import numpy as np
import os
import json
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Directories
MODEL_DIR = "models"
RESULT_DIR = "results/crop"
ensure_dir(MODEL_DIR)
ensure_dir(RESULT_DIR)

# Load dataset
df = pd.read_csv("../../DATASET/COP RECCOMENDATION/Crop_recommendation.csv")
df.dropna(inplace=True)

# Features and target
feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
X = df[feature_cols]
y_raw = df['label']

# Encode target for models like XGBoost that require numeric labels
le = LabelEncoder()
y = le.fit_transform(y_raw)

# Save feature names
features_dict = {"features": feature_cols}
with open(os.path.join(MODEL_DIR, "crop_features.json"), "w") as f:
    json.dump(features_dict, f, indent=4)

# Save encoder
joblib.dump({"Crop Type": le}, os.path.join(MODEL_DIR, "crop_encoders.pkl"))

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define models
models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42),
    "KNN": KNeighborsClassifier(),
    "SVM": SVC(probability=True, random_state=42)
}

results = []
best_model = None
best_f1 = -1
best_model_name = ""
trained_models = {}

print("Training Crop Recommendation Models...")
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='macro')
    rec = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    
    results.append({
        "Algorithm": name,
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1": round(f1, 4)
    })
    
    trained_models[name] = model
    
    if f1 > best_f1:
        best_f1 = f1
        best_model = model
        best_model_name = name

# Save comparison report
results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(RESULT_DIR, "model_comparison.csv"), index=False)
print("Model comparison saved.")
print(results_df)

# Save the best model
print(f"Best Model: {best_model_name}")
joblib.dump(best_model, os.path.join(MODEL_DIR, "crop_model.pkl"))

# Generate graphs for the best model
y_pred_best = best_model.predict(X_test)

# 1. Classification Report Image
def save_classification_report_as_image(y_true, y_pred, classes, filename):
    report = classification_report(y_true, y_pred, target_names=classes, output_dict=True)
    report_df = pd.DataFrame(report).T
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(report_df.iloc[:-3, :-1], annot=True, fmt=".2f", cmap="Blues", cbar=False)
    plt.title(f"Classification Report - {best_model_name}")
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close()

save_classification_report_as_image(y_test, y_pred_best, le.classes_, os.path.join(RESULT_DIR, "classification_report.png"))

# 2. Confusion Matrix Image
def save_confusion_matrix_as_image(y_true, y_pred, classes, filename):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"Confusion Matrix - {best_model_name}")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

save_confusion_matrix_as_image(y_test, y_pred_best, le.classes_, os.path.join(RESULT_DIR, "confusion_matrix.png"))

# 3. Feature Importance Plots for RF and XGBoost
def save_feature_importance_as_image(model, feature_names, title, filename):
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        plt.figure(figsize=(10, 6))
        sns.barplot(x=importances, y=feature_names, palette="viridis")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()

save_feature_importance_as_image(trained_models["Random Forest"], feature_cols, "Feature Importances - Random Forest", os.path.join(RESULT_DIR, "feature_importance_rf.png"))
save_feature_importance_as_image(trained_models["XGBoost"], feature_cols, "Feature Importances - XGBoost", os.path.join(RESULT_DIR, "feature_importance_xgb.png"))

print("Crop model training and evaluation complete.")
