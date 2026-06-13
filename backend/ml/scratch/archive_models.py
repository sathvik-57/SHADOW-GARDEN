import os
import shutil
import json
from datetime import datetime

base_ml_dir = r"I:\4th SEM\IOT\EL\IOT PROJECT\backend\ml"
models_dir = os.path.join(base_ml_dir, "models")
results_dir = os.path.join(base_ml_dir, "results")
archive_dir = os.path.join(base_ml_dir, "model_archive")

# Ensure archive subdirectories exist
for module in ["crop", "fertilizer", "disease"]:
    os.makedirs(os.path.join(archive_dir, module), exist_ok=True)

manifest = []

def copy_to_archive(src_path, module):
    if not os.path.exists(src_path):
        return
        
    if os.path.isfile(src_path):
        filename = os.path.basename(src_path)
        dest_path = os.path.join(archive_dir, module, filename)
        
        # Avoid copying to itself if they happen to overlap, though they don't
        shutil.copy2(src_path, dest_path)
        
        stat = os.stat(src_path)
        creation_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
        
        manifest.append({
            "Filename": filename,
            "Module": module,
            "Creation_Timestamp": creation_time,
            "File_Size_Bytes": stat.st_size,
            "Original_Location": src_path
        })
    elif os.path.isdir(src_path):
        # Recursively process files in the directory
        for item in os.listdir(src_path):
            copy_to_archive(os.path.join(src_path, item), module)

# 1. Archive Crop Models & Artifacts
for f in os.listdir(models_dir):
    if "crop" in f.lower():
        copy_to_archive(os.path.join(models_dir, f), "crop")

if os.path.exists(results_dir):
    for f in os.listdir(results_dir):
        if "crop" in f.lower():
            copy_to_archive(os.path.join(results_dir, f), "crop")

# 2. Archive Fertilizer Models & Artifacts
for f in os.listdir(models_dir):
    if "fertilizer" in f.lower():
        copy_to_archive(os.path.join(models_dir, f), "fertilizer")

if os.path.exists(results_dir):
    for f in os.listdir(results_dir):
        if "fertilizer" in f.lower():
            copy_to_archive(os.path.join(results_dir, f), "fertilizer")

# 3. Archive Disease Models & Artifacts
disease_model_path = os.path.join(base_ml_dir, "trained_plant_disease_model.pth")
if os.path.exists(disease_model_path):
    copy_to_archive(disease_model_path, "disease")

# Write Manifest
manifest_path = os.path.join(archive_dir, "archive_manifest.json")
with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=4)

print("Archive Process Complete.")
print(f"Archived Crop files: {len([x for x in manifest if x['Module'] == 'crop'])}")
print(f"Archived Fertilizer files: {len([x for x in manifest if x['Module'] == 'fertilizer'])}")
print(f"Archived Disease files: {len([x for x in manifest if x['Module'] == 'disease'])}")
