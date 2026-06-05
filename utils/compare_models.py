import numpy as np
import tensorflow as tf
import torch
import cv2
from PIL import Image

def analyze_keras_model():
    """Analyze full_acne_detector.keras output format in detail"""
    print("=== ANALYZING KERAS MODEL (full_acne_detector.keras) ===")
    
    try:
        # Load Keras model
        keras_model = tf.keras.models.load_model('full_acne_detector.keras', compile=False)
        print("✅ Keras model loaded successfully")
        
        # Create test image
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        test_input = np.expand_dims(test_img, axis=0)
        
        print(f"Input shape: {test_input.shape}")
        
        # Get model prediction
        outputs = keras_model.predict(test_input, verbose=0)
        
        print(f"Output type: {type(outputs)}")
        print(f"Output structure: {outputs}")
        
        if isinstance(outputs, dict):
            print("✅ Keras model outputs dictionary format:")
            for key, value in outputs.items():
                print(f"  {key}: {type(value)}, shape: {value.shape if hasattr(value, 'shape') else 'N/A'}")
                
                if hasattr(value, '__len__') and len(value) > 0:
                    first_item = value[0]
                    print(f"    First item shape: {first_item.shape if hasattr(first_item, 'shape') else 'N/A'}")
                    print(f"    First item type: {type(first_item)}")
                    
                    if hasattr(first_item, 'shape') and len(first_item.shape) >= 2:
                        print(f"    Sample values (first 3): {first_item[:3] if len(first_item) >= 3 else first_item}")
        
        elif isinstance(outputs, list):
            print("✅ Keras model outputs list format:")
            for i, value in enumerate(outputs):
                print(f"  Output {i}: {type(value)}, shape: {value.shape if hasattr(value, 'shape') else 'N/A'}")
        
        else:
            print(f"❓ Unexpected output format: {type(outputs)}")
            if hasattr(outputs, 'shape'):
                print(f"  Shape: {outputs.shape}")
                print(f"  Sample values: {outputs.flatten()[:10]}")
        
        return outputs
        
    except Exception as e:
        print(f"❌ Error analyzing Keras model: {e}")
        return None

def analyze_yolo_model():
    """Analyze best(1).pt YOLO output format in detail"""
    print("\n=== ANALYZING YOLO MODEL (best (1).pt) ===")
    
    try:
        # Load YOLO model
        from ultralytics import YOLO
        yolo_model = YOLO('best (1).pt')
        print("✅ YOLO model loaded successfully")
        
        # Create test image
        test_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        print(f"Input shape: {test_img.shape}")
        
        # Get model prediction
        results = yolo_model(test_img)
        
        print(f"Results type: {type(results)}")
        print(f"Results length: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"\n--- Result {i} ---")
            print(f"Type: {type(result)}")
            print(f"Attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            
            # Check boxes
            if hasattr(result, 'boxes'):
                boxes = result.boxes
                print(f"Boxes type: {type(boxes)}")
                print(f"Boxes is None: {boxes is None}")
                
                if boxes is not None and len(boxes) > 0:
                    print(f"Number of boxes: {len(boxes)}")
                    
                    # Analyze first box
                    first_box = boxes[0]
                    print(f"First box type: {type(first_box)}")
                    print(f"First box attributes: {[attr for attr in dir(first_box) if not attr.startswith('_')]}")
                    
                    # Get box data
                    if hasattr(first_box, 'xyxy'):
                        xyxy = first_box.xyxy
                        print(f"xyxy type: {type(xyxy)}, shape: {xyxy.shape}")
                        print(f"xyxy sample: {xyxy[0].cpu().numpy()}")
                    
                    if hasattr(first_box, 'conf'):
                        conf = first_box.conf
                        print(f"conf type: {type(conf)}, shape: {conf.shape}")
                        print(f"conf sample: {conf[0].cpu().numpy()}")
                    
                    if hasattr(first_box, 'cls'):
                        cls = first_box.cls
                        print(f"cls type: {type(cls)}, shape: {cls.shape}")
                        print(f"cls sample: {cls[0].cpu().numpy()}")
                else:
                    print("No boxes detected (expected for random image)")
            
            # Check names
            if hasattr(result, 'names'):
                print(f"Names: {result.names}")
            
            # Check other attributes
            if hasattr(result, 'orig_shape'):
                print(f"Original shape: {result.orig_shape}")
            
            if hasattr(result, 'speed'):
                print(f"Speed: {result.speed}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error analyzing YOLO model: {e}")
        return None

def create_realistic_test_image():
    """Create a more realistic test image with acne-like features"""
    # Create a skin-colored background
    img = np.ones((640, 640, 3), dtype=np.uint8) * [200, 150, 120]  # Skin tone
    
    # Add some darker spots (simulating acne)
    for _ in range(5):
        x = np.random.randint(50, 590)
        y = np.random.randint(50, 590)
        radius = np.random.randint(5, 15)
        color = [180, 100, 80]  # Darker skin tone
        
        cv2.circle(img, (x, y), radius, color, -1)
    
    return img

def test_with_realistic_image():
    """Test both models with a more realistic image"""
    print("\n=== TESTING WITH REALISTIC IMAGE ===")
    
    realistic_img = create_realistic_test_image()
    
    # Test Keras model
    print("\n--- Keras Model with Realistic Image ---")
    try:
        keras_model = tf.keras.models.load_model('full_acne_detector.keras', compile=False)
        keras_input = np.expand_dims(realistic_img, axis=0)
        keras_outputs = keras_model.predict(keras_input, verbose=0)
        
        if isinstance(keras_outputs, dict):
            print("Keras detections found:")
            for key, value in keras_outputs.items():
                if hasattr(value, '__len__') and len(value) > 0:
                    first_batch = value[0]
                    print(f"  {key}: {len(first_batch)} detections")
                    if len(first_batch) > 0:
                        print(f"    Sample: {first_batch[0]}")
        else:
            print(f"Keras output: {type(keras_outputs)}")
            
    except Exception as e:
        print(f"Keras test error: {e}")
    
    # Test YOLO model
    print("\n--- YOLO Model with Realistic Image ---")
    try:
        from ultralytics import YOLO
        yolo_model = YOLO('best (1).pt')
        yolo_results = yolo_model(realistic_img)
        
        for i, result in enumerate(yolo_results):
            if hasattr(result, 'boxes') and result.boxes is not None and len(result.boxes) > 0:
                print(f"YOLO detections found: {len(result.boxes)}")
                for j, box in enumerate(result.boxes):
                    if hasattr(box, 'xyxy') and hasattr(box, 'conf'):
                        xyxy = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        print(f"  Detection {j}: xyxy={xyxy}, conf={conf}")
            else:
                print("No YOLO detections")
                
    except Exception as e:
        print(f"YOLO test error: {e}")

def main():
    print("🔍 COMPREHENSIVE MODEL OUTPUT ANALYSIS")
    print("=" * 50)
    
    # Analyze both models
    keras_outputs = analyze_keras_model()
    yolo_outputs = analyze_yolo_model()
    
    # Test with realistic image
    test_with_realistic_image()
    
    print("\n" + "=" * 50)
    print("📊 ANALYSIS COMPLETE")
    print("\nNext steps:")
    print("1. Compare the output formats above")
    print("2. Create proper converter based on actual output structures")
    print("3. Test the converter with real data")

if __name__ == "__main__":
    main()
