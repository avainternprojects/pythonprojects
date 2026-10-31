# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# Load the dataset
url = r"C:\Users\vijay\OneDrive\Desktop\python projects\Mall_Customers.csv"
df = pd.read_csv(url)

# Display basic information
print("Dataset shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nData information:")
print(df.info())
print("\nDescriptive statistics:")
print(df.describe())

# Rename columns for easier access
df.rename(columns={'Annual Income (k$)': 'Income', 'Spending Score (1-100)': 'SpendingScore'}, inplace=True)

# Exploratory Data Analysis
plt.figure(figsize=(15, 5))

# Age distribution
plt.subplot(1, 3, 1)
sns.histplot(df['Age'], bins=20, kde=True)
plt.title('Age Distribution')

# Income distribution
plt.subplot(1, 3, 2)
sns.histplot(df['Income'], bins=20, kde=True)
plt.title('Income Distribution')

# Spending score distribution
plt.subplot(1, 3, 3)
sns.histplot(df['SpendingScore'], bins=20, kde=True)
plt.title('Spending Score Distribution')

plt.tight_layout()
plt.show()

# Gender distribution
plt.figure(figsize=(6, 4))
sns.countplot(x='Gender', data=df)
plt.title('Gender Distribution')
plt.show()

# Feature selection for clustering
X = df[['Income', 'SpendingScore']]  # We'll use these two features for segmentation

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Determine optimal number of clusters using Elbow Method
wcss = []  # Within-Cluster-Sum-of-Squares
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
    kmeans.fit(X_scaled)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(10, 5))
plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
plt.title('Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()

# Silhouette Score analysis
silhouette_scores = []
for n_cluster in range(2, 11):
    kmeans = KMeans(n_clusters=n_cluster, init='k-means++', random_state=42)
    kmeans.fit(X_scaled)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

plt.figure(figsize=(10, 5))
plt.plot(range(2, 11), silhouette_scores, marker='o')
plt.title('Silhouette Score')
plt.xlabel('Number of clusters')
plt.ylabel('Score')
plt.show()

# Based on the plots, let's choose 5 clusters
n_clusters = 5

# Apply K-Means clustering
kmeans = KMeans(n_clusters=n_clusters, init='k-means++', random_state=42)
clusters = kmeans.fit_predict(X_scaled)

# Add cluster labels to the dataframe
df['Cluster'] = clusters

# Visualize the clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Income', y='SpendingScore', hue='Cluster', data=df, palette='viridis', s=100)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red', marker='X', label='Centroids')
plt.title('Customer Segments')
plt.xlabel('Annual Income (k$)')
plt.ylabel('Spending Score (1-100)')
plt.legend()
plt.show()

# Analyze the clusters
cluster_summary = df.groupby('Cluster').agg({
    'Age': 'mean',
    'Income': 'mean',
    'SpendingScore': 'mean',
    'Gender': lambda x: x.value_counts().index[0]
}).reset_index()

print("\nCluster Summary:")
print(cluster_summary)

# Interpretation of clusters
cluster_names = {
    0: "High Income, Low Spending",
    1: "Moderate Income, Moderate Spending",
    2: "High Income, High Spending",
    3: "Low Income, High Spending",
    4: "Low Income, Low Spending"
}

df['Segment'] = df['Cluster'].map(cluster_names)

# Final visualization with segment names
plt.figure(figsize=(12, 7))
sns.scatterplot(x='Income', y='SpendingScore', hue='Segment', data=df, palette='Set2', s=100)
plt.title('Customer Segmentation based on Income and Spending', pad=20)
plt.xlabel('Annual Income (k$)', labelpad=15)
plt.ylabel('Spending Score (1-100)', labelpad=15)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()