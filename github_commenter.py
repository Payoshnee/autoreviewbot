import requests
import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# === Load environment variables or config ===
GITHUB_TOKEN = "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"
REPO = "Payoshnee/commons-lang"
PR_NUMBER = 1

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# === Load violations ===
with open("violations.json", "r") as f:
    violations = json.load(f)

# === Load ML ranker model ===
try:
    model, tfidf, severity_enc, tool_enc = joblib.load("ranker_model.pkl")
    print("✅ Loaded trained ranker model")
except:
    model = None
    print("⚠️ Ranker model not found. Proceeding without ML ranking.")

# === Score and sort violations using ML model ===
def score_violations(violations):
    if not model:
        return violations

    df = pd.DataFrame(violations)

    X_text = tfidf.transform(df["message"])
    X_sev = severity_enc.transform(df["severity"])
    X_tool = tool_enc.transform(df["tool"])
    X_all = np.hstack([X_text.toarray(), X_sev.reshape(-1, 1), X_tool.reshape(-1, 1)])

    scores = model.predict_proba(X_all)[:, 1]
    df["score"] = scores

    ranked = df.sort_values("score", ascending=False).to_dict(orient="records")
    return ranked

ranked_violations = score_violations(violations)

# === Post inline comments ===
def post_comment(file_path, line, body):
    url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/comments"
    payload = {
        "path": file_path,
        "line": line,
        "side": "RIGHT",
        "body": body
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        print(f"✅ Comment posted: {file_path}:{line}")
    else:
        print(f"❌ Failed to post comment: {response.status_code} - {response.text}")

# === Post summary ===
def post_summary(total, critical):
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    body = f"""🔍 AutoReviewBot completed analysis.

- Total violations: **{total}**
- Critical: **{critical}**

_This PR is under review. Please fix the issues._"""
    response = requests.post(url, headers=headers, json={"body": body})
    print("📝 Summary comment posted:", response.status_code)

# === Post comments (top N only for now) ===
critical_count = 0
for v in ranked_violations[:10]:  # top 10 only
    severity = v.get("severity", "unknown")
    tool = v.get("tool", "unknown").capitalize()
    message = v.get("message", "No message provided.")
    file_path = v.get("file", "unknown")
    line_number = v.get("line", 1)

    body = f"**{tool}**: {message}\n\n> Severity: **{severity}**"
    post_comment(file_path, line_number, body)

    if severity.lower() == "critical":
        critical_count += 1

post_summary(len(ranked_violations), critical_count)
