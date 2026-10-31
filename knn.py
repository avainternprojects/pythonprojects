import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix,ConfusionMatrixDisplay,roc_curve,auc


df=pd.read_csv(r"C:\Users\vijay\OneDrive\Desktop\python projects\data.csv")

targets="diagnosis"
imputer=SimpleImputer(strategy='mean')
x=imputer.fit_transform(df.drop(targets,axis=1))
y=df[targets]

x_train,x_test,y_train,y_test = train_test_split(x,y, test_size=0.3)

model=KNeighborsClassifier()
model.fit (x_train, y_train)

print("Accuracy:",model.score(x_test,y_test))

y_pred=model.predict(x_test)
ConfusionMatrixDisplay.from_estimator(model, x_test, y_test)
plt.title("confusion matrix")
plt.show()

if len(model.classes_)==2:
    y_prob=model.predict_proba(x_test)[:,1]
    fpr, tpr, _ = roc_curve(y_test,y_prob,pos_label=model.classes_[1])

    plt.figure(fpr, tpr, label=f'AUC={auc(fpr,tpr):.2f}')
    plt.plot([0,1],[0,1],'k--')
    plt.xlabel("false positive rate")
    plt.ylabel("true positive rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.plot()
else:
    print("roc curve skipped")