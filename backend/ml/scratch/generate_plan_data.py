import json

with open('analysis_report.json') as f:
    data = json.load(f)

# Combine essentially identical classes that might have differed by punctuation not caught by the first normalizer
final_classes = {}

for key, info in data.items():
    # normalize key more aggressively for merging
    norm_key = key.replace("-", "_").replace("_(maize)", "").replace("_bell", "").strip("_")
    
    if norm_key not in final_classes:
        final_classes[norm_key] = {
            "original_names": [],
            "datasets": set(),
            "total_count": 0
        }
        
    final_classes[norm_key]["original_names"].extend(info["original_names"])
    final_classes[norm_key]["datasets"].update(info["datasets"])
    final_classes[norm_key]["total_count"] += info["total_count"]

print(f"Total Unique Classes after normalization: {len(final_classes)}")

# Identify duplicates
duplicates = {k: v for k, v in final_classes.items() if len(v["datasets"]) > 1}
print(f"\nDuplicates ({len(duplicates)}):")
for k, v in duplicates.items():
    print(f"- {k}: {v['total_count']} images from {v['datasets']}")

# Empty classes
empty = {k: v for k, v in final_classes.items() if v["total_count"] == 0}
print(f"\nEmpty Classes ({len(empty)}):")
for k, v in empty.items():
    print(f"- {k}")

# Total images
total_images = sum(v["total_count"] for v in final_classes.values())
print(f"\nTotal Images: {total_images}")

# Generate the proposed final structure
print("\nProposed Final Structure:")
for k in sorted(final_classes.keys()):
    if final_classes[k]["total_count"] > 0:
        print(f"├── {k.title().replace('_', ' ')}/ ({final_classes[k]['total_count']} images)")
