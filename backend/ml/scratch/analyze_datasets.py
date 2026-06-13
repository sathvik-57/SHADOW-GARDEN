import os
import glob
import json

base_path = r"I:\4th SEM\IOT\EL\IOT PROJECT\DATASET\DISEASE DETECTION"

d1_path = os.path.join(base_path, r"archive\New Plant Diseases Dataset(Augmented)\train")
d2_path = os.path.join(base_path, r"archive (1)\PlantVillage\PlantVillage") # nested
if not os.path.exists(d2_path):
    d2_path = os.path.join(base_path, r"archive (1)\PlantVillage")
d3_path = os.path.join(base_path, r"archive2\Crop Diseases")

datasets = {
    "D1": d1_path,
    "D2": d2_path,
    "D3": d3_path
}

def normalize_class_name(name):
    # E.g., 'Tomato_Late_blight', 'Tomato___Late_blight', 'Tomato_Late_Blight'
    name = name.replace("___", "_").replace("__", "_").replace(" ", "_")
    name = name.lower()
    return name

inventory = {}

for d_name, d_path in datasets.items():
    if not os.path.exists(d_path):
        print(f"Warning: Path not found {d_path}")
        continue
    
    classes = [d for d in os.listdir(d_path) if os.path.isdir(os.path.join(d_path, d))]
    for cls in classes:
        cls_path = os.path.join(d_path, cls)
        # count images
        images = glob.glob(os.path.join(cls_path, "*.*"))
        count = len(images)
        
        norm_name = normalize_class_name(cls)
        
        if norm_name not in inventory:
            inventory[norm_name] = {
                "original_names": set(),
                "datasets": set(),
                "total_count": 0,
                "dataset_counts": {}
            }
        
        inventory[norm_name]["original_names"].add(cls)
        inventory[norm_name]["datasets"].add(d_name)
        inventory[norm_name]["total_count"] += count
        inventory[norm_name]["dataset_counts"][d_name] = inventory[norm_name]["dataset_counts"].get(d_name, 0) + count

# Convert sets to list for JSON
for key in inventory:
    inventory[key]["original_names"] = list(inventory[key]["original_names"])
    inventory[key]["datasets"] = list(inventory[key]["datasets"])

with open("analysis_report.json", "w") as f:
    json.dump(inventory, f, indent=4)

print("Analysis complete. Saved to analysis_report.json.")
