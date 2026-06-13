import os
import time
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from torchvision.models import resnet50, ResNet50_Weights

# ----------------- CONFIGURATION -----------------
base_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(base_dir, "..", "..", "DATASET", "DISEASE DETECTION", "Disease_Dataset_Final")
train_dir = os.path.join(dataset_dir, "train")
valid_dir = os.path.join(dataset_dir, "valid")
test_dir = os.path.join(dataset_dir, "test")

models_dir = os.path.join(base_dir, "models")
results_dir = os.path.join(base_dir, "results", "disease_v2")
os.makedirs(models_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)

model_save_path = os.path.join(models_dir, "trained_plant_disease_model_v2.pth")
mapping_save_path = os.path.join(models_dir, "disease_class_mapping.json")

batch_size = 16
image_size = 224
num_epochs = 10
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------------- DATA LOADING -----------------
data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]),
    'valid': transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]),
    'test': transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
}

# ----------------- TRAINING LOOP -----------------
def train_model(model, criterion, optimizer, scheduler, dataloaders, dataset_sizes, num_epochs=10):
    since = time.time()
    best_acc = 0.0
    history = {'train_loss': [], 'valid_loss': [], 'train_acc': [], 'valid_acc': []}
    
    print(f"Starting training on {device}...")
    for epoch in range(num_epochs):
        print(f"Epoch {epoch + 1}/{num_epochs}")
        print("-" * 10)
        
        for phase in ['train', 'valid']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
            
            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double().item() / dataset_sizes[phase]

            print(f"{phase.capitalize()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
            
            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(epoch_acc)

            # Save Best Model based on Validation Accuracy
            if phase == 'valid' and epoch_acc > best_acc:
                best_acc = epoch_acc
                torch.save(model.state_dict(), model_save_path)
                print(f"  -> Best model updated! (Valid Acc: {best_acc:.4f})")
                
    time_elapsed = time.time() - since
    print(f"\nTraining complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s")
    print(f"Best Validation Accuracy: {best_acc:.4f}")
    
    return history, time_elapsed, history['train_acc'][-1], best_acc

def main():
    image_datasets = {
        'train': datasets.ImageFolder(train_dir, data_transforms['train']),
        'valid': datasets.ImageFolder(valid_dir, data_transforms['valid']),
        'test': datasets.ImageFolder(test_dir, data_transforms['test'])
    }

    dataloaders = {
        'train': DataLoader(image_datasets['train'], batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True),
        'valid': DataLoader(image_datasets['valid'], batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True),
        'test': DataLoader(image_datasets['test'], batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True)
    }

    dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'valid', 'test']}
    class_names = image_datasets['train'].classes

    # Save mapping
    with open(mapping_save_path, "w") as f:
        json.dump(class_names, f, indent=4)

    # ----------------- MODEL SETUP -----------------
    model = resnet50(weights=ResNet50_Weights.DEFAULT)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(class_names))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=4, gamma=0.1)

    history, train_time, final_train_acc, best_valid_acc = train_model(
        model, criterion, optimizer, scheduler, dataloaders, dataset_sizes, num_epochs
    )

    # ----------------- PLOTTING -----------------
    plt.figure(figsize=(8,6))
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['valid_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(os.path.join(results_dir, "training_loss.png"))
    plt.close()

    plt.figure(figsize=(8,6))
    plt.plot(history['train_acc'], label='Train Accuracy')
    plt.plot(history['valid_acc'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.savefig(os.path.join(results_dir, "training_accuracy.png"))
    plt.close()

    # ----------------- EVALUATION ON TEST SET -----------------
    print("Evaluating best model on Test set...")
    model.load_state_dict(torch.load(model_save_path))
    model.eval()

    all_preds = []
    all_labels = []

    running_corrects = 0
    with torch.no_grad():
        for inputs, labels in dataloaders['test']:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            running_corrects += torch.sum(preds == labels.data)

    test_acc = running_corrects.double().item() / dataset_sizes['test']
    print(f"Test Accuracy: {test_acc:.4f}")

    # Classification Report
    report = classification_report(all_labels, all_preds, target_names=class_names)
    with open(os.path.join(results_dir, "classification_report.txt"), "w") as f:
        f.write(report)

    # Confusion Matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(20, 16))
    sns.heatmap(cm, annot=False, cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix - Test Set')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "confusion_matrix.png"))
    plt.close()

    # ----------------- FINAL METRICS SAVE -----------------
    model_size = os.path.getsize(model_save_path) / (1024 * 1024)

    metrics = {
        "Train_Accuracy": final_train_acc,
        "Validation_Accuracy": best_valid_acc,
        "Test_Accuracy": test_acc,
        "Training_Time_Seconds": train_time,
        "Final_Model_Size_MB": model_size,
        "Number_Of_Classes": len(class_names)
    }

    with open(os.path.join(results_dir, "disease_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)

    print("\nModel training and evaluation fully complete. Check backend/ml/results/disease_v2 for artifacts.")

if __name__ == "__main__":
    main()
