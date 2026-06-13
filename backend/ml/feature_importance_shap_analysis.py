"""
═══════════════════════════════════════════════════════════════════
 SHADOW GARDEN — Feature Importance & SHAP Analysis
 Generates:
   1. Top-10 Feature Importance bar plots (Crop & Fertilizer)
   2. SHAP summary bee-swarm plots (Crop & Fertilizer)
   3. SHAP waterfall plots for 20 sample predictions each
   4. CSV reports with exact feature importance values
═══════════════════════════════════════════════════════════════════
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns

# Try importing SHAP
try:
    import shap
    HAS_SHAP = True
    print("[OK] SHAP library found.")
except ImportError:
    HAS_SHAP = False
    print("[WARN] SHAP not installed. Run: pip install shap")
    print("       Skipping SHAP analysis, but feature importance plots will still be generated.")

# ─── Configuration ───────────────────────────────────────────────
MODEL_DIR = "models"
OUTPUT_DIR = "results/feature_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Premium plot styling
plt.rcParams.update({
    'figure.facecolor': '#0f1117',
    'axes.facecolor': '#1a1c2e',
    'axes.edgecolor': '#3d3f5a',
    'axes.labelcolor': '#c4c7d4',
    'text.color': '#e0e3ed',
    'xtick.color': '#a0a3b5',
    'ytick.color': '#a0a3b5',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.dpi': 150,
})

# Custom color palette (fantasy theme)
GRADIENT_COLORS = ['#22d3ee', '#6366f1', '#8b5cf6', '#a855f7', '#c084fc', '#d946ef', '#ec4899', '#f43f5e', '#fb923c', '#facc15']

# ═══════════════════════════════════════════════════════════════
#  SECTION 1: CROP MODEL ANALYSIS
# ═══════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("  CROP MODEL — Feature Importance Analysis")
print("═" * 60)

# Load crop model and data
crop_model = joblib.load(os.path.join(MODEL_DIR, "crop_model.pkl"))
crop_encoders = joblib.load(os.path.join(MODEL_DIR, "crop_encoders.pkl"))

with open(os.path.join(MODEL_DIR, "crop_features.json")) as f:
    crop_feature_names = json.load(f)["features"]

print(f"  Model type: {type(crop_model).__name__}")
print(f"  Features: {crop_feature_names}")

# Load crop dataset for SHAP
crop_df = pd.read_csv("../../DATASET/COP RECCOMENDATION/Crop_recommendation.csv")
crop_df.dropna(inplace=True)
X_crop = crop_df[crop_feature_names]

# ─── 1A: Feature Importance Bar Plot (Top 10) ────────────────

if hasattr(crop_model, 'feature_importances_'):
    importances = crop_model.feature_importances_
    fi_df = pd.DataFrame({
        'Feature': crop_feature_names,
        'Importance': importances
    }).sort_values('Importance', ascending=True)
    
    # Save CSV
    fi_df.sort_values('Importance', ascending=False).to_csv(
        os.path.join(OUTPUT_DIR, "crop_feature_importance.csv"), index=False
    )
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    top10 = fi_df.tail(10)
    colors = GRADIENT_COLORS[:len(top10)]
    bars = ax.barh(top10['Feature'], top10['Importance'], color=colors, edgecolor='#2d2f45', linewidth=0.5)
    
    # Add value labels on bars
    for bar, val in zip(bars, top10['Importance']):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9, color='#c4c7d4')
    
    ax.set_xlabel('Importance Score (Gini / Gain)')
    ax.set_title('🌾 CROP MODEL — Top 10 Feature Importances')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "crop_feature_importance_top10.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Crop feature importance plot saved.")
    
    # Print ranking
    print("\n  Crop Feature Ranking:")
    for _, row in fi_df.sort_values('Importance', ascending=False).iterrows():
        bar = "█" * int(row['Importance'] * 50)
        print(f"    {row['Feature']:>15s}  {row['Importance']:.4f}  {bar}")
else:
    print("  [WARN] Crop model does not have feature_importances_ attribute.")

# ─── 1B: SHAP Analysis for Crop Model ────────────────────────

if HAS_SHAP:
    print("\n  Computing SHAP values for Crop model (this may take a minute)...")
    
    # Use a background sample for efficiency
    background = shap.sample(X_crop, 100, random_state=42)
    
    # Use TreeExplainer for tree-based models (RF, XGBoost)
    if hasattr(crop_model, 'estimators_') or 'XGB' in type(crop_model).__name__:
        explainer = shap.TreeExplainer(crop_model, data=background)
    else:
        explainer = shap.KernelExplainer(crop_model.predict_proba, background)
    
    # Compute SHAP for 200 samples (for summary plot) and 20 samples (for waterfall)
    sample_200 = X_crop.sample(n=min(200, len(X_crop)), random_state=42)
    shap_values_200 = explainer.shap_values(sample_200)
    
    # SHAP Summary Bar Plot (manual to avoid SHAP 0.49 color bug)
    if isinstance(shap_values_200, list):
        # List of arrays (one per class). Compute mean across samples and then across classes
        shap_mean = np.mean(np.abs(np.array(shap_values_200)), axis=(0, 1))
    else:
        # Depending on SHAP version, it might have a .values attribute
        vals = shap_values_200.values if hasattr(shap_values_200, 'values') else shap_values_200
        # For multi-class (samples, features, classes)
        if len(vals.shape) == 3:
            shap_mean = np.mean(np.abs(vals), axis=(0, 2))
        else:
            shap_mean = np.mean(np.abs(vals), axis=0)
    
    shap_df = pd.DataFrame({
        'Feature': crop_feature_names,
        'Mean |SHAP|': shap_mean
    }).sort_values('Mean |SHAP|', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(shap_df['Feature'], shap_df['Mean |SHAP|'], 
                   color=GRADIENT_COLORS[:len(shap_df)], edgecolor='#2d2f45', linewidth=0.5)
    for bar, val in zip(bars, shap_df['Mean |SHAP|']):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9, color='#c4c7d4')
    ax.set_xlabel('Mean |SHAP Value|')
    ax.set_title('CROP MODEL - SHAP Feature Impact (Mean Absolute)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "crop_shap_summary.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save SHAP values CSV
    shap_df.sort_values('Mean |SHAP|', ascending=False).to_csv(
        os.path.join(OUTPUT_DIR, "crop_shap_importance.csv"), index=False
    )
    print("  [OK] Crop SHAP summary plot saved.")
    
    print("\n  Crop SHAP Ranking:")
    for _, row in shap_df.sort_values('Mean |SHAP|', ascending=False).iterrows():
        bar_str = "#" * int(row['Mean |SHAP|'] * 100)
        print(f"    {row['Feature']:>15s}  {row['Mean |SHAP|']:.4f}  {bar_str}")
    
    # SHAP Waterfall Plots for 20 individual predictions
    sample_20 = X_crop.sample(n=20, random_state=123)
    shap_values_20 = explainer.shap_values(sample_20)
    
    crop_le = crop_encoders.get("Crop Type", crop_encoders.get("label", None))
    predictions_20 = crop_model.predict(sample_20)
    
    waterfall_dir = os.path.join(OUTPUT_DIR, "crop_shap_waterfall")
    os.makedirs(waterfall_dir, exist_ok=True)
    
    for idx in range(20):
        try:
            pred_class = predictions_20[idx]
            pred_label = crop_le.inverse_transform([pred_class])[0] if crop_le else str(pred_class)
            
            if hasattr(shap_values_20, 'values'):
                # SHAP Explanation object
                # Some versions return list of Explanations, some return 3D arrays
                if isinstance(shap_values_20, list):
                    exp = shap_values_20[pred_class][idx]
                elif len(shap_values_20.shape) == 3:
                    exp = shap_values_20[idx, :, pred_class]
                else:
                    exp = shap_values_20[idx]
                
                fig, ax = plt.subplots(figsize=(10, 5))
                shap.plots.waterfall(exp, show=False)
            else:
                # Legacy array list
                sv = shap_values_20[pred_class][idx] if isinstance(shap_values_20, list) else shap_values_20[idx]
                bv = explainer.expected_value[pred_class] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
                exp = shap.Explanation(values=sv, base_values=bv, data=sample_20.iloc[idx].values, feature_names=crop_feature_names)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                shap.plots.waterfall(exp, show=False)
            plt.title(f'Crop Sample {idx+1} → Predicted: {pred_label}', fontsize=12, color='#e0e3ed')
            plt.tight_layout()
            plt.savefig(os.path.join(waterfall_dir, f"sample_{idx+1}_{pred_label}.png"),
                       dpi=200, bbox_inches='tight', facecolor='#0f1117')
            plt.close()
        except Exception as e:
            print(f"    [WARN] Waterfall {idx+1} failed: {e}")
    
    print(f"  ✅ 20 Crop SHAP waterfall plots saved to {waterfall_dir}/")


# ═══════════════════════════════════════════════════════════════
#  SECTION 2: FERTILIZER MODEL ANALYSIS
# ═══════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("  FERTILIZER MODEL — Feature Importance Analysis")
print("═" * 60)

# Load fertilizer model and data
fert_model = joblib.load(os.path.join(MODEL_DIR, "fertilizer_model.pkl"))
fert_encoders = joblib.load(os.path.join(MODEL_DIR, "fertilizer_encoders.pkl"))

with open(os.path.join(MODEL_DIR, "fertilizer_features.json")) as f:
    fert_feature_names = json.load(f)["features"]

print(f"  Model type: {type(fert_model).__name__}")
print(f"  Features: {fert_feature_names}")

# Load fertilizer dataset
fert_df = pd.read_csv("../../DATASET/FERTILIZER RECCOMENDATION/Fertilizer Prediction.csv")
fert_df.columns = fert_df.columns.str.strip()
fert_df.dropna(inplace=True)

# Encode categorical features using saved encoders
for col in ['Soil Type', 'Crop Type']:
    if col in fert_encoders:
        fert_df[col] = fert_encoders[col].transform(fert_df[col])

X_fert = fert_df[fert_feature_names]

# ─── 2A: Feature Importance Bar Plot (Top 10) ────────────────

if hasattr(fert_model, 'feature_importances_'):
    importances_f = fert_model.feature_importances_
    fi_df_f = pd.DataFrame({
        'Feature': fert_feature_names,
        'Importance': importances_f
    }).sort_values('Importance', ascending=True)
    
    # Save CSV
    fi_df_f.sort_values('Importance', ascending=False).to_csv(
        os.path.join(OUTPUT_DIR, "fertilizer_feature_importance.csv"), index=False
    )
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    top10_f = fi_df_f.tail(10)
    colors_f = GRADIENT_COLORS[:len(top10_f)]
    bars_f = ax.barh(top10_f['Feature'], top10_f['Importance'], color=colors_f, edgecolor='#2d2f45', linewidth=0.5)
    
    for bar, val in zip(bars_f, top10_f['Importance']):
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9, color='#c4c7d4')
    
    ax.set_xlabel('Importance Score (Gini / Gain)')
    ax.set_title('🧪 FERTILIZER MODEL — Top 10 Feature Importances')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fertilizer_feature_importance_top10.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✅ Fertilizer feature importance plot saved.")
    
    # Print ranking
    print("\n  Fertilizer Feature Ranking:")
    for _, row in fi_df_f.sort_values('Importance', ascending=False).iterrows():
        bar = "█" * int(row['Importance'] * 50)
        print(f"    {row['Feature']:>15s}  {row['Importance']:.4f}  {bar}")
else:
    print("  [WARN] Fertilizer model does not have feature_importances_ attribute.")

# ─── 2B: SHAP Analysis for Fertilizer Model ──────────────────

if HAS_SHAP:
    print("\n  Computing SHAP values for Fertilizer model...")
    
    background_f = shap.sample(X_fert, 100, random_state=42)
    
    # Use KernelExplainer for XGBoost to avoid base_score string parsing bug in TreeExplainer
    if hasattr(fert_model, 'estimators_') and 'XGB' not in type(fert_model).__name__:
        explainer_f = shap.TreeExplainer(fert_model, data=background_f)
    else:
        # Wrapper function avoids SHAP monkey-patching feature_names_in_ on bound methods
        def predict_wrapper(x):
            return fert_model.predict_proba(pd.DataFrame(x, columns=fert_feature_names))
        # Use KernelExplainer for XGBoost and SVM/KNN
        explainer_f = shap.KernelExplainer(predict_wrapper, background_f)
    
    sample_200_f = X_fert.sample(n=min(200, len(X_fert)), random_state=42)
    shap_values_200_f = explainer_f.shap_values(sample_200_f)
    
    # SHAP Summary Bar Plot (manual to avoid SHAP 0.49 color bug)
    if isinstance(shap_values_200_f, list):
        shap_mean_f = np.mean(np.abs(np.array(shap_values_200_f)), axis=(0, 1))
    else:
        vals_f = shap_values_200_f.values if hasattr(shap_values_200_f, 'values') else shap_values_200_f
        if len(vals_f.shape) == 3:
            shap_mean_f = np.mean(np.abs(vals_f), axis=(0, 2))
        else:
            shap_mean_f = np.mean(np.abs(vals_f), axis=0)
    
    shap_df_f = pd.DataFrame({
        'Feature': fert_feature_names,
        'Mean |SHAP|': shap_mean_f
    }).sort_values('Mean |SHAP|', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(shap_df_f['Feature'], shap_df_f['Mean |SHAP|'], 
                   color=GRADIENT_COLORS[:len(shap_df_f)], edgecolor='#2d2f45', linewidth=0.5)
    for bar, val in zip(bars, shap_df_f['Mean |SHAP|']):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9, color='#c4c7d4')
    ax.set_xlabel('Mean |SHAP Value|')
    ax.set_title('FERTILIZER MODEL - SHAP Feature Impact (Mean Absolute)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fertilizer_shap_summary.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    shap_df_f.sort_values('Mean |SHAP|', ascending=False).to_csv(
        os.path.join(OUTPUT_DIR, "fertilizer_shap_importance.csv"), index=False
    )
    print("  [OK] Fertilizer SHAP summary plot saved.")
    
    print("\n  Fertilizer SHAP Ranking:")
    for _, row in shap_df_f.sort_values('Mean |SHAP|', ascending=False).iterrows():
        bar_str = "#" * int(row['Mean |SHAP|'] * 100)
        print(f"    {row['Feature']:>15s}  {row['Mean |SHAP|']:.4f}  {bar_str}")
    
    # SHAP Waterfall Plots for 20 individual predictions
    sample_20_f = X_fert.sample(n=20, random_state=123)
    shap_values_20_f = explainer_f.shap_values(sample_20_f)
    
    fert_le = fert_encoders.get("Fertilizer Name")
    predictions_20_f = fert_model.predict(sample_20_f)
    
    waterfall_dir_f = os.path.join(OUTPUT_DIR, "fertilizer_shap_waterfall")
    os.makedirs(waterfall_dir_f, exist_ok=True)
    
    for idx in range(20):
        try:
            pred_class = predictions_20_f[idx]
            pred_label = fert_le.inverse_transform([pred_class])[0] if fert_le else str(pred_class)
            
            if hasattr(shap_values_20_f, 'values'):
                if isinstance(shap_values_20_f, list):
                    exp_f = shap_values_20_f[pred_class][idx]
                elif len(shap_values_20_f.shape) == 3:
                    exp_f = shap_values_20_f[idx, :, pred_class]
                else:
                    exp_f = shap_values_20_f[idx]
                
                fig, ax = plt.subplots(figsize=(10, 5))
                shap.plots.waterfall(exp_f, show=False)
            else:
                sv_f = shap_values_20_f[pred_class][idx] if isinstance(shap_values_20_f, list) else shap_values_20_f[idx]
                bv_f = explainer_f.expected_value[pred_class] if isinstance(explainer_f.expected_value, (list, np.ndarray)) else explainer_f.expected_value
                exp_f = shap.Explanation(values=sv_f, base_values=bv_f, data=sample_20_f.iloc[idx].values, feature_names=fert_feature_names)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                shap.plots.waterfall(exp_f, show=False)
            plt.title(f'Fertilizer Sample {idx+1} → Predicted: {pred_label}', fontsize=12, color='#e0e3ed')
            plt.tight_layout()
            plt.savefig(os.path.join(waterfall_dir_f, f"sample_{idx+1}_{pred_label}.png"),
                       dpi=200, bbox_inches='tight', facecolor='#0f1117')
            plt.close()
        except Exception as e:
            print(f"    [WARN] Waterfall {idx+1} failed: {e}")
    
    print(f"  ✅ 20 Fertilizer SHAP waterfall plots saved to {waterfall_dir_f}/")


# ═══════════════════════════════════════════════════════════════
#  SECTION 3: COMBINED COMPARISON PLOT
# ═══════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("  Generating Combined Comparison Plot...")
print("═" * 60)

fig, axes = plt.subplots(1, 2, figsize=(18, 7))

# Crop model
if hasattr(crop_model, 'feature_importances_'):
    crop_fi = pd.DataFrame({
        'Feature': crop_feature_names,
        'Importance': crop_model.feature_importances_
    }).sort_values('Importance', ascending=True)
    
    axes[0].barh(crop_fi['Feature'], crop_fi['Importance'], 
                 color=GRADIENT_COLORS[:len(crop_fi)], edgecolor='#2d2f45')
    axes[0].set_title('🌾 Crop Model Features', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Importance Score')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

# Fertilizer model
if hasattr(fert_model, 'feature_importances_'):
    fert_fi = pd.DataFrame({
        'Feature': fert_feature_names,
        'Importance': fert_model.feature_importances_
    }).sort_values('Importance', ascending=True)
    
    axes[1].barh(fert_fi['Feature'], fert_fi['Importance'], 
                 color=GRADIENT_COLORS[:len(fert_fi)], edgecolor='#2d2f45')
    axes[1].set_title('🧪 Fertilizer Model Features', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Importance Score')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

plt.suptitle('SHADOW GARDEN — Feature Importance Comparison', fontsize=16, fontweight='bold',
             color='#22d3ee', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "combined_feature_importance.png"), dpi=300, bbox_inches='tight')
plt.close()

print("  ✅ Combined comparison plot saved.")
print("\n" + "═" * 60)
print(f"  All outputs saved to: {os.path.abspath(OUTPUT_DIR)}")
print("═" * 60)
