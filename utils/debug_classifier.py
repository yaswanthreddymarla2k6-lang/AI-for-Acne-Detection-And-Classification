import numpy as np
import tensorflow as tf
import cv2

def debug_classifier():
    """Debug the classifier model to understand why only 'whiteheads' is output"""
    
    print("🔍 DEBUGGING CLASSIFIER MODEL")
    print("=" * 50)
    
    try:
        # Load classifier model
        classifier = tf.keras.models.load_model('acne_detection_model.keras')
        print("✅ Classifier model loaded successfully")
        
        # Check model summary
        print("\n📊 MODEL STRUCTURE:")
        classifier.summary()
        
        # Check input shape
        print(f"\n📐 Input shape: {classifier.input_shape}")
        print(f"📐 Output shape: {classifier.output_shape}")
        
        # Create test data
        test_img = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
        test_input = np.expand_dims(test_img, axis=0).astype('float32') / 255.0
        
        print(f"\n🧪 Test input shape: {test_input.shape}")
        print(f"🧪 Test input min/max: {test_input.min():.3f} / {test_input.max():.3f}")
        
        # Get prediction
        prediction = classifier.predict(test_input, verbose=0)
        
        print(f"\n📈 Raw prediction: {prediction}")
        print(f"📈 Prediction shape: {prediction.shape}")
        print(f"📈 Prediction values: {prediction[0]}")
        
        # Get predicted class
        categories = ['Blackheads', 'Cyst', 'Papules', 'Pustules', 'Whiteheads']
        predicted_class_idx = np.argmax(prediction[0])
        predicted_class = categories[predicted_class_idx]
        
        print(f"\n🏷️ Predicted class index: {predicted_class_idx}")
        print(f"🏷️ Predicted class: {predicted_class}")
        print(f"🏷️ Confidence: {prediction[0][predicted_class_idx]:.3f}")
        
        # Check all class probabilities
        print(f"\n📋 All class probabilities:")
        for i, (category, prob) in enumerate(zip(categories, prediction[0])):
            print(f"  {i}: {category} - {prob:.3f}")
        
        return classifier, categories
        
    except Exception as e:
        print(f"❌ Error debugging classifier: {e}")
        return None, None

def test_multiple_inputs(classifier, categories):
    """Test classifier with multiple different inputs"""
    
    print("\n🔄 TESTING MULTIPLE INPUTS")
    print("=" * 50)
    
    # Test with different random images
    for i in range(5):
        test_img = np.random.randint(0, 255, (150, 150, 3), dtype=np.uint8)
        test_input = np.expand_dims(test_img, axis=0).astype('float32') / 255.0
        
        prediction = classifier.predict(test_input, verbose=0)
        predicted_class_idx = np.argmax(prediction[0])
        predicted_class = categories[predicted_class_idx]
        
        print(f"Test {i+1}: {predicted_class} (conf: {prediction[0][predicted_class_idx]:.3f})")

if __name__ == "__main__":
    classifier, categories = debug_classifier()
    
    if classifier is not None:
        test_multiple_inputs(classifier, categories)
    
    print("\n" + "=" * 50)
    print("🎯 DEBUGGING COMPLETE")
