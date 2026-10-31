import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(
    page_title="Disease Prediction System",
    page_icon="🏥",
    layout="wide"
)

# Title
st.title("🏥 Disease Prediction from Symptoms")
st.markdown("Enter patient symptoms to predict possible diseases.")

# --- Load Data ---
@st.cache_data
def load_data():

    data = pd.DataFrame({
        'Fever': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0],
        'Cough': [1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
        'Fatigue': [1, 0, 1, 0, 1, 1, 0, 0, 1, 0],
        'Headache': [0, 1, 0, 1, 0, 0, 1, 1, 0, 1],
        'Sore_Throat': [1, 0, 0, 1, 0, 1, 0, 0, 1, 0],
        'Difficulty_Breathing': [0, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        'Nausea': [0, 0, 0, 0, 1, 0, 1, 0, 0, 1],
        'Chills': [1, 0, 1, 0, 0, 1, 0, 0, 1, 0],
        'Disease': ['Flu', 'None', 'Pneumonia', 'Strep Throat', 'Allergy', 
                   'COVID-19', 'Migraine', 'Cold', 'Flu', 'None']
    })
    return data

# --- Train Model ---
@st.cache_data
def train_model(data):
    X = data.drop('Disease', axis=1)
    y = data['Disease']
    
    # Encode target labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Calculate accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return model, le, accuracy

# Load data
data = load_data()
model, le, accuracy = train_model(data)

# --- Sidebar ---
st.sidebar.header("About")
st.sidebar.info(
    "This app predicts diseases based on patient symptoms. "
    "The model was trained with an accuracy of "
    f"{accuracy:.2%}."
)

# --- Main Input Form ---
st.header("Patient Symptoms Input")

# Get all symptoms (excluding 'Disease')
symptoms = data.columns.tolist()
symptoms.remove('Disease')

# Organize symptoms into columns
col1, col2 = st.columns(2)
input_symptoms = {}

for i, symptom in enumerate(symptoms):
    # Format symptom name for display
    display_name = symptom.replace('_', ' ').title()
    
    # Alternate between columns
    col = col1 if i % 2 == 0 else col2
    
    input_symptoms[symptom] = col.radio(
        display_name,
        options=["No", "Yes"],
        horizontal=True
    )

# --- Prediction ---
if st.button("Predict Disease", type="primary"):
    # Convert input to model format
    input_df = pd.DataFrame([input_symptoms])
    input_df = input_df.replace({"No": 0, "Yes": 1})
    
    # Make prediction
    prediction_encoded = model.predict(input_df)
    prediction = le.inverse_transform(prediction_encoded)[0]
    
    # Get probabilities
    proba = model.predict_proba(input_df)[0]
    diseases = le.classes_
    
    # Create results dataframe
    results = pd.DataFrame({
        "Disease": diseases,
        "Probability": proba
    }).sort_values("Probability", ascending=False)
    
    # Display results
    st.success(f"**Most Likely Disease:** {prediction}")
    
    # Show probability chart
    st.subheader("Prediction Probabilities")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(results['Disease'], results['Probability'], color='skyblue')
    ax.set_xlabel('Probability')
    ax.set_title('Disease Prediction Confidence')
    st.pyplot(fig)
    
    # Show detailed probabilities
    with st.expander("See detailed probabilities"):
        st.dataframe(results.style.format({'Probability': '{:.2%}'}))

# --- Data Explorer ---
with st.expander("View Training Data"):
    st.dataframe(data)
    
    # Show disease distribution
    st.subheader("Disease Distribution in Training Data")
    disease_counts = data['Disease'].value_counts()
    st.bar_chart(disease_counts)

# --- How It Works ---
with st.expander("How this system works"):
    st.markdown("""
    1. **Input Symptoms**: Select which symptoms the patient is experiencing
    2. **Model Prediction**: The trained Random Forest model analyzes the symptoms
    3. **Results**: Shows the most likely disease and confidence percentages
    """)
    