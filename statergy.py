import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Union, List
from sklearn.preprocessing import StandardScaler as SklearnStandardScaler
from sklearn.preprocessing import MinMaxScaler as SklearnMinMaxScaler

class PreprocessingStrategy(ABC):
    """Abstract base class for preprocessing strategies"""
    @abstractmethod
    def process(self, data: Union[np.ndarray, pd.DataFrame, List]) -> Union[np.ndarray, pd.DataFrame]:
        """
        Process the input data
        
        Args:
            data: Input data to be processed (array-like or DataFrame)
            
        Returns:
            Processed data in the same format as input
        """
        pass

class StandardScalerStrategy(PreprocessingStrategy):
    """Standardization (Z-score normalization) strategy"""
    def __init__(self, with_mean=True, with_std=True):
        self.with_mean = with_mean
        self.with_std = with_std
        
    def process(self, data):
        if isinstance(data, pd.DataFrame):
            return (data - data.mean()) / data.std()
        elif isinstance(data, (np.ndarray, list)):
            data = np.array(data)
            mean = data.mean() if self.with_mean else 0
            std = data.std() if self.with_std else 1
            return (data - mean) / std
        else:
            raise TypeError("Input data must be DataFrame, numpy array, or list")

class MinMaxScalerStrategy(PreprocessingStrategy):
    """Min-Max normalization strategy"""
    def __init__(self, feature_range=(0, 1)):
        self.feature_range = feature_range
        
    def process(self, data):
        if isinstance(data, pd.DataFrame):
            min_val = data.min()
            max_val = data.max()
            return (data - min_val) / (max_val - min_val) * \
                   (self.feature_range[1] - self.feature_range[0]) + self.feature_range[0]
        elif isinstance(data, (np.ndarray, list)):
            data = np.array(data)
            min_val = data.min()
            max_val = data.max()
            return (data - min_val) / (max_val - min_val) * \
                   (self.feature_range[1] - self.feature_range[0]) + self.feature_range[0]
        else:
            raise TypeError("Input data must be DataFrame, numpy array, or list")

class SklearnAdapterStrategy(PreprocessingStrategy):
    """Adapter for scikit-learn preprocessing classes"""
    def __init__(self, sklearn_preprocessor):
        self.preprocessor = sklearn_preprocessor
        
    def process(self, data):
        if isinstance(data, pd.DataFrame):
            transformed = self.preprocessor.fit_transform(data)
            return pd.DataFrame(transformed, columns=data.columns, index=data.index)
        return self.preprocessor.fit_transform(data)

class DataPreprocessor:
    """Context class that uses the selected strategy"""
    def __init__(self, strategy: PreprocessingStrategy = None):
        """
        Initialize with optional strategy
        
        Args:
            strategy: Preprocessing strategy to use
        """
        self.strategy = strategy or StandardScalerStrategy()
        
    def set_strategy(self, strategy: PreprocessingStrategy):
        """Change the preprocessing strategy at runtime"""
        self.strategy = strategy
        
    def transform(self, data: Union[np.ndarray, pd.DataFrame, List]) -> Union[np.ndarray, pd.DataFrame]:
        """
        Apply the selected preprocessing strategy
        
        Args:
            data: Input data to be processed
            
        Returns:
            Processed data in the same format as input
            
        Raises:
            ValueError: If data is empty or invalid
        """
        if data is None or len(data) == 0:
            raise ValueError("Input data cannot be empty")
            
        return self.strategy.process(data)

# Example Usage
if __name__ == "__main__":
    # Create sample data
    numeric_data = [1, 2, 3, 4, 5]
    df_data = pd.DataFrame({
        'feature1': [10, 20, 30, 40, 50],
        'feature2': [0.1, 0.2, 0.3, 0.4, 0.5]
    })
    
    # Initialize preprocessor with default strategy (StandardScaler)
    preprocessor = DataPreprocessor()
    
    print("=== Standard Scaling ===")
    # Process list data
    scaled_list = preprocessor.transform(numeric_data)
    print(f"List input: {numeric_data}")
    print(f"Scaled list: {scaled_list}")
    
    # Process DataFrame
    scaled_df = preprocessor.transform(df_data)
    print("\nDataFrame input:")
    print(df_data)
    print("\nScaled DataFrame:")
    print(scaled_df)
    
    # Change to MinMax strategy at runtime
    print("\n=== MinMax Scaling ===")
    preprocessor.set_strategy(MinMaxScalerStrategy(feature_range=(-1, 1)))
    minmax_scaled = preprocessor.transform(numeric_data)
    print(f"MinMax scaled: {minmax_scaled}")
    
    # Use sklearn adapter
    print("\n=== Sklearn StandardScaler ===")
    sklearn_strategy = SklearnAdapterStrategy(SklearnStandardScaler())
    preprocessor.set_strategy(sklearn_strategy)
    sklearn_scaled = preprocessor.transform(df_data)
    print(sklearn_scaled)