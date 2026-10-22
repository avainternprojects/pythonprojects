import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from sklearn.inspection import DecisionBoundaryDisplay

df=pd.read_csv("Iris.csv")
X=df.drop("Species", axis=1)
Y=df["Species"]

X_train,X_test,Y_train,Y_test= train_test_split(X,Y, test_size=0.3, random_state=42)

model=SVC(kernel='rbf')
model.fit(X_train,Y_train)
Y_pred=model.predict(X_test)
print("Accuracy:",accuracy_score(Y_test,Y_pred))

X_2d=X.iloc[:,:2]
model_2d=SVC(kernel='rbf').fit(X_2d,Y)
DecisionBoundaryDisplay.from_estimator(
    model_2d,X_2d,response_method="predict", alpha=0.5
)
plt.scatter(X_2d.iloc[:,0],X_2d.iloc[:,1],edgecolor='k')
plt.xlabel("spal lenght")
plt.ylabel("spal width")
plt.title("SVM Decission Boundary")
plt.show()

