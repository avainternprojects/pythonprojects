import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler

# Load the dataset (assuming you have a CSV file)
# Dataset should have features like time, amount, V1-V28 (PCA components), and Class (0=legit, 1=fraud)
def load_data(filepath):
    data = pd.read_csv(filepath)
    return data

# Exploratory Data Analysis
def explore_data(data):
    print("Dataset shape:", data.shape)
    print("\nClass distribution:")
    print(data['Class'].value_counts())
    print("\nFraud percentage: {:.4f}%".format(data['Class'].mean()*100))
    
    # Plot class distribution
    plt.figure(figsize=(8,6))
    sns.countplot(x='Class', data=data)
    plt.title('Class Distribution (0=Legitimate, 1=Fraud)')
    plt.show()
    
    # Plot transaction amounts
    plt.figure(figsize=(10,6))
    plt.subplot(1,2,1)
    sns.boxplot(x='Class', y='Amount', data=data)
    plt.title('Transaction Amount by Class')
    plt.subplot(1,2,2)
    sns.histplot(data[data['Class']==0]['Amount'], bins=50, color='blue', label='Legitimate', kde=True)
    sns.histplot(data[data['Class']==1]['Amount'], bins=50, color='red', label='Fraud', kde=True)
    plt.legend()
    plt.title('Amount Distribution by Class')
    plt.tight_layout()
    plt.show()

# Preprocess the data
def preprocess_data(data):
    # Scale the 'Amount' and 'Time' features
    scaler = StandardScaler()
    data['Amount'] = scaler.fit_transform(data['Amount'].values.reshape(-1, 1))
    data['Time'] = scaler.fit_transform(data['Time'].values.reshape(-1, 1))
    
    # Separate features and target
    X = data.drop('Class', axis=1)
    y = data['Class']
    
    return X, y

# Handle class imbalance using SMOTE
def balance_data(X, y):
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)
    return X_res, y_res

# Train and evaluate model
def train_and_evaluate(X, y):
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Initialize and train Random Forest classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Evaluate model
    print("\nModel Evaluation:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred))
    print("Recall:", recall_score(y_test, y_pred))
    print("F1 Score:", f1_score(y_test, y_pred))
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, 
                xticklabels=['Legitimate', 'Fraud'], 
                yticklabels=['Legitimate', 'Fraud'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.show()
    
    return model

# Main function
def main():
    # Load data (replace with your dataset path)
    data = load_data(r"C:\Users\vijay\Downloads\creditcard.csv\creditcard.csv")
    
    # Explore data
    explore_data(data)
    
    # Preprocess data
    X, y = preprocess_data(data)
    
    # Handle class imbalance (optional - can try with and without SMOTE)
    X_res, y_res = balance_data(X, y)
    
    # Train and evaluate model
    model = train_and_evaluate(X_res, y_res)

if __name__ == "__main__":
    main()