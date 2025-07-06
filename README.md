AutoReviewBot: AI-Powered Pull Request Reviewer

AutoReviewBot is an automated GitHub bot that reviews Pull Requests (PRs) using static code analyzers and Machine Learning (ML). It posts GitHub comments highlighting potential code issues, prioritizes them using AI.

---

## Key Features

- Runs static code analyzers: Checkstyle, PMD, SpotBugs
- Uses ML to prioritize violations based on developer feedback
- Posts inline comments on GitHub PRs using GitHub API
- Optional LLM summarization for grouped feedback
- Tracks metrics (Precision, Recall) and logs feedback
- Supports adaptive rule weights with `weights.yaml`

---

## 📦 Tech Stack

| Component            | Tool/Library         |
|----------------------|----------------------|
| Language             | Python 3             |
| Static Analysis      | Checkstyle, PMD, SpotBugs |
| ML Ranking           | LightGBM + TF-IDF + Scikit-learn |
| LLM Summarization    | OpenAI GPT (optional) |
| GitHub Integration   | REST API + Webhooks  |
| Hosting              | Ngrok                |
| CI/CD Support        | GitHub Actions       |

---

## ⚙️ Architecture
![Untitled diagram _ Mermaid Chart-2025-07-06-033047](https://github.com/user-attachments/assets/5efd3631-88b4-49f9-92ae-ab01febb965d)

---
