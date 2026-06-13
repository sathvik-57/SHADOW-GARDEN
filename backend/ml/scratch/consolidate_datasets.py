import os
import glob
import json
import hashlib
import shutil
import random
import csv
from collections import defaultdict
from pathlib import Path

base_path = r"I:\4th SEM\IOT\EL\IOT PROJECT\DATASET\DISEASE DETECTION"
output_dir = os.path.join(base_path, "Disease_Dataset_Final")

# Ensure clean slate for output if it exists (but we'll just create it)
os.makedirs(output_dir, exist_ok=True)

d1_path = os.path.join(base_path, r"archive\New Plant Diseases Dataset(Augmented)\train")
d2_path = os.path.join(base_path, r"archive (1)\PlantVillage\PlantVillage")
if not os.path.exists(d2_path):
    d2_path = os.path.join(base_path, r"archive (1)\PlantVillage")
d3_path = os.path.join(base_path, r"archive2\Crop Diseases")

datasets = {
    "D1": d1_path,
    "D2": d2_path,
    "D3": d3_path
}

def normalize_class_name(name):
    name = name.replace("___", "_").replace("__", "_").replace("-", "_").replace("_(maize)", "").replace("_bell", "").replace(" ", "_")
    name = name.replace("YellowLeaf", "Yellow_Leaf")
    name = name.strip("_").lower()
    return name.title()

def get_file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception as e:
        return None

print("Scanning and hashing files...")

class_images = defaultdict(list)
duplicate_summary = defaultdict(list)
seen_hashes = {} # class -> set of hashes

for d_name, d_path in datasets.items():
    if not os.path.exists(d_path):
        print(f"Warning: Path not found {d_path}")
        continue
    
    classes = [d for d in os.listdir(d_path) if os.path.isdir(os.path.join(d_path, d))]
    for cls in classes:
        norm_name = normalize_class_name(cls)
        if norm_name not in seen_hashes:
            seen_hashes[norm_name] = set()
            
        cls_path = os.path.join(d_path, cls)
        images = glob.glob(os.path.join(cls_path, "*.*"))
        
        for img_path in images:
            img_hash = get_file_hash(img_path)
            if img_hash is None:
                continue
                
            if img_hash in seen_hashes[norm_name]:
                duplicate_summary[norm_name].append({
                    "dataset": d_name,
                    "original_class": cls,
                    "file": os.path.basename(img_path),
                    "hash": img_hash
                })
            else:
                seen_hashes[norm_name].add(img_hash)
                class_images[norm_name].append({
                    "path": img_path,
                    "hash": img_hash,
                    "ext": os.path.splitext(img_path)[1]
                })

print("Hashing complete. Splitting and copying files...")

# Split 80/10/10
splits = ['train', 'valid', 'test']
for s in splits:
    os.makedirs(os.path.join(output_dir, s), exist_ok=True)

class_counts = {}
consolidation_report = {}

random.seed(42) # For reproducibility

total_copied = 0

for cls, images in class_images.items():
    if len(images) == 0:
        continue
        
    random.shuffle(images)
    
    total_imgs = len(images)
    train_end = int(total_imgs * 0.8)
    valid_end = train_end + int(total_imgs * 0.1)
    
    split_imgs = {
        'train': images[:train_end],
        'valid': images[train_end:valid_end],
        'test': images[valid_end:]
    }
    
    class_counts[cls] = {
        'Total': total_imgs,
        'Train': len(split_imgs['train']),
        'Valid': len(split_imgs['valid']),
        'Test': len(split_imgs['test'])
    }
    
    consolidation_report[cls] = class_counts[cls].copy()
    
    # Create class dirs and copy
    for split_name, imgs in split_imgs.items():
        split_dir = os.path.join(output_dir, split_name, cls)
        os.makedirs(split_dir, exist_ok=True)
        
        for img_info in imgs:
            dest_filename = f"{img_info['hash']}{img_info['ext']}"
            dest_path = os.path.join(split_dir, dest_filename)
            shutil.copy2(img_info['path'], dest_path)
            total_copied += 1
            
print(f"Copied {total_copied} deduplicated files.")

print("Generating reports...")

reports_dir = os.path.join(base_path, "Consolidation_Reports")
os.makedirs(reports_dir, exist_ok=True)

# 1. consolidation_report.json
with open(os.path.join(reports_dir, "consolidation_report.json"), "w") as f:
    json.dump(consolidation_report, f, indent=4)

# 2. class_counts.csv
with open(os.path.join(reports_dir, "class_counts.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Class", "Total", "Train (80%)", "Valid (10%)", "Test (10%)"])
    for cls, counts in class_counts.items():
        writer.writerow([cls, counts['Total'], counts['Train'], counts['Valid'], counts['Test']])

# 3. duplicate_summary.json
# Too large to format pretty fully if thousands of files, but we'll dump it
with open(os.path.join(reports_dir, "duplicate_summary.json"), "w") as f:
    # Just save count per class for brevity in top level, full list inside
    summary = {
        "total_duplicates": sum(len(dup) for dup in duplicate_summary.values()),
        "duplicates_per_class": {cls: len(dup) for cls, dup in duplicate_summary.items()},
        "details": duplicate_summary
    }
    json.dump(summary, f, indent=4)

print(f"Consolidation complete! Reports saved in {reports_dir}")
