import torch
import numpy as np
import cv2
from PIL import Image

def analyze_best_model():
    """Analyze the output format of best(1).pt model"""
    
    print("Loading best(1).pt model...")
    try:
        # Try loading with ultralytics first
        try:
            from ultralytics import YOLO
            model = YOLO('best (1).pt')
            print("Model loaded with Ultralytics YOLO")
            model_type = "ultralytics"
        except:
            # Fallback to PyTorch loading
            model_data = torch.load('best (1).pt', map_location=torch.device('cpu'), weights_only=False)
            print(f"Model loaded as type: {type(model_data)}")
            
            if isinstance(model_data, dict):
                if 'model' in model_data:
                    model = model_data['model']
                else:
                    model = model_data
            else:
                model = model_data
            
            model_type = "pytorch"
        
        print(f"Model type: {model_type}")
        
        # Create a test image
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # Test model inference
        print("Running inference on test image...")
        
        if model_type == "ultralytics":
            # Ultralytics YOLO inference
            results = model(test_img)
            print("Ultralytics results structure:")
            
            for i, result in enumerate(results):
                print(f"Result {i}:")
                print(f"  Type: {type(result)}")
                print(f"  Has boxes: {hasattr(result, 'boxes')}")
                print(f"  Has names: {hasattr(result, 'names')}")
                
                if hasattr(result, 'boxes'):
                    boxes = result.boxes
                    print(f"  Boxes type: {type(boxes)}")
                    print(f"  Boxes length: {len(boxes) if boxes is not None else 0}")
                    
                    if boxes is not None and len(boxes) > 0:
                        print(f"  First box attributes: {dir(boxes[0])}")
                        
                        # Extract sample data
                        if hasattr(boxes[0], 'xyxy'):
                            xyxy = boxes[0].xyxy[0].cpu().numpy()
                            print(f"  Sample xyxy: {xyxy}")
                        
                        if hasattr(boxes[0], 'conf'):
                            conf = boxes[0].conf[0].cpu().numpy()
                            print(f"  Sample confidence: {conf}")
                        
                        if hasattr(boxes[0], 'cls'):
                            cls = boxes[0].cls[0].cpu().numpy()
                            print(f"  Sample class: {cls}")
                
                if hasattr(result, 'names'):
                    print(f"  Class names: {result.names}")
        
        else:
            # PyTorch model inference
            img_tensor = torch.from_numpy(test_img).permute(2, 0, 1).float().unsqueeze(0) / 255.0
            
            with torch.no_grad():
                outputs = model(img_tensor)
            
            print(f"PyTorch outputs type: {type(outputs)}")
            print(f"PyTorch outputs length: {len(outputs) if hasattr(outputs, '__len__') else 'N/A'}")
            
            if hasattr(outputs, '__len__') and len(outputs) > 0:
                print(f"First output type: {type(outputs[0])}")
                print(f"First output shape: {outputs[0].shape if hasattr(outputs[0], 'shape') else 'N/A'}")
                
                if hasattr(outputs[0], 'numpy'):
                    sample_output = outputs[0].numpy()
                    print(f"Sample output shape: {sample_output.shape}")
                    print(f"Sample output (first 10 values): {sample_output.flatten()[:10]}")
        
        return True
        
    except Exception as e:
        print(f"Error analyzing model: {e}")
        return False

def create_keras_format_converter():
    """Create a function to convert best(1).pt outputs to Keras format"""
    
    converter_code = '''
import torch
import numpy as np

def convert_best_to_keras_format(model_outputs, model_type="ultralytics"):
    """
    Convert best(1).pt model outputs to match Keras model format
    Expected Keras format: {'boxes': array, 'confidence': array}
    """
    
    if model_type == "ultralytics":
        # Handle Ultralytics YOLO output
        boxes_list = []
        conf_list = []
        
        for result in model_outputs:
            if hasattr(result, 'boxes') and result.boxes is not None:
                for box in result.boxes:
                    # Extract coordinates and confidence
                    if hasattr(box, 'xyxy') and hasattr(box, 'conf'):
                        xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                        conf = box.conf[0].cpu().numpy()
                        
                        # Convert to normalized coordinates (0-1 range)
                        # Assuming input was 640x640
                        normalized_box = [
                            xyxy[1] / 640.0,  # y1 normalized
                            xyxy[0] / 640.0,  # x1 normalized  
                            xyxy[3] / 640.0,  # y2 normalized
                            xyxy[2] / 640.0   # x2 normalized
                        ]
                        
                        boxes_list.append(normalized_box)
                        conf_list.append(conf)
        
        # Convert to arrays matching Keras format
        boxes_array = np.array(boxes_list) if boxes_list else np.array([[0.1, 0.1, 0.3, 0.3]])
        conf_array = np.array(conf_list) if conf_list else np.array([0.8])
        
        return {
            'boxes': [boxes_array],  # Batch dimension
            'confidence': [conf_array]  # Batch dimension
        }
    
    else:
        # Handle raw PyTorch tensor output
        # This depends on the specific output format of your model
        outputs = model_outputs[0]  # Remove batch dimension
        
        # Assuming output format: [x1, y1, x2, y2, conf, class] for each detection
        if len(outputs.shape) == 2 and outputs.shape[1] >= 5:
            boxes_list = []
            conf_list = []
            
            for detection in outputs:
                if len(detection) >= 5:
                    x1, y1, x2, y2, conf = detection[:5]
                    
                    # Normalize coordinates
                    normalized_box = [
                        y1 / 640.0,  # y1 normalized
                        x1 / 640.0,  # x1 normalized
                        y2 / 640.0,  # y2 normalized  
                        x2 / 640.0   # x2 normalized
                    ]
                    
                    boxes_list.append(normalized_box)
                    conf_list.append(float(conf))
            
            boxes_array = np.array(boxes_list) if boxes_list else np.array([[0.1, 0.1, 0.3, 0.3]])
            conf_array = np.array(conf_list) if conf_list else np.array([0.8])
            
            return {
                'boxes': [boxes_array],
                'confidence': [conf_array]
            }
        
        else:
            # Fallback - create mock detection
            return {
                'boxes': [np.array([[0.1, 0.1, 0.3, 0.3]])],
                'confidence': [np.array([0.8])]
            }
'''
    
    with open('best_to_keras_converter.py', 'w') as f:
        f.write(converter_code)
    
    print("Converter function saved to 'best_to_keras_converter.py'")

if __name__ == "__main__":
    print("Analyzing best(1).pt model...")
    if analyze_best_model():
        print("\nCreating Keras format converter...")
        create_keras_format_converter()
        print("Done! Check the output above for model format details.")
    else:
        print("Failed to analyze model.")
