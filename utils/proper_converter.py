import numpy as np

def convert_yolo_to_keras_format(yolo_results):
    """
    Convert YOLO results to exactly match Keras model output format
    
    Keras format:
    {
        'boxes': array(1, 100, 4) - [y1, x1, y2, x2] normalized, -1 for no detection
        'confidence': array(1, 100) - confidence scores, -1 for no detection
        'classes': array(1, 100) - class indices, -1 for no detection
        'num_detections': array(1,) - total number of detections
    }
    """
    
    # Initialize arrays with -1 (no detection)
    boxes_array = np.full((1, 100, 4), -1.0, dtype=np.float32)
    conf_array = np.full((1, 100), -1.0, dtype=np.float32)
    classes_array = np.full((1, 100), -1, dtype=np.int32)
    num_detections = 0
    
    # Process YOLO results
    for result in yolo_results:
        if hasattr(result, 'boxes') and result.boxes is not None:
            boxes = result.boxes
            
            for i, box in enumerate(boxes):
                if i >= 100:  # Limit to 100 detections like Keras model
                    break
                
                # Extract YOLO box data
                if hasattr(box, 'xyxy') and hasattr(box, 'conf') and hasattr(box, 'cls'):
                    xyxy = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
                    conf = box.conf[0].cpu().numpy()
                    cls = int(box.cls[0].cpu().numpy())
                    
                    # Convert to Keras format: [y1, x1, y2, x2] normalized
                    # YOLO outputs are absolute coordinates, need to normalize to 0-1
                    normalized_box = [
                        xyxy[1] / 640.0,  # y1 normalized
                        xyxy[0] / 640.0,  # x1 normalized
                        xyxy[3] / 640.0,  # y2 normalized
                        xyxy[2] / 640.0   # x2 normalized
                    ]
                    
                    # Fill arrays
                    boxes_array[0, i] = normalized_box
                    conf_array[0, i] = float(conf)
                    classes_array[0, i] = cls
                    num_detections += 1
    
    # Set num_detections
    num_detections_array = np.array([num_detections], dtype=np.int32)
    
    return {
        'boxes': boxes_array,
        'confidence': conf_array,
        'classes': classes_array,
        'num_detections': num_detections_array
    }

def test_converter():
    """Test the converter with sample data"""
    print("🧪 TESTING YOLO TO KERAS CONVERTER")
    
    # Test with empty results first
    empty_results = []
    empty_format = convert_yolo_to_keras_format(empty_results)
    
    print("Empty results format:")
    for key, value in empty_format.items():
        print(f"  {key}: {value.shape}, sample: {value.flatten()[:5] if value.size > 0 else 'empty'}")
    
    print(f"Number of detections: {empty_format['num_detections'][0]}")
    
    return empty_format

if __name__ == "__main__":
    test_converter()
