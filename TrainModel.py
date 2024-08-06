import pandas as pd
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score, classification_report, confusion_matrix

# Load the datasets
X_train = pd.read_csv('/data/users/fengwwta/SeniorProject/Training_Set.csv')
y_train = pd.read_csv('/data/users/fengwwta/SeniorProject/Training_Labels.csv')
X_test = pd.read_csv('/data/users/fengwwta/SeniorProject/Test_Set.csv')
y_test = pd.read_csv('/data/users/fengwwta/SeniorProject/Test_Labels.csv')

# Fill NaN values with empty string in 'subject' and 'body' columns
X_train['subject'] = X_train['subject'].fillna('')
X_train['body'] = X_train['body'].fillna('')
X_test['subject'] = X_test['subject'].fillna('')
X_test['body'] = X_test['body'].fillna('')

# Combine text fields into a single field for vectorization
X_train['text'] = X_train['subject'] + ' ' + X_train['body']
X_test['text'] = X_test['subject'] + ' ' + X_test['body']

# Vectorize the text data using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train['text'])
X_test_tfidf = vectorizer.transform(X_test['text'])

# Dictionary to store results
results = {}

# Function to evaluate model
def evaluate_model(model, X_train, y_train, X_test, y_test):
    start_time = time.time()
    model.fit(X_train, y_train.values.ravel())
    end_time = time.time()
    training_time = end_time - start_time
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    
    return training_time, accuracy, recall, precision, y_pred

# Naive Bayes
nb_model = MultinomialNB()
nb_results = evaluate_model(nb_model, X_train_tfidf, y_train, X_test_tfidf, y_test)
results['Naive Bayes'] = nb_results

# Decision Tree
dt_model = DecisionTreeClassifier()
dt_results = evaluate_model(dt_model, X_train_tfidf, y_train, X_test_tfidf, y_test)
results['Decision Tree'] = dt_results

# Random Forest
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_results = evaluate_model(rf_model, X_train_tfidf, y_train, X_test_tfidf, y_test)
results['Random Forest'] = rf_results

# Print results
for model_name, result in results.items():
    print(f"Model: {model_name}")
    print(f"Training Time: {result[0]:.4f} seconds")
    print(f"Accuracy: {result[1]:.4f}")
    print(f"Recall: {result[2]:.4f}")
    print(f"Precision: {result[3]:.4f}")
    print(f"Classification Report:\n{classification_report(y_test, result[4])}")
    print(f"Confusion Matrix:\n{confusion_matrix(y_test, result[4])}\n")
