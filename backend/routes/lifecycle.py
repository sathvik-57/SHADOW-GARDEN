from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter()

@router.get("/lifecycle/{crop_name}")
def get_crop_lifecycle(crop_name: str):
    path = os.path.join("data", "crop_lifecycle.xlsx")
    df = pd.read_excel(path)
    filtered = df[df["Crop"].str.lower() == crop_name.lower()]
    if filtered.empty:
        return {"error": f"No lifecycle data found for {crop_name}"}
    return filtered.to_dict(orient="records")
