# Research Experiment Summary
## EfficientNet-B0 vs ResNet50 for Plant Disease Detection

**Generated**: 2026-06-11 17:02:00
**Device**: cuda (CUDA: NVIDIA GeForce RTX 2050)

---

## Dataset Statistics

| Split | Images |
|-------|--------|
| Train | 54889 |
| Validation | 6847 |
| Test | 6898 |
| **Total** | **68634** |
| Classes | 45 |

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
| Epochs Trained | 10 | 10 |
| Training Time | 104.0 min | 185.1 min |

---

## Test Set Metrics

| Metric | EfficientNet-B0 | ResNet50 |
|--------|-----------------|----------|
| **Accuracy** | **0.9529** | **0.9556** |
| Top-5 Accuracy | 0.9999 | N/A |
| Precision (macro) | 0.9452 | 0.9500 |
| Recall (macro) | 0.9402 | 0.9500 |
| F1 Score (macro) | 0.9371 | 0.9500 |
| Cohen's Kappa | 0.9516 | N/A |
| MCC | 0.9520 | N/A |
| ROC-AUC (macro) | 0.9992 | N/A |
| ROC-AUC (weighted) | 0.9992 | N/A |

---

## Resource Comparison

| Resource | EfficientNet-B0 | ResNet50 |
|----------|-----------------|----------|
| Parameters | 4,065,193 | ~23,508,000 |
| Model Size | 15.80 MB | 90.34 MB |
| Training Time | 104.0 min | 185.1 min |
| Inference/Image | 10.39 ms | N/A |

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
| Accuracy | 0.9556 | 0.9529 | -0.0028 |
| Precision | 0.9500 | 0.9452 | -0.0048 |
| Recall | 0.9500 | 0.9402 | -0.0098 |
| F1 | 0.9500 | 0.9371 | -0.0129 |
| Cohen's Kappa | N/A | 0.9516 | — |
| MCC | N/A | 0.9520 | — |

---

## Parameter Efficiency

| Architecture | Accuracy | Parameters | Acc / Million Params |
|-------------|----------|------------|----------------------|
| ResNet50 | 0.9556 | ~23.5M | 0.0407 |
| EfficientNet-B0 | 0.9529 | 4.1M | 0.2344 |

> **Efficiency Ratio**: EfficientNet-B0 achieves 5.8x the accuracy-per-parameter of ResNet50.

---

## Notes

- The ResNet50 model was trained with a fixed 10-epoch schedule; EfficientNet-B0 used early stopping.
- ResNet50 macro precision/recall/F1 values are taken from the classification report (0.95 macro avg).
- Cohen's Kappa, MCC, and ROC-AUC were not computed for ResNet50 during original training.
- All plots saved at 300 DPI for IEEE publication quality.
