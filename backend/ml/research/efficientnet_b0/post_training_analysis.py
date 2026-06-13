"""
Post-Training Analysis Script for EfficientNet-B0
==================================================
Run AFTER training completes. Loads the saved best model and generates:
  1. misclassification_analysis.csv
  2. classwise_accuracy_barplot.png
  3. top_confusion_pairs.csv
  4. research_summary.md

Does NOT retrain or modify any model weights.
"""
import os
import json
import time
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from torchvision import transforms, datasets, models
from torch.utils.data import DataLoader
from torchvision.models import efficientnet_b0
from sklearn.metrics import confusion_matrix

# ── Paths ──
base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "..", "..", "DATASET", "DISEASE DETECTION", "Disease_Dataset_Final"))
test_dir = os.path.join(dataset_dir, "test")

models_dir = os.path.join(base_dir, "models")
metrics_dir = os.path.join(base_dir, "metrics")
plots_dir = os.path.join(base_dir, "plots")
preds_dir = os.path.join(base_dir, "predictions")

model_path = os.path.join(models_dir, "efficientnet_b0_best.pth")
mapping_path = os.path.join(models_dir, "class_mapping.json")
metrics_path = os.path.join(metrics_dir, "metrics.json")
dataset_summary_path = os.path.join(metrics_dir, "dataset_summary.json")
comparison_path = os.path.join(base_dir, "comparison_summary.json")

resnet_metrics_path = os.path.abspath(os.path.join(base_dir, "..", "..", "results", "disease_v2", "disease_metrics.json"))
resnet_report_path = os.path.abspath(os.path.join(base_dir, "..", "..", "results", "disease_v2", "classification_report.txt"))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
image_size = 224
batch_size = 16


def load_model(class_names):
    model = efficientnet_b0(weights=None)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, len(class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model


def generate_misclassification_analysis(model, dataloader, class_names):
    """Generate misclassification_analysis.csv with image path, actual, predicted, confidence."""
    print("Generating misclassification analysis...")
    
    misclassified = []
    correct_samples = []
    
    dataset = dataloader.dataset
    idx = 0
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            confidences, preds = torch.max(probs, 1)
            
            for i in range(len(labels)):
                img_path = dataset.samples[idx][0]
                img_basename = os.path.basename(img_path)
                actual = class_names[labels[i].item()]
                predicted = class_names[preds[i].item()]
                confidence = confidences[i].item()
                
                if labels[i].item() != preds[i].item():
                    misclassified.append({
                        "Image": img_basename,
                        "Actual_Class": actual,
                        "Predicted_Class": predicted,
                        "Confidence": round(confidence, 4)
                    })
                else:
                    if len(correct_samples) < 50:
                        correct_samples.append({
                            "Image": img_basename,
                            "Actual_Class": actual,
                            "Predicted_Class": predicted,
                            "Confidence": round(confidence, 4)
                        })
                idx += 1
    
    df_mis = pd.DataFrame(misclassified)
    df_mis = df_mis.sort_values("Confidence", ascending=True)
    df_mis.to_csv(os.path.join(preds_dir, "misclassification_analysis.csv"), index=False)
    print(f"  Saved {len(misclassified)} misclassified samples.")
    
    df_correct = pd.DataFrame(correct_samples)
    df_correct.to_csv(os.path.join(preds_dir, "correct_predictions_sample.csv"), index=False)
    print(f"  Saved {len(correct_samples)} correct prediction samples.")
    
    return len(misclassified)


def generate_classwise_accuracy(model, dataloader, class_names):
    """Generate per-class accuracy bar plot and CSV."""
    print("Generating classwise accuracy bar plot...")
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    per_class_acc = []
    for i, cls in enumerate(class_names):
        mask = all_labels == i
        if mask.sum() == 0:
            per_class_acc.append({"Class": cls, "Accuracy": 0.0, "Support": 0})
        else:
            acc = (all_preds[mask] == i).sum() / mask.sum()
            per_class_acc.append({"Class": cls, "Accuracy": round(float(acc), 4), "Support": int(mask.sum())})
    
    df = pd.DataFrame(per_class_acc).sort_values("Accuracy", ascending=True)
    df.to_csv(os.path.join(metrics_dir, "per_class_metrics.csv"), index=False)
    
    # Publication-quality horizontal bar plot
    fig, ax = plt.subplots(figsize=(12, max(10, len(class_names) * 0.35)))
    colors = ['#e74c3c' if a < 0.90 else '#f39c12' if a < 0.95 else '#2ecc71' for a in df['Accuracy']]
    ax.barh(df['Class'], df['Accuracy'], color=colors, edgecolor='white', linewidth=0.5)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel('Accuracy', fontsize=13, fontweight='bold')
    ax.set_title('EfficientNet-B0: Per-Class Test Accuracy', fontsize=16, fontweight='bold')
    ax.axvline(x=0.95, color='gray', linestyle='--', alpha=0.5, label='95% threshold')
    ax.legend(loc='lower right')
    for i, (acc, cls) in enumerate(zip(df['Accuracy'], df['Class'])):
        ax.text(acc + 0.005, i, f'{acc:.1%}', va='center', fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "classwise_accuracy_barplot.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved classwise_accuracy_barplot.png")
    
    return df


def generate_top_confusion_pairs(model, dataloader, class_names, top_n=15):
    """Generate top_confusion_pairs.csv from the confusion matrix."""
    print("Generating top confusion pairs...")
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    cm = confusion_matrix(all_labels, all_preds)
    
    # Extract off-diagonal entries
    pairs = []
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if i != j and cm[i][j] > 0:
                pairs.append({
                    "Actual": class_names[i],
                    "Predicted": class_names[j],
                    "Count": int(cm[i][j])
                })
    
    df = pd.DataFrame(pairs).sort_values("Count", ascending=False).head(top_n)
    df.to_csv(os.path.join(preds_dir, "top_confusion_pairs.csv"), index=False)
    print(f"  Saved top {top_n} confusion pairs.")
    return df


def generate_research_summary():
    """Generate research_summary.md with all experiment metadata."""
    print("Generating research summary...")
    
    # Load all available metrics
    eff_metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            eff_metrics = json.load(f)
    
    dataset_stats = {}
    if os.path.exists(dataset_summary_path):
        with open(dataset_summary_path, 'r') as f:
            dataset_stats = json.load(f)
    
    comparison = {}
    if os.path.exists(comparison_path):
        with open(comparison_path, 'r') as f:
            comparison = json.load(f)
    
    resnet_metrics = {}
    if os.path.exists(resnet_metrics_path):
        with open(resnet_metrics_path, 'r') as f:
            resnet_metrics = json.load(f)
    
    # Format training time
    train_secs = eff_metrics.get("Training_Time_Seconds", 0)
    train_mins = train_secs / 60
    train_hrs = train_secs / 3600
    
    resnet_secs = resnet_metrics.get("Training_Time_Seconds", 0)
    resnet_mins = resnet_secs / 60
    
    md = f"""# Research Experiment Summary
## EfficientNet-B0 vs ResNet50 for Plant Disease Detection

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Device**: {device} ({'CUDA: ' + torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})

---

## Dataset Statistics

| Split | Images |
|-------|--------|
| Train | {dataset_stats.get('train_total', 'N/A')} |
| Validation | {dataset_stats.get('valid_total', 'N/A')} |
| Test | {dataset_stats.get('test_total', 'N/A')} |
| **Total** | **{sum(v for k,v in dataset_stats.items() if isinstance(v, int))}** |
| Classes | {eff_metrics.get('Number_Of_Classes', 'N/A')} |

---

## Training Configuration

| Parameter | EfficientNet-B0 | ResNet50 |
|-----------|-----------------|----------|
| Architecture | EfficientNet-B0 | ResNet50 |
| Pretrained | ImageNet | ImageNet |
| Optimizer | Adam | Adam |
| Initial LR | 0.001 | 0.0001 |
| LR Scheduler | ReduceLROnPlateau | StepLR |
| Early Stopping | Yes (patience=3) | No (fixed 10 epochs) |
| Batch Size | 16 | 16 |
| Image Size | 224×224 | 224×224 |

---

## Training Results

| Metric | EfficientNet-B0 | ResNet50 |
|--------|-----------------|----------|
| Epochs Trained | {eff_metrics.get('Epochs_Trained', 'N/A')} | 10 |
| Training Time | {train_mins:.1f} min | {resnet_mins:.1f} min |

---

## Test Set Metrics

| Metric | EfficientNet-B0 | ResNet50 |
|--------|-----------------|----------|
| **Accuracy** | **{eff_metrics.get('Accuracy', 0):.4f}** | **{resnet_metrics.get('Test_Accuracy', 0):.4f}** |
| Top-5 Accuracy | {eff_metrics.get('Top_5_Accuracy', 0):.4f} | N/A |
| Precision (macro) | {eff_metrics.get('Precision', 0):.4f} | 0.9500 |
| Recall (macro) | {eff_metrics.get('Recall', 0):.4f} | 0.9500 |
| F1 Score (macro) | {eff_metrics.get('F1', 0):.4f} | 0.9500 |
| Cohen's Kappa | {eff_metrics.get('Cohen_Kappa', 0):.4f} | N/A |
| MCC | {eff_metrics.get('MCC', 0):.4f} | N/A |
| ROC-AUC (macro) | {eff_metrics.get('ROC_AUC_Macro', 0):.4f} | N/A |
| ROC-AUC (weighted) | {eff_metrics.get('ROC_AUC_Weighted', 0):.4f} | N/A |

---

## Resource Comparison

| Resource | EfficientNet-B0 | ResNet50 |
|----------|-----------------|----------|
| Parameters | {eff_metrics.get('Parameters', 0):,} | ~23,508,000 |
| Model Size | {eff_metrics.get('Model_Size_MB', 0):.2f} MB | {resnet_metrics.get('Final_Model_Size_MB', 90):.2f} MB |
| Training Time | {train_mins:.1f} min | {resnet_mins:.1f} min |
| Inference/Image | {eff_metrics.get('Inference_Time_Per_Image_Seconds', 0)*1000:.2f} ms | N/A |

---

## Generated Artifacts

### Models
- `models/efficientnet_b0_best.pth`
- `models/class_mapping.json`

### Metrics
- `metrics/metrics.json`
- `metrics/classification_report.csv`
- `metrics/per_class_metrics.csv`
- `metrics/dataset_summary.json`
- `metrics/class_distribution.csv`

### Plots
- `plots/loss_curve.png`
- `plots/accuracy_curve.png`
- `plots/confusion_matrix.png`
- `plots/classwise_accuracy_barplot.png`

### Predictions
- `predictions/misclassification_analysis.csv`
- `predictions/correct_predictions_sample.csv`
- `predictions/top_confusion_pairs.csv`

### Explainability
- `gradcam/` (Grad-CAM heatmap visualizations)

### Comparison
- `comparison_summary.json`
- `comparison_summary.csv`

---

## Statistical Comparison (with Difference)

| Metric | ResNet50 | EfficientNet-B0 | Difference |
|--------|----------|-----------------|------------|
| Accuracy | {resnet_metrics.get('Test_Accuracy', 0):.4f} | {eff_metrics.get('Accuracy', 0):.4f} | {eff_metrics.get('Accuracy', 0) - resnet_metrics.get('Test_Accuracy', 0):+.4f} |
| Precision | 0.9500 | {eff_metrics.get('Precision', 0):.4f} | {eff_metrics.get('Precision', 0) - 0.95:+.4f} |
| Recall | 0.9500 | {eff_metrics.get('Recall', 0):.4f} | {eff_metrics.get('Recall', 0) - 0.95:+.4f} |
| F1 | 0.9500 | {eff_metrics.get('F1', 0):.4f} | {eff_metrics.get('F1', 0) - 0.95:+.4f} |
| Cohen's Kappa | N/A | {eff_metrics.get('Cohen_Kappa', 0):.4f} | — |
| MCC | N/A | {eff_metrics.get('MCC', 0):.4f} | — |

---

## Parameter Efficiency

| Architecture | Accuracy | Parameters | Acc / Million Params |
|-------------|----------|------------|----------------------|
| ResNet50 | {resnet_metrics.get('Test_Accuracy', 0):.4f} | ~23.5M | {resnet_metrics.get('Test_Accuracy', 0) / 23.5:.4f} |
| EfficientNet-B0 | {eff_metrics.get('Accuracy', 0):.4f} | {eff_metrics.get('Parameters', 0) / 1e6:.1f}M | {eff_metrics.get('Accuracy', 0) / (eff_metrics.get('Parameters', 1) / 1e6):.4f} |

> **Efficiency Ratio**: EfficientNet-B0 achieves {eff_metrics.get('Accuracy', 0) / (eff_metrics.get('Parameters', 1) / 1e6) / (resnet_metrics.get('Test_Accuracy', 0.96) / 23.5):.1f}x the accuracy-per-parameter of ResNet50.

---

## Notes

- The ResNet50 model was trained with a fixed 10-epoch schedule; EfficientNet-B0 used early stopping.
- ResNet50 macro precision/recall/F1 values are taken from the classification report (0.95 macro avg).
- Cohen's Kappa, MCC, and ROC-AUC were not computed for ResNet50 during original training.
- All plots saved at 300 DPI for IEEE publication quality.
"""
    
    with open(os.path.join(base_dir, "research_summary.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print("  Saved research_summary.md")


def main():
    # Verify model exists
    if not os.path.exists(model_path):
        print(f"ERROR: Model not found at {model_path}")
        print("Training must complete before running post-processing.")
        return
    
    # Load class names
    with open(mapping_path, 'r') as f:
        class_names = json.load(f)
    print(f"Loaded {len(class_names)} classes.")
    
    # Load model
    model = load_model(class_names)
    print(f"Model loaded from {model_path}")
    
    # Prepare test dataloader
    test_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    test_dataset = datasets.ImageFolder(test_dir, test_transforms)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    
    print(f"Test set: {len(test_dataset)} images\n")
    
    # 1. Misclassification analysis
    num_mis = generate_misclassification_analysis(model, test_loader, class_names)
    
    # 2. Classwise accuracy bar plot + per_class_metrics.csv
    classwise_df = generate_classwise_accuracy(model, test_loader, class_names)
    
    # 3. Top confusion pairs
    confusion_df = generate_top_confusion_pairs(model, test_loader, class_names)
    
    # 4. Research summary
    generate_research_summary()
    
    print("\n" + "=" * 60)
    print("  Post-processing complete!")
    print("=" * 60)
    print(f"\n  Misclassified samples: {num_mis}")
    print(f"\n  Top confusion pairs:")
    print(confusion_df.to_string(index=False))
    print(f"\n  Lowest accuracy classes:")
    print(classwise_df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
