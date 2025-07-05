import pandas as pd
import lightgbm as lgb
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

# Load feedback CSV
df = pd.read_csv("Generated_Feedback_Log (1).csv")

# Drop rows with missing labels or messages
df = df.dropna(subset=["label", "message"])

# Encode text features
tfidf = TfidfVectorizer(max_features=100)
X_msg = tfidf.fit_transform(df["message"])

# Encode categorical
severity_enc = LabelEncoder()
X_sev = severity_enc.fit_transform(df["severity"])

tool_enc = LabelEncoder()
X_tool = tool_enc.fit_transform(df["tool"])

# Combine into full feature set
import scipy.sparse as sp
X = sp.hstack([X_msg, 
               sp.csr_matrix(X_sev).T, 
               sp.csr_matrix(X_tool).T])

y = df["label"]

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = lgb.LGBMClassifier()
model.fit(X_train, y_train)

# Evaluate (optional)
from sklearn.metrics import precision_score, recall_score
y_pred = model.predict(X_test)
print("📊 Precision:", precision_score(y_test, y_pred))
print("📊 Recall:", recall_score(y_test, y_pred))

# Save everything
joblib.dump((model, tfidf, severity_enc, tool_enc), "ranker_model.pkl")
print("✅ Model saved to ranker_model.pkl")
