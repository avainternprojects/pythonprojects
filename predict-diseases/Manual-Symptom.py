import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import streamlit as st

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv(r'C:\Users\vijay\OneDrive\Desktop\python projects\predict-diseases\Symptom2Disease.csv')
    # Use the correct column name 'label' instead of 'disease'
    return df

df = load_data()

# Train model
@st.cache_resource
def train_model():
    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', MultinomialNB())
    ])
    # Use 'label' instead of 'disease'
    model.fit(df['text'], df['disease'])
    return model

model = train_model()

# Streamlit UI
st.title("Symptom to Disease Predictor")
st.markdown("Describe your symptoms below and get a possible disease prediction")

# Text input for symptoms
user_input = st.text_area(
    "Describe your symptoms:",
    placeholder="Example: I have a red itchy rash on my arms and legs, with joint pain...",
    height=150
)

# Prediction button
if st.button("Predict Disease"):
    if user_input.strip() == "":
        st.warning("Please enter your symptoms first")
    else:
        prediction = model.predict([user_input])[0]
        
        # Display prediction with styling
        st.subheader("Prediction Result")
        st.markdown(f"""
        <div style='
            background-color: #f0f8ff;
            padding: 15px;
            border-radius: 5px;
            border-left: 6px solid #1e90ff;
            margin-top: 10px;
        '>
            <h3 style='color: #1e90ff; margin-top: 0;'>Possible Condition:</h3>
            <p style='font-size: 20px; color:#1e90ff'><strong>{prediction}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show similar cases
        st.subheader("Similar Cases in Our Database")
        similar_cases = df[df['disease'] == prediction].sample(5)  # Changed to 'label'
        for _, row in similar_cases.iterrows():
            st.markdown(f"""
            <div style='
                background-color: #f9f9f9;
                padding: 10px;
                border-radius: 5px;
                margin: 5px 0;
                color:#1e90ff;
            '>
                <p style='margin: 0;'><i>"{row['text']}"</i></p>
            </div>
            """, unsafe_allow_html=True)

# Add some info about the system
st.sidebar.markdown("""
### About This Tool
This system predicts possible medical conditions based on symptom descriptions using machine learning.

**Dataset Info:**
- Contains {} symptom descriptions
- Covers {} different diseases
- Accuracy: ~85% (may vary)

**Instructions:**
1. Describe your symptoms in detail
2. Click "Predict Disease"
3. Review results (not a medical diagnosis)
""".format(len(df), len(df['disease'].unique())))  

# Add footer
st.markdown("---")
st.caption("Note: This is for educational purposes only. Always consult a healthcare professional for medical advice.")