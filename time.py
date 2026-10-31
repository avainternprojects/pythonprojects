import time
from functools import wraps
import logging
from typing import List, Union
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def timer_decorator(print_output: bool = False):
    """
    Decorator factory that times function execution and optionally logs output
    
    Args:
        print_output (bool): Whether to log function return value
    """
    def decorator(func):
        @wraps(func)  # Preserves function metadata
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()  # Higher precision timing
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            elapsed = end_time - start_time
            logger.info(f"{func.__name__} executed in {elapsed:.4f} seconds")
            
            if print_output and result is not None:
                logger.debug(f"Function output: {str(result)[:100]}...")  # Truncate long outputs
            
            return result
        return wrapper
    return decorator

class MLModel:
    def __init__(self):
        self.model = RandomForestClassifier()
        self._is_trained = False

    @timer_decorator(print_output=True)
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the model with timing"""
        logger.info(f"Training on {len(X)} samples...")
        time.sleep(0.5)  # Simulate training time
        self.model.fit(X, y)
        self._is_trained = True
        return "Training completed successfully"

    @timer_decorator()
    def predict(self, X: Union[np.ndarray, List]) -> np.ndarray:
        """Make predictions with timing"""
        if not self._is_trained:
            raise RuntimeError("Model must be trained before prediction")
        
        if isinstance(X, list):
            X = np.array(X)
            
        time.sleep(0.2)  # Simulate prediction time
        return self.model.predict(X)

    @timer_decorator(print_output=False)
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> float:
        """Evaluate model performance with timing"""
        if not self._is_trained:
            raise RuntimeError("Model must be trained before evaluation")
            
        time.sleep(0.3)  # Simulate evaluation time
        return self.model.score(X, y)

# Example usage
if __name__ == "__main__":
    # Generate sample data
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    
    # Initialize and use model
    model = MLModel()
    
    # Train with timing
    model.train(X, y)
    
    # Predict with timing
    sample = [[0.5] * 20]  # Sample input
    predictions = model.predict(sample)
    print(f"Predictions: {predictions}")
    
    # Evaluate with timing
    accuracy = model.evaluate(X, y)
    print(f"Model accuracy: {accuracy:.2f}")