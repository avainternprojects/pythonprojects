import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression  # Faster than SVM
from sklearn.metrics import accuracy_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import seaborn as sns

# 1. Load Data (with error handling)
try:
    df = pd.read_csv(r"C:\Users\vijay\OneDrive\Desktop\python projects\IMDB Dataset.csv\IMDB Dataset.csv")
    df = df.sample(50000)  # Smaller dataset for testing
    print("Data loaded. Samples:", len(df))
except Exception as e:
    print("Error loading file:", e)
    exit()

# 2. Preprocess
df['sentiment'] = df['sentiment'].map({'positive': 1, 'negative': 0})

# 3. Split Data
X = df['review']
y = df['sentiment']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. TF-IDF (smaller features)
tfidf = TfidfVectorizer(max_features=50000)  # Reduced features
print("Transforming text...")
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# 5. Train Model (faster alternative)
print("Training model...")
model = LogisticRegression(max_iter=50000)  # Faster training
model.fit(X_train_tfidf, y_train)
print("Model trained!")  # Confirm training completes

# 6. Evaluate
try:
    y_pred = model.predict(X_test_tfidf)
    print("\nAccuracy:", accuracy_score(y_test, y_pred))
except Exception as e:
    print("Evaluation failed:", e)


# 7. Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()