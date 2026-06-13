import os
import json
import torch
import torch.nn as nn
import numpy as np
from torchvision import transforms, datasets, models
from torch.utils.data import DataLoader
from sklearn.metrics import cohen_kappa_score, matthews_corrcoef, roc_auc_score

base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "..", "DATASET", "DISEASE DETECTION", "Disease_Dataset_Final"))
test_dir = os.path.join(dataset_dir, "test")

# Using the V2 model which was trained on 45 classes and generated the 95.56% metrics
model_path = os.path.abspath(os.path.join(base_dir, "..", "models", "trained_plant_disease_model_v2.pth"))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
image_size = 224
batch_size = 16

def load_model(num_classes):
    model = models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

def main():
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return

    # Using standard test transform
    test_transforms = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    
    test_dataset = datasets.ImageFolder(test_dir, test_transforms)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    
    class_names = test_dataset.classes
    num_classes = len(class_names)
    
    model = load_model(num_classes)
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    top5_correct = 0
    total = 0
    
    print("Evaluating ResNet50 on Test Set...")
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            
            probs = torch.nn.functional.softmax(outputs, dim=1)
            all_probs.extend(probs.cpu().numpy())
            
            # Top 1
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            # Top 5
            _, top5_preds = outputs.topk(5, 1, True, True)
            for i in range(len(labels)):
                if labels[i] in top5_preds[i]:
                    top5_correct += 1
            total += len(labels)

    top5_acc = top5_correct / total
    kappa = cohen_kappa_score(all_labels, all_preds)
    mcc = matthews_corrcoef(all_labels, all_preds)
    
    try:
        roc_auc_macro = roc_auc_score(all_labels, all_probs, multi_class='ovr', average='macro')
        roc_auc_weighted = roc_auc_score(all_labels, all_probs, multi_class='ovr', average='weighted')
    except Exception as e:
        print(f"Failed to calculate ROC-AUC: {e}")
        roc_auc_macro = 0.0
        roc_auc_weighted = 0.0

    print(f"\n--- ResNet50 Metrics ---")
    print(f"Top-5 Accuracy: {top5_acc:.4f}")
    print(f"Cohen's Kappa: {kappa:.4f}")
    print(f"MCC: {mcc:.4f}")
    print(f"ROC-AUC (Macro): {roc_auc_macro:.4f}")
    print(f"ROC-AUC (Weighted): {roc_auc_weighted:.4f}")

if __name__ == "__main__":
    main()
