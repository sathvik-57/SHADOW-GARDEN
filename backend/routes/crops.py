from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np
import json

router = APIRouter(prefix="/api/crops", tags=["Crop Recommendation"])

# Load models and encoders
try:
    crop_clf = joblib.load("ml/models/crop_model.pkl")
    print("[OK] Crop model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load crop model: {e}")
    crop_clf = None

try:
    crop_encoders = joblib.load("ml/models/crop_encoders.pkl")
    print("[OK] Crop encoders loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load crop encoders: {e}")
    crop_encoders = {}

try:
    fertilizer_clf = joblib.load("ml/models/fertilizer_model.pkl")
    print("[OK] Fertilizer model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load fertilizer model: {e}")
    fertilizer_clf = None

try:
    fertilizer_encoders = joblib.load("ml/models/fertilizer_encoders.pkl")
    print("[OK] Fertilizer encoders loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load fertilizer encoders: {e}")
    fertilizer_encoders = {}

# Load lifecycle steps
try:
    with open("data/crop_lifecycle.json", encoding="utf-8") as f:
        crop_lifecycle = json.load(f)
    print("[OK] Crop lifecycle steps loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load lifecycle steps: {e}")
    crop_lifecycle = {}

# Load fertilizer info
try:
    with open("data/fertilizer_info.json", encoding="utf-8") as f:
        fertilizer_info = json.load(f)
    print("[OK] Fertilizer info loaded successfully.")
except Exception as e:
    print(f"[ERROR] Failed to load fertilizer info: {e}")
    fertilizer_info = {}

class CropInput(BaseModel):
    temperature: float
    humidity: float
    ph: float
    n: float
    p: float
    k: float
    rainfall: float

class FertilizerInput(BaseModel):
    temperature: float
    humidity: float
    moisture: float
    soil_type: str
    crop_type: str
    n: float
    p: float
    k: float

@router.post("/recommend-crop")
def recommend_crop(data: CropInput):
    try:
        if crop_clf is None or not crop_encoders:
            return {"error": "Required model or encoders not loaded."}

        # Features: N, P, K, temperature, humidity, ph, rainfall
        X_crop = np.array([[data.n, data.p, data.k, data.temperature, data.humidity, data.ph, data.rainfall]])
        crop_encoded = crop_clf.predict(X_crop)[0]
        crop_name = crop_encoders['Crop Type'].inverse_transform([crop_encoded])[0]

        return {
            "recommended_crop": crop_name
        }
    except Exception as e:
        print(f"[ERROR] Error during crop recommendation: {str(e)}")
        return {"error": str(e)}


@router.post("/recommend-fertilizer")
def recommend_fertilizer(data: FertilizerInput):
    try:
        if fertilizer_clf is None or not fertilizer_encoders:
            return {"error": "Required model or encoders not loaded."}

        # Validate soil type for fertilizer model
        if data.soil_type not in fertilizer_encoders['Soil Type'].classes_:
            soil_encoded = 0
        else:
            soil_encoded = fertilizer_encoders['Soil Type'].transform([data.soil_type])[0]
        
        # Format crop type for fertilizer model
        crop_for_fert = data.crop_type.title()
        if data.crop_type.lower() == 'rice':
            crop_for_fert = 'Paddy'

        if crop_for_fert not in fertilizer_encoders['Crop Type'].classes_:
            crop_encoded_fert = 0
        else:
            crop_encoded_fert = fertilizer_encoders['Crop Type'].transform([crop_for_fert])[0]

        # Features: Temperature, Humidity, Moisture, Soil Type, Crop Type, Nitrogen, Potassium, Phosphorous
        X_fert = np.array([[data.temperature, data.humidity, data.moisture, soil_encoded, crop_encoded_fert, data.n, data.k, data.p]])
        
        fertilizer_encoded = fertilizer_clf.predict(X_fert)[0]
        fertilizer_name = fertilizer_encoders['Fertilizer Name'].inverse_transform([fertilizer_encoded])[0]

        # Handle new nested crop data structure
        crop_name = data.crop_type.title()
        crop_data = crop_lifecycle.get(crop_name, {})
        lifecycle = crop_data.get("lifecycle", [])
        lifecycle_kn = crop_data.get("lifecycle_kn", [])
        water_req = crop_data.get("water_requirement", "Unknown")
        water_req_kn = crop_data.get("water_requirement_kn", "ಮಾಹಿತಿ ಇಲ್ಲ")
        growth_dur = crop_data.get("growth_duration", "Unknown")
        growth_dur_kn = crop_data.get("growth_duration_kn", "ಮಾಹಿತಿ ಇಲ್ಲ")
        ideal_temp = crop_data.get("ideal_temperature", "Unknown")
        ideal_temp_kn = crop_data.get("ideal_temperature_kn", "ಮಾಹಿತಿ ಇಲ್ಲ")
        crop_name_kn = crop_data.get("crop_name_kn", crop_name)

        # Handle new nested fertilizer data structure
        fert_name_title = fertilizer_name.title()
        # Special case for "10-26-26", "14-35-14", "28-28" etc if they exist, title doesn't break them
        fert_data = fertilizer_info.get(fert_name_title, {})
        if not fert_data:
            # Fallback if title case didn't match (e.g., Urea vs UREA vs urea)
            fert_data = fertilizer_info.get(fertilizer_name, {})
            
        why_fertilizer = fert_data.get("reason", f"{fertilizer_name} is recommended based on soil and crop requirements.")
        why_fertilizer_kn = fert_data.get("reason_kn", "ಯಾವುದೇ ಮಾಹಿತಿ ಇಲ್ಲ.")
        dosage = fert_data.get("dosage", "Consult local guidelines")
        dosage_kn = fert_data.get("dosage_kn", "ಸ್ಥಳೀಯ ಕೃಷಿ ಇಲಾಖೆಯನ್ನು ಸಂಪರ್ಕಿಸಿ")
        fertilizer_name_kn = fert_data.get("fertilizer_name_kn", fertilizer_name)

        return {
            "recommended_crop": crop_name,
            "crop_name_kn": crop_name_kn,
            "fertilizer": fertilizer_name,
            "fertilizer_name_kn": fertilizer_name_kn,
            "lifecycle": lifecycle,
            "lifecycle_kn": lifecycle_kn,
            "why_fertilizer": why_fertilizer,
            "why_fertilizer_kn": why_fertilizer_kn,
            "dosage": dosage,
            "dosage_kn": dosage_kn,
            "water_requirement": water_req,
            "water_requirement_kn": water_req_kn,
            "growth_duration": growth_dur,
            "growth_duration_kn": growth_dur_kn,
            "ideal_temperature": ideal_temp,
            "ideal_temperature_kn": ideal_temp_kn
        }

    except Exception as e:
        print(f"[ERROR] Error during fertilizer recommendation: {str(e)}")
        return {"error": str(e)}