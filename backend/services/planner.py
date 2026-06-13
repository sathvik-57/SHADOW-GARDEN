import pandas as pd

class CropPlanner:
    def __init__(self, lifecycle_file: str):
        self.df = pd.read_excel(lifecycle_file)

    def get_plan(self, crop_type: str) -> dict:
        match = self.df[self.df["Crop"].str.lower() == crop_type.lower()]
        if match.empty:
            return {"error": "No plan found for this crop"}
        row = match.iloc[0]
        return {
            "crop": row["Crop"],
            "sowing": row["Sowing"],
            "irrigation": row["Irrigation"],
            "fertilizer": row["Fertilizer"],
            "pest_control": row["Pest Control"],
            "harvest": row["Harvest"]
        }
