import sys
from pathlib import Path
import random
from PIL import Image

backend_dir = Path('I:/4th SEM/IOT/EL/IOT PROJECT/backend')
sys.path.append(str(backend_dir))

from ml.inference import load_model, predict_image

print('\n--- Loading Model ---')
model = load_model('ml/models/trained_plant_disease_model_v2.pth')

print('\n--- Running Inference on Test Set ---')
test_dir = Path('I:/4th SEM/IOT/EL/IOT PROJECT/DATASET/DISEASE DETECTION/Disease_Dataset_Final/test')
all_images = list(test_dir.glob('*/*.jpg')) + list(test_dir.glob('*/*.JPG')) + list(test_dir.glob('*/*.jpeg'))

if not all_images:
    print('No test images found!')
    sys.exit(1)

sample_images = random.sample(all_images, 10)

correct_predictions = 0

for img_path in sample_images:
    true_label = img_path.parent.name
    img = Image.open(img_path).convert('RGB')
    
    result = predict_image(img, model, lang='en')
    predicted_label = result.get('disease', 'Error')
    confidence = result.get('confidence', 0.0)
    
    is_correct = (true_label == predicted_label)
    if is_correct: 
        correct_predictions += 1
    
    print(f'\nImage: {img_path.name}')
    print(f'True Label: {true_label}')
    print(f'Predicted : {predicted_label} (Match: {is_correct})')
    print(f'Confidence: {confidence:.4f}')
    
    prevention_list = result.get('prevention_steps', ['None'])
    preview = prevention_list[0][:60] if prevention_list else 'None'
    print(f'Prevention: {preview}...')

print(f'\n--- Summary ---')
print(f'Accuracy on sample: {correct_predictions}/10 ({(correct_predictions/10)*100:.1f}%)')
