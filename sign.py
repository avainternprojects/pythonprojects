import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import cv2
import numpy as np
import os
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

class CNNSignLanguageDetector:
    def __init__(self, img_height=224, img_width=224, num_classes=26):
        self.img_height = img_height
        self.img_width = img_width
        self.num_classes = num_classes
        self.model = self.build_model()
    
    def build_model(self):
        """Build CNN model for sign language detection"""
        model = keras.Sequential([
            # First convolution layer
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.img_height, self.img_width, 3)),
            layers.MaxPooling2D(2, 2),
            
            # Second convolution layer
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),
            
            # Third convolution layer
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),
            
            # Fourth convolution layer
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),
            
            # Flatten and dense layers
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(512, activation='relu'),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def prepare_data(self, data_dir):
        """Prepare training data from directory"""
        datagen = keras.preprocessing.image.ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            validation_split=0.2
        )
        
        train_generator = datagen.flow_from_directory(
            data_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=32,
            class_mode='categorical',
            subset='training'
        )
        
        validation_generator = datagen.flow_from_directory(
            data_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=32,
            class_mode='categorical',
            subset='validation'
        )
        
        return train_generator, validation_generator
    
    def train(self, train_generator, validation_generator, epochs=50):
        """Train the model"""
        history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=validation_generator,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                keras.callbacks.ReduceLROnPlateau(patience=5)
            ]
        )
        
        return history
    
    def predict(self, image):
        """Predict sign language from image"""
        # Preprocess image
        image = cv2.resize(image, (self.img_width, self.img_height))
        image = image / 255.0
        image = np.expand_dims(image, axis=0)
        
        # Make prediction
        predictions = self.model.predict(image)
        predicted_class = np.argmax(predictions[0])
        confidence = np.max(predictions[0])
        
        return predicted_class, confidence
    
    def save_model(self, filepath):
        """Save trained model"""
        self.model.save(filepath)
    
    def load_model(self, filepath):
        """Load pre-trained model"""
        self.model = keras.models.load_model(filepath)

# Real-time detection using CNN
def real_time_cnn_detection(model_path, class_names):
    """Real-time detection using trained CNN model"""
    detector = CNNSignLanguageDetector()
    detector.load_model(model_path)
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip frame
        frame = cv2.flip(frame, 1)
        
        # Create ROI for hand detection
        height, width = frame.shape[:2]
        roi = frame[50:300, 50:300]  # Adjust ROI as needed
        
        # Predict
        predicted_class, confidence = detector.predict(roi)
        
        # Draw ROI rectangle
        cv2.rectangle(frame, (50, 50), (300, 300), (0, 255, 0), 2)
        
        # Display prediction
        sign_name = class_names[predicted_class] if predicted_class < len(class_names) else "Unknown"
        cv2.putText(frame, f'Sign: {sign_name}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'Confidence: {confidence:.2f}', (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('CNN Sign Language Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Example usage
if __name__ == "__main__":
    main()
    # For MediaPipe approach
        
    # For CNN approach (you need trained model first)
    # class_names = ['A', 'B', 'C', 'D', 'E', ...]  # Your class names
    # real_time_cnn_detection('sign_language_model.h5', class_names)