import pandas as pd
from sklearn.metrics import precision_score, recall_score

df = pd.read_csv("predictions.csv")  # contains true_label, predicted_label
p = precision_score(df["true_label"], df["predicted_label"])
r = recall_score(df["true_label"], df["predicted_label"])
print("📊 Precision:", p, "| Recall:", r)