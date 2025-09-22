import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, accuracy_score, mean_squared_error
import pickle
import os

data_path = os.path.join('model', 'training_reviews.xlsx')
model_dir = 'model'
os.makedirs(model_dir, exist_ok=True)

df = pd.read_excel(data_path)

vectorizer = TfidfVectorizer(max_features=500)
X = vectorizer.fit_transform(df['Текст']).toarray()

y_is_fake = df['Is_Fake']
y_fake_score = df['Fake_Score']

X_train, X_test, y_train_fake, y_test_fake = train_test_split(X, y_is_fake, test_size=0.25, random_state=42)
_, _, y_train_score, y_test_score = train_test_split(X, y_fake_score, test_size=0.25, random_state=42)

clf_model = RandomForestClassifier(random_state=42, n_estimators=100)
clf_model.fit(X_train, y_train_fake)

y_pred_fake = clf_model.predict(X_test)
print(classification_report(y_test_fake, y_pred_fake))
print(f"Точность классификации (Is_Fake): {accuracy_score(y_test_fake, y_pred_fake):.2f}")

reg_model = RandomForestRegressor(random_state=42, n_estimators=100)
reg_model.fit(X_train, y_train_score)

y_pred_score = reg_model.predict(X_test)

clf_model_path = os.path.join(model_dir, 'clf_model.pkl')
reg_model_path = os.path.join(model_dir, 'reg_model.pkl')
vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')

with open(clf_model_path, "wb") as model_file:
    pickle.dump(clf_model, model_file)

with open(reg_model_path, "wb") as model_file:
    pickle.dump(reg_model, model_file)

with open(vectorizer_path, "wb") as vec_file:
    pickle.dump(vectorizer, vec_file)

print(f"Классификационная модель сохранена в {clf_model_path}.")
print(f"Регрессионная модель сохранена в {reg_model_path}.")
print(f"Векторизатор сохранен в {vectorizer_path}.")
