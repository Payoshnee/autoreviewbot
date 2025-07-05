from flask import Flask, request, jsonify
from github import Github
import os
import subprocess

app = Flask(__name__)

# Set your GitHub token here or use environment variable
GITHUB_TOKEN = os.getenv("GH_TOKEN")

@app.route("/", methods=["GET"])
def index():
    return "AutoReviewBot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    event = request.headers.get("X-GitHub-Event", "ping")
    payload = request.json

    if event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            repo_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]

            print(f"🔔 PR #{pr_number} triggered in {repo_name}")

            # Run the analysis
            subprocess.run(["python", "analyze.py"])

            # Connect to GitHub and post a comment
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            pr.create_issue_comment(" AutoReviewBot: Code analyzed. See inline comments and violations logged below.")

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
