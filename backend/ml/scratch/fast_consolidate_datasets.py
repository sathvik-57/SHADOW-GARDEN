import os
import glob
import json
import hashlib
import shutil
import random
import csv
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

base_path = r"I:\4th SEM\IOT\EL\IOT PROJECT\DATASET\DISEASE DETECTION"
output_dir = os.path.join(base_path, "Disease_Dataset_Final")
os.makedirs(output_dir, exist_ok=True)

datasets = {
    "D1": os.path.join(base_path, r"archive\New Plant Diseases Dataset(Augmented)\train"),
    "D2": os.path.join(base_path, r"archive (1)\PlantVillage\PlantVillage"),
    "D3": os.path.join(base_path, r"archive2\Crop Diseases")
}

if not os.path.exists(datasets["D2"]):
    datasets["D2"] = os.path.join(base_path, r"archive (1)\PlantVillage")

def normalize_class_name(name):
    name = name.replace("___", "_").replace("__", "_").replace("-", "_").replace("_(maize)", "").replace("_bell", "").replace(" ", "_")
    name = name.replace("YellowLeaf", "Yellow_Leaf")
    return name.strip("_").lower().title()

def get_file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as afile:
            buf = afile.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None

def process_image(img_info):
    img_path = img_info['path']
    img_hash = get_file_hash(img_path)
    return {
        **img_info,
        'hash': img_hash
    }

print("Gathering files...")
all_images = []
for d_name, d_path in datasets.items():
    if not os.path.exists(d_path): continue
    for cls in [d for d in os.listdir(d_path) if os.path.isdir(os.path.join(d_path, d))]:
        norm_name = normalize_class_name(cls)
        for img_path in glob.glob(os.path.join(d_path, cls, "*.*")):
            all_images.append({
                'dataset': d_name,
                'original_class': cls,
                'norm_name': norm_name,
                'path': img_path,
                'ext': os.path.splitext(img_path)[1]
            })

print(f"Hashing {len(all_images)} files concurrently...")
class_images = defaultdict(list)
duplicate_summary = defaultdict(list)
seen_hashes = {}

with ThreadPoolExecutor(max_workers=32) as executor:
    futures = [executor.submit(process_image, img) for img in all_images]
    for i, future in enumerate(as_completed(futures)):
        res = future.result()
        img_hash = res['hash']
        if not img_hash: continue
        
        norm_name = res['norm_name']
        if norm_name not in seen_hashes:
            seen_hashes[norm_name] = set()
            
        if img_hash in seen_hashes[norm_name]:
            duplicate_summary[norm_name].append(res)
        else:
            seen_hashes[norm_name].add(img_hash)
            class_images[norm_name].append(res)

print("Hashing complete. Splitting and copying files...")
splits = ['train', 'valid', 'test']
for s in splits:
    os.makedirs(os.path.join(output_dir, s), exist_ok=True)

class_counts = {}
consolidation_report = {}
random.seed(42)

copy_tasks = []
for cls, images in class_images.items():
    if len(images) == 0: continue
    random.shuffle(images)
    
    total = len(images)
    train_end = int(total * 0.8)
    valid_end = train_end + int(total * 0.1)
    
    split_imgs = {
        'train': images[:train_end],
        'valid': images[train_end:valid_end],
        'test': images[valid_end:]
    }
    class_counts[cls] = {'Total': total, 'Train': len(split_imgs['train']), 'Valid': len(split_imgs['valid']), 'Test': len(split_imgs['test'])}
    consolidation_report[cls] = class_counts[cls].copy()
    
    for split_name, imgs in split_imgs.items():
        split_dir = os.path.join(output_dir, split_name, cls)
        os.makedirs(split_dir, exist_ok=True)
        for img in imgs:
            dest = os.path.join(split_dir, f"{img['hash']}{img['ext']}")
            copy_tasks.append((img['path'], dest))

def copy_file(task):
    src, dst = task
    shutil.copy2(src, dst)

print(f"Copying {len(copy_tasks)} files concurrently...")
with ThreadPoolExecutor(max_workers=32) as executor:
    list(executor.map(copy_file, copy_tasks))

print("Generating reports...")
reports_dir = os.path.join(base_path, "Consolidation_Reports")
os.makedirs(reports_dir, exist_ok=True)

with open(os.path.join(reports_dir, "consolidation_report.json"), "w") as f:
    json.dump(consolidation_report, f, indent=4)

with open(os.path.join(reports_dir, "class_counts.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Class", "Total", "Train", "Valid", "Test"])
    for cls, counts in class_counts.items():
        writer.writerow([cls, counts['Total'], counts['Train'], counts['Valid'], counts['Test']])

with open(os.path.join(reports_dir, "duplicate_summary.json"), "w") as f:
    json.dump({"total_duplicates": sum(len(d) for d in duplicate_summary.values()), "details": {k: len(v) for k, v in duplicate_summary.items()}}, f, indent=4)

print("Done.")
