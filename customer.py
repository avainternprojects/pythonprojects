import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns

st.set_page_config(page_title="Customer Segmentation", layout="wide")

st.title("Mall Customer Segmentation")
st.markdown(""" This app performs customer segmentation using K-Means Clustering On thr Mall Customers dataset """ )

@st.cache_data
def load_data():
    return pd.read_csv(r"C:\Users\vijay\OneDrive\Desktop\python projects\Mall_Customers.csv")
df=load_data()
st.sidebar.header("Controls")
show_data=st.sidebar.checkbox("Show Raw data",value=False)
k_value=st.sidebar.slider("Number of Clusters (k)",2,10,5)

if show_data:
    st.subheader("Raw Data")
    st.dataframe(df)
x=df[['Annual Income (k$)','Spending Score (1-100)']]

scaler=StandardScaler()
x_scaled=scaler.fit_transform(x)

col1,col2=st.columns(2)

with col1:
    st.subheader("Elbow method for optimal k")

    wcss=[]
    for k in range(1, 11):
        kmeans=KMeans(n_clusters=k,random_state=42)
        kmeans.fit(x_scaled)
        wcss.append(kmeans.inertia_)
    
    fig1, ax1 =plt.subplots()
    ax1.plot(range(1,11),wcss,marker='o')
    ax1.set_title('Elbow Method')
    ax1.set_xlabel('Number of clusters(k)')
    ax1.set_ylabel('WCSS')
    st.pyplot(fig1)

kmeans=KMeans(n_clusters=k_value,random_state=42)
clusters=kmeans.fit_predict(x_scaled)
df['Cluster']=clusters

with col2:
    st.subheader(f"customer segmentation (k={k_value}) ")
    fig2, ax2 =plt.subplots(figsize=(10,6))
    sns.scatterplot(data=df,x='Annual Income (k$)',y='Spending Score (1-100)',hue='Cluster', palette='viridis', s=100, ax=ax2)
    ax2.set_title(f'customer segmentation (k={k_value})')
    st.pyplot(fig2)

st.subheader('Cluster Analysis')

numeric_cols=df.select_dtypes(include=['int64','float64']).columns.tolist()
if 'CustomerID' in numeric_cols:
    numeric_cols.remove('CustomerID')

cluster_means=df.groupby('Cluster')[numeric_cols].mean()
st.dataframe(cluster_means.style.background_gradient(cmap='Blues'))                                    



st.markdown("----")
st.markdown(""" ** Interpretation Guise:**
- **High Income,Low Spending**:Potential Targets for Loyalty Programs
-**High Income, High Spending**:Premium Customers
-**Low Income, High Spending**:Budget-conscious but frequent Shoppers""")