import torch
from torchvision import models, transforms
from PIL import Image
import json
from pathlib import Path

# Define device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load prevention data
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
PREVENTION_DATA_PATH = BASE_DIR / "data" / "disease_prevention.json"

try:
    with open(PREVENTION_DATA_PATH, "r", encoding="utf-8") as f:
        disease_prevention = json.load(f)
    print(f"[OK] Prevention data loaded from {PREVENTION_DATA_PATH}")
except FileNotFoundError:
    raise FileNotFoundError(f"Prevention JSON file not found at {PREVENTION_DATA_PATH}")
except UnicodeDecodeError as e:
    raise RuntimeError(f"Encoding error in JSON file: {e}. Make sure it's saved as UTF-8")

def format_disease_name(raw_name):
    name = raw_name.replace("_", " ").replace(",", "").replace("(", "").replace(")", "")
    return " ".join(name.split())

def get_prevention_steps(disease_name):
    entry = disease_prevention.get(disease_name, {})
    return {
        "en": entry.get("prevention_en", ["No prevention steps found."]),
        "kn": entry.get("prevention_kn", ["ಯಾವುದೇ ತಡೆಗಟ್ಟುವ ಕ್ರಮಗಳ ಮಾಹಿತಿಯಿಲ್ಲ."])
    }

# Load class names dynamically
MAPPING_PATH = BASE_DIR / "ml" / "models" / "disease_class_mapping.json"
try:
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        class_names = json.load(f)
    print(f"[OK] Class names loaded from {MAPPING_PATH}")
except Exception as e:
    print(f"[WARN] Failed to load class names: {e}")
    class_names = []

# Image transform pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# Load trained model
def load_model(model_path="ml/models/trained_plant_disease_model_v2.pth"):
    try:
        model = models.resnet50(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
        
        # Resolve full path to avoid relative path issues
        full_model_path = BASE_DIR / model_path
        model.load_state_dict(torch.load(full_model_path, map_location=device))
        model.to(device)
        model.eval()
        print("[OK] Model loaded successfully.")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None

# Predict disease from PIL image
def predict_image(image, model, lang="en"):
    try:
        image_tensor = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(image_tensor)

        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        predicted_index = torch.argmax(probabilities).item()
        confidence = probabilities[predicted_index].item()

        disease_name = class_names[predicted_index]
        display_name = format_disease_name(disease_name)
        prevention = get_prevention_steps(disease_name)

        entry = disease_prevention.get(disease_name, {})
        
        disease_name_kn = entry.get("disease_name_kn", display_name)
        description = entry.get("description", "Unknown")
        description_kn = entry.get("description_kn", "ಮಾಹಿತಿ ಇಲ್ಲ")
        severity = entry.get("severity", "Unknown")
        severity_kn = entry.get("severity_kn", "ಮಾಹಿತಿ ಇಲ್ಲ")
        yield_loss = entry.get("yield_loss", "Unknown")
        yield_loss_kn = entry.get("yield_loss_kn", "ಮಾಹಿತಿ ಇಲ್ಲ")
        pathogen = entry.get("pathogen", "Unknown")
        pathogen_kn = entry.get("pathogen_kn", "ಮಾಹಿತಿ ಇಲ್ಲ")

        # Map severity to color and score
        severity_color_map = {
            "None": ("green", 0),
            "Low": ("yellow", 25),
            "Medium": ("orange", 50),
            "High": ("red", 75),
            "Critical": ("red", 100)
        }
        
        # Default to gray/0 if unknown
        sev_color, sev_score = severity_color_map.get(severity, ("gray", 0))

        return {
            "disease": display_name,
            "disease_kn": disease_name_kn,
            "confidence": round(confidence, 4),
            "severity": severity,
            "severity_kn": severity_kn,
            "severity_color": sev_color,
            "severity_score": sev_score,
            "yield_loss": yield_loss,
            "yield_loss_kn": yield_loss_kn,
            "pathogen": pathogen,
            "pathogen_kn": pathogen_kn,
            "description": description,
            "description_kn": description_kn,
            "prevention_steps": prevention["en"],
            "prevention_steps_kn": prevention["kn"]
        }

    except Exception as e:
        return {"error": str(e)}
