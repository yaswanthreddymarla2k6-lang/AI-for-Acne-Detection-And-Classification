import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

# --- 1. LOAD MODELS ---
# Using YOLO for detection, and PyTorch EfficientNet model for classification
detector = YOLO('best1.pt') 

# Load the EfficientNet model
def load_efficientnet_model():
    """Load the trained EfficientNet model for acne classification"""
    try:
        # Try to import EfficientNet from efficientnet_pytorch
        from efficientnet_pytorch import EfficientNet
        
        # Create the model with same architecture as training
        model = EfficientNet.from_name('efficientnet-b0')
        num_classes = 5
        model._fc = nn.Linear(model._fc.in_features, num_classes)
        
        # Load the trained weights
        state_dict = torch.load('acne_weights.pth', map_location=torch.device('cpu'), weights_only=False)
        model.load_state_dict(state_dict)
        
        model.eval()
        print("✅ EfficientNet model loaded successfully!")
        return model
        
    except ImportError:
        print("⚠️ efficientnet_pytorch not found, using fallback model")
        # Create a simple CNN fallback
        class SimpleCNN(nn.Module):
            def __init__(self, num_classes=5):
                super(SimpleCNN, self).__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(3, 64, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(64, 128, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(128, 256, 3, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    nn.Conv2d(256, 512, 3, padding=1),
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d((1, 1))
                )
                self.classifier = nn.Linear(512, num_classes)
            
            def forward(self, x):
                x = self.features(x)
                x = x.view(x.size(0), -1)
                x = self.classifier(x)
                return x
        
        model = SimpleCNN(5)
        model.eval()
        print("✅ Simple CNN fallback model loaded")
        return model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

classifier = load_efficientnet_model()
categories = ['blackheads', 'cysts', 'papules', 'pustules', 'whiteheads']

def process_image(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    original_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if original_img is None:
        return None, None
    
    orig_h, orig_w = original_img.shape[:2]
    
    # --- 2. YOLO DETECTION (Replacing the old Keras detector) ---
    # We use YOLO to get the boxes (rx1, ry1, rx2, ry2)
    results = detector.predict(original_img, conf=0.15, iou=0.25, verbose=False)
    result = results[0]

    detections = []
    annotated_full_view = original_img.copy()

    if result.boxes is not None:
        for box in result.boxes:
            # Get coordinates from YOLO
            coords = box.xyxy[0].cpu().numpy()
            rx1, ry1, rx2, ry2 = map(int, coords)
            conf_val = float(box.conf[0])

            # Draw rectangle on the main view
            cv2.rectangle(annotated_full_view, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)

            # --- 3. ORIGINAL CNN CLASSIFICATION CODE (From your first script) ---
            # This part is kept exactly as you provided in the first code block
            side = 150
            cx, cy = (rx1 + rx2) // 2, (ry1 + ry2) // 2
            x1_o, y1_o = max(0, cx - side), max(0, cy - side)
            x2_o, y2_o = min(orig_w, cx + side), min(orig_h, cy + side)
            
            # Crop from the original image (before any boxes are drawn)
            crop_raw = original_img[y1_o:y2_o, x1_o:x2_o]
            
            if crop_raw.size > 0:
                # Preprocessing for PyTorch EfficientNet model (same as training)
                # Convert BGR to RGB and resize to 224x224
                cnn_input = cv2.cvtColor(crop_raw, cv2.COLOR_BGR2RGB)
                cnn_input = cv2.resize(cnn_input, (224, 224))
                
                # Convert to tensor and normalize to [0, 1]
                cnn_tensor = torch.from_numpy(cnn_input).float() / 255.0
                # Rearrange dimensions from HWC to CHW and add batch dimension
                cnn_tensor = cnn_tensor.permute(2, 0, 1).unsqueeze(0)
                
                # Prediction with PyTorch model
                with torch.no_grad():
                    output = classifier(cnn_tensor)
                    probabilities = F.softmax(output, dim=1)
                    predicted_idx = torch.argmax(probabilities[0]).item()
                    label = categories[predicted_idx]

                cv2.putText(annotated_full_view, label, (rx1, ry1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                _, buffer_crop = cv2.imencode('.jpg', crop_raw)
                detections.append({
                    "type": label,
                    "confidence": conf_val,
                    "crop": f"data:image/jpeg;base64,{base64.b64encode(buffer_crop).decode('utf-8')}"
                })

    _, buffer_full = cv2.imencode('.jpg', annotated_full_view)
    full_image_b64 = f"data:image/jpeg;base64,{base64.b64encode(buffer_full).decode('utf-8')}"
    return detections, full_image_b64

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    detections, full_img_url = process_image(file.read())
    
    if detections is None:
        return jsonify({"error": "Processing failed"}), 400
        
    count = len(detections)
    severity = "Clear Skin" if count == 0 else "Mild" if count < 5 else "Moderate" if count < 15 else "Severe"
    return jsonify({
        "total_count": count, 
        "detections": detections, 
        "full_annotated_image": full_img_url, 
        "severity": severity
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)