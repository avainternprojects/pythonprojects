import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
from sklearn.pipeline import Pipeline

class ModelFactory:
    def __init__(self):
        """Initialize with default models and their configurations"""
        self.available_models = {
            "random_forest": {
                "model": RandomForestClassifier,
                "default_params": {"n_estimators": 100, "random_state": 42}
            },
            "svm": {
                "model": SVC,
                "default_params": {"kernel": "rbf", "random_state": 42}
            }
        }
    
    def get_model(self, model_type, params=None):
        """
        Get a configured machine learning model
        
        Args:
            model_type (str): Type of model ('random_forest' or 'svm')
            params (dict): Optional parameters to override defaults
            
        Returns:
            sklearn model instance
        """
        if model_type not in self.available_models:
            raise ValueError(f"Unknown model type. Available options: {list(self.available_models.keys())}")
            
        model_info = self.available_models[model_type]
        model_class = model_info["model"]
        model_params = model_info["default_params"].copy()
        
        if params:
            model_params.update(params)
            
        return model_class(**model_params)
    
    def get_model_with_pipeline(self, model_type, params=None):
        """
        Get a model with preprocessing pipeline (scaling for SVM)
        
        Args:
            model_type (str): Type of model
            params (dict): Optional parameters
            
        Returns:
            sklearn Pipeline
        """
        model = self.get_model(model_type, params)
        
        # Add standard scaling for SVM
        if model_type == "svm":
            return Pipeline([
                ('scaler', StandardScaler()),
                ('classifier', model)
            ])
        return model


class ModelTrainer:
    def __init__(self, test_size=0.2, random_state=42):
        """
        Initialize model trainer
        
        Args:
            test_size (float): Size of test set (0-1)
            random_state (int): Random seed for reproducibility
        """
        self.test_size = test_size
        self.random_state = random_state
        self.factory = ModelFactory()
    
    def load_data(self):
        """Load sample iris dataset"""
        data = load_iris()
        self.X = data.data
        self.y = data.target
        self.feature_names = data.feature_names
        self.target_names = data.target_names
        
    def split_data(self):
        """Split data into train/test sets"""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, 
            test_size=self.test_size, 
            random_state=self.random_state,
            stratify=self.y
        )
    
    def train_model(self, model_type, params=None):
        """
        Train a specified model
        
        Args:
            model_type (str): Type of model
            params (dict): Optional model parameters
            
        Returns:
            Trained model
        """
        model = self.factory.get_model_with_pipeline(model_type, params)
        model.fit(self.X_train, self.y_train)
        return model
    
    def evaluate_model(self, model):
        """Evaluate model performance"""
        y_pred = model.predict(self.X_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        report = classification_report(self.y_test, y_pred, target_names=self.target_names)
        
        print(f"Model Accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(report)
        
        return accuracy, report


# Example Usage
if __name__ == "__main__":
    # Initialize components
    trainer = ModelTrainer()
    
    # Load and prepare data
    trainer.load_data()
    trainer.split_data()
    
    # Train and evaluate different models
    print("=== Random Forest ===")
    rf_model = trainer.train_model("random_forest", {"n_estimators": 200})
    trainer.evaluate_model(rf_model)
    
    print("\n=== SVM ===")
    svm_model = trainer.train_model("svm", {"kernel": "linear"})
    trainer.evaluate_model(svm_model)