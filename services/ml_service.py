import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import base64
from ultralytics import YOLO
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MLService:
    """Machine Learning service for acne detection and classification"""
    
    def __init__(self):
        self.detector = None
        self.classifier = None
        self.categories = ['blackheads', 'cysts', 'papules', 'pustules', 'whiteheads']
        self._models_loaded = False
    
    def _ensure_models_loaded(self):
        """Ensure models are loaded (lazy initialization)"""
        if not self._models_loaded:
            self._load_models()
            self._models_loaded = True
    
    def _load_models(self):
        """Load YOLO detector and EfficientNet classifier"""
        try:
            # Load YOLO model for detection
            yolo_path = current_app.config.get('YOLO_MODEL_PATH')
            self.detector = YOLO(yolo_path)
            logger.info(f"YOLO model loaded from: {yolo_path}")
            
            # Load EfficientNet model for classification
            self._load_efficientnet_model()
            
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            raise
    
    def _load_efficientnet_model(self):
        """Load EfficientNet model for classification"""
        try:
            # Try to import EfficientNet from efficientnet_pytorch
            from efficientnet_pytorch import EfficientNet
            
            # Create model with same architecture as training
            model = EfficientNet.from_name('efficientnet-b0')
            num_classes = 5
            model._fc = torch.nn.Linear(model._fc.in_features, num_classes)
            
            # Load the trained weights
            weights_path = current_app.config.get('EFFICIENTNET_MODEL_PATH')
            state_dict = torch.load(weights_path, map_location=torch.device('cpu'), weights_only=False)
            model.load_state_dict(state_dict)
            
            model.eval()
            self.classifier = model
            logger.info(f"EfficientNet model loaded from: {weights_path}")
            
        except ImportError:
            logger.warning("efficientnet_pytorch not found, using fallback model")
            self._create_fallback_model()
            
        except Exception as e:
            logger.error(f"EfficientNet loading failed: {str(e)}")
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Create a simple CNN fallback model"""
        class SimpleCNN(torch.nn.Module):
            def __init__(self, num_classes=5):
                super(SimpleCNN, self).__init__()
                self.features = torch.nn.Sequential(
                    torch.nn.Conv2d(3, 64, 3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.MaxPool2d(2),
                    torch.nn.Conv2d(64, 128, 3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.MaxPool2d(2),
                    torch.nn.Conv2d(128, 256, 3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.MaxPool2d(2),
                    torch.nn.Conv2d(256, 512, 3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.AdaptiveAvgPool2d((1, 1))
                )
                self.classifier = torch.nn.Linear(512, num_classes)
            
            def forward(self, x):
                x = self.features(x)
                x = x.view(x.size(0), -1)
                x = self.classifier(x)
                return x
        
        self.classifier = SimpleCNN(5)
        self.classifier.eval()
        logger.info("Fallback CNN model created")
    
    def process_image(self, image_bytes):
        """Process image for acne detection and classification"""
        try:
            # Ensure models are loaded
            self._ensure_models_loaded()
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            original_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if original_img is None:
                return {'success': False, 'error': 'Invalid image format'}
            
            orig_h, orig_w = original_img.shape[:2]
            
            # YOLO Detection
            results = self.detector(original_img)
            detections = []
            
            # Process each detection
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                        conf_val = float(box.conf[0])
                        
                        if conf_val < 0.5:  # Confidence threshold
                            continue
                        
                        # Crop region for classification
                        side = 150
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        x1_o, y1_o = max(0, cx - side), max(0, cy - side)
                        x2_o, y2_o = min(orig_w, cx + side), min(orig_h, cy + side)
                        
                        crop_raw = original_img[y1_o:y2_o, x1_o:x2_o]
                        
                        if crop_raw.size > 0:
                            # Preprocess for EfficientNet
                            cnn_input = cv2.cvtColor(crop_raw, cv2.COLOR_BGR2RGB)
                            cnn_input = cv2.resize(cnn_input, (224, 224))
                            
                            # Convert to tensor and normalize
                            cnn_tensor = torch.from_numpy(cnn_input).float() / 255.0
                            cnn_tensor = cnn_tensor.permute(2, 0, 1).unsqueeze(0)
                            
                            # Classification
                            with torch.no_grad():
                                output = self.classifier(cnn_tensor)
                                probabilities = F.softmax(output, dim=1)
                                predicted_idx = torch.argmax(probabilities[0]).item()
                                label = self.categories[predicted_idx]
                                confidence = float(probabilities[0][predicted_idx])
                            
                            # Encode cropped image
                            _, buffer_crop = cv2.imencode('.jpg', crop_raw)
                            crop_b64 = base64.b64encode(buffer_crop).decode('utf-8')
                            
                            detections.append({
                                'type': label,
                                'confidence': round(confidence, 3),
                                'detection_confidence': round(conf_val, 3),
                                'bbox': {
                                    'x': int(x1),
                                    'y': int(y1),
                                    'width': int(x2 - x1),
                                    'height': int(y2 - y1)
                                },
                                'crop': f"data:image/jpeg;base64,{crop_b64}"
                            })
            
            # Calculate severity
            count = len(detections)
            severity = "Clear Skin" if count == 0 else "Mild" if count < 5 else "Moderate" if count < 15 else "Severe"
            
            # Create annotated image
            annotated_img = original_img.copy()
            for detection in detections:
                bbox = detection['bbox']
                cv2.rectangle(annotated_img, 
                           (bbox['x'], bbox['y']), 
                           (bbox['x'] + bbox['width'], bbox['y'] + bbox['height']), 
                           (0, 255, 0), 2)
                cv2.putText(annotated_img, detection['type'], 
                           (bbox['x'], bbox['y'] - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Encode annotated image
            _, buffer_full = cv2.imencode('.jpg', annotated_img)
            full_image_b64 = base64.b64encode(buffer_full).decode('utf-8')
            
            return {
                'success': True,
                'detections': detections,
                'total_count': count,
                'severity_level': severity,
                'annotated_image': f"data:image/jpeg;base64,{full_image_b64}"
            }
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            return {'success': False, 'error': 'Image processing failed'}
    
    def get_model_info(self):
        """Get information about loaded models"""
        self._ensure_models_loaded()
        return {
            'detector_loaded': self.detector is not None,
            'classifier_loaded': self.classifier is not None,
            'categories': self.categories,
            'yolo_model_path': current_app.config.get('YOLO_MODEL_PATH'),
            'efficientnet_model_path': current_app.config.get('EFFICIENTNET_MODEL_PATH')
        }
    
    def validate_image(self, image_file):
        """Validate uploaded image file"""
        try:
            # Check file extension
            allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
            if not image_file.filename:
                return False, "No file selected"
            
            file_ext = image_file.filename.rsplit('.', 1)[1].lower()
            if file_ext not in allowed_extensions:
                return False, f"File type '{file_ext}' not allowed. Allowed types: {', '.join(allowed_extensions)}"
            
            # Check file size
            max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
            image_file.seek(0, 2)  # Seek to end
            file_size = image_file.tell()
            image_file.seek(0)  # Reset position
            
            if file_size > max_size:
                return False, f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            
            return True, "Valid image file"
            
        except Exception as e:
            logger.error(f"Image validation error: {str(e)}")
            return False, "Image validation failed"

# Global ML service instance
ml_service = MLService()
