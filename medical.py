import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Insurence Cost predictor", layout="wide")

st.title("MEDICAL INSURENCE COST PREDICTION")
st.write("""This app predicts the medical incurence costs based on demographic and health factors""")

st.sidebar.header("Input Parameters")

@st.cache_data
def load_data():
    return pd.read_csv(r"C:\Users\vijay\OneDrive\Desktop\python projects\insurance.csv")
df=load_data()

if st.sidebar.checkbox("Show Visualizations"):
    st.subheader("Data Visualizations")

    col1, col2 =st.columns(2)
    with col1:
        st.write("Insurence Charges by checking smoking status")
        fig1= plt.figure(figsize=(8,4))
        sns.boxenplot(x='smoker', y='charges', data=df)
        st.pyplot(fig1)
    with col2:
        st.write("  BMI VS Charges by smoking status")
        fig2= plt.figure(figsize=(8,4))
        sns.boxenplot(x='bmi', y='charges', hue='smoker', data=df)
        st.pyplot(fig2)
x=df.drop('charges', axis=1)
y=df['charges']

preprocessor=ColumnTransformer([
    ('num', StandardScaler(),['age','bmi','children']),
    ('cat', OneHotEncoder(),['sex','smoker','region'])
])
x_processed=preprocessor.fit_transform(x)

@st.cache_resource
def train_model():
    x_train,x_test,y_train,y_test=train_test_split(x_processed, y, test_size=0.2, random_state=42)
    model=RandomForestRegressor(n_estimators=100)
    model.fit(x_train,y_train)
    return model, x_test, y_test
model, x_test, y_test=train_model()

if st.sidebar.checkbox("show model performance"):
    st.subheader("Model Performance")
    y_pred=model.predict(x_test)

    col1,col2=st.columns(2)
    col1.metric("R² Score",f"{r2_score(y_test,y_pred):.3f}")
    col2.metric("Mean Absolute Error",f"${mean_absolute_error(y_test,y_pred):.2f})")

    st.write("Feature Impoertance")
    features=['age','bmi','children'] + list(preprocessor.named_transformers_['cat'].get_feature_names_out())

    fig3= plt.figure(figsize=(10,5))
    sns.barplot(x=model.feature_importances_, y=features)
    st.pyplot(fig3)

st.subheader("make prediction")
with st.form("prediction_form"):
    col1,col2,col3=st.columns(3)

    with col1:
        age=st.slider("Age",18,70,30)
        bmi=st.slider("BMI",15.0,50.0,25.0)
        children=st.slider("Children",0,10,0)
    with col2:
        sex=st.selectbox("sex",["male","female"])
        smoker=st.selectbox("smoker",["yes","no"])
    with col3:
        region=st.selectbox("Region",["southwest","southeast","northwest","northeast"])
    submitted=st.form_submit_button("Predict Incurence cost")

if submitted:
    input_data=pd.DataFrame([{
        'age':age,
        'sex':sex,
        'bmi':bmi,
        'children':children,
        'smoker':smoker,
        'region':region
        
    }])

    input_processed=preprocessor.transform(input_data)
    prediction=model.predict(input_processed)

    st.success(f"Predicted Inscurence Cost:${prediction[0]:.2f}")
        