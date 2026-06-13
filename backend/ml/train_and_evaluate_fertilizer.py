import pandas as pd
import numpy as np
import os
import json
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
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
RESULT_DIR = "results/fertilizer"
ensure_dir(MODEL_DIR)
ensure_dir(RESULT_DIR)

# Load dataset
df = pd.read_csv("../../DATASET/FERTILIZER RECCOMENDATION/Fertilizer Prediction.csv")
df.columns = df.columns.str.strip()
df.dropna(inplace=True)

# Encode categorical feature columns
encoders = {}
categorical_features = ['Soil Type', 'Crop Type']
for col in categorical_features:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# Features and target
feature_cols = ['Temparature', 'Humidity', 'Moisture', 'Soil Type', 'Crop Type', 'Nitrogen', 'Potassium', 'Phosphorous']
X = df[feature_cols]
y_raw = df['Fertilizer Name']

# Encode target
target_le = LabelEncoder()
y = target_le.fit_transform(y_raw)
encoders['Fertilizer Name'] = target_le

# Save feature names
features_dict = {"features": feature_cols}
with open(os.path.join(MODEL_DIR, "fertilizer_features.json"), "w") as f:
    json.dump(features_dict, f, indent=4)

# Save encoders
joblib.dump(encoders, os.path.join(MODEL_DIR, "fertilizer_encoders.pkl"))

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
best_cv = -1
best_model_name = ""
trained_models = {}

print("Training Fertilizer Recommendation Models...")
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    # 5-fold CV
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    cv_mean = cv_scores.mean()
    
    prec = precision_score(y_test, y_pred_test, average='macro', zero_division=0)
    rec = recall_score(y_test, y_pred_test, average='macro', zero_division=0)
    f1 = f1_score(y_test, y_pred_test, average='macro', zero_division=0)
    
    results.append({
        "Algorithm": name,
        "Train Accuracy": round(train_acc, 4),
        "Test Accuracy": round(test_acc, 4),
        "CV Accuracy": round(cv_mean, 4),
        "Test F1": round(f1, 4)
    })
    
    trained_models[name] = model
    
    # Select best model primarily by CV Accuracy to avoid overfitting small datasets
    if cv_mean > best_cv:
        best_cv = cv_mean
        best_model = model
        best_model_name = name

# Save comparison report
results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(RESULT_DIR, "model_comparison.csv"), index=False)
print("Model comparison saved.")
print(results_df)

# Save the best model
print(f"Best Model: {best_model_name}")
joblib.dump(best_model, os.path.join(MODEL_DIR, "fertilizer_model.pkl"))

# Generate graphs for the best model
y_pred_best = best_model.predict(X_test)

# 1. Classification Report Image
def save_classification_report_as_image(y_true, y_pred, classes, filename):
    import numpy as np
    labels = np.arange(len(classes))
    report = classification_report(y_true, y_pred, labels=labels, target_names=classes, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report).T
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(report_df.iloc[:-3, :-1], annot=True, fmt=".2f", cmap="Blues", cbar=False)
    plt.title(f"Classification Report - {best_model_name}")
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close()

save_classification_report_as_image(y_test, y_pred_best, target_le.classes_, os.path.join(RESULT_DIR, "classification_report.png"))

# 2. Confusion Matrix Image
def save_confusion_matrix_as_image(y_true, y_pred, classes, filename):
    import numpy as np
    labels = np.arange(len(classes))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=classes, yticklabels=classes)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"Confusion Matrix - {best_model_name}")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

save_confusion_matrix_as_image(y_test, y_pred_best, target_le.classes_, os.path.join(RESULT_DIR, "confusion_matrix.png"))

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

print("Fertilizer model training and evaluation complete.")
