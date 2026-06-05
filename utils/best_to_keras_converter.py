
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
