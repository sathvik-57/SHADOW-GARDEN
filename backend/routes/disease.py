from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
from ml.inference import load_model, predict_image
from PIL import Image
import io
import json
from pathlib import Path

router = APIRouter(prefix="/api/disease", tags=["Disease Detection"])

# Load model once at startup
model_path = "ml/models/trained_plant_disease_model_v2.pth"
model = load_model(model_path=model_path)

# Load prevention data once
BASE_DIR = Path(__file__).resolve().parent.parent
prevention_data_path = BASE_DIR / "data" / "disease_prevention.json"

with prevention_data_path.open("r", encoding="utf-8") as f:
    prevention_data = json.load(f)

@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(...),
    lang: str = Query("en", enum=["en", "kn"])  # Accept "en" or "kn" as query param
):
    if not file.content_type.startswith("image/"):
        return JSONResponse(status_code=400, content={"error": "Invalid file type. Please upload an image."})

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Predict disease using ML model
        result = predict_image(image, model, lang=lang)

        if "error" in result:
            return JSONResponse(status_code=500, content=result)

        return result

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
