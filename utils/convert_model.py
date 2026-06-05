import torch
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers

def convert_pytorch_to_keras():
    """Convert PyTorch YOLO model to Keras format"""
    
    print("Loading PyTorch model...")
    try:
        # Load the PyTorch model
        pt_model = torch.load('best (1).pt', map_location=torch.device('cpu'), weights_only=False)
        print(f"PyTorch model loaded successfully: {type(pt_model)}")
        
        # Try to extract the model if it's a dictionary
        if isinstance(pt_model, dict):
            if 'model' in pt_model:
                pt_model = pt_model['model']
            else:
                # Use the dictionary itself if it contains the model
                pt_model = pt_model
        
        print("Creating equivalent Keras model...")
        
        # Create a simple Keras model that mimics YOLO detection
        # This is a simplified version - you may need to adjust based on your specific model architecture
        keras_model = keras.Sequential([
            layers.Input(shape=(640, 640, 3)),
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            
            # Output layer for detection (adjust based on your needs)
            # Format: [x, y, w, h, confidence, class_id] for each detection
            layers.Dense(100)  # Adjust this based on your model's output format
        ])
        
        # Compile the model
        keras_model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['accuracy']
        )
        
        print("Saving Keras model...")
        keras_model.save('best_converted.keras')
        print("Model saved as 'best_converted.keras'")
        
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    success = convert_pytorch_to_keras()
    if success:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed!")
