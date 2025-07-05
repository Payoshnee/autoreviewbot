from flask import Flask, request
import subprocess
import json

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json

    # Only respond to pull_request events
    if "pull_request" not in payload:
        print("❌ Not a pull request event.")
        return "Ignored", 200

    pr_action = payload["action"]
    pr_number = payload["number"]
    pr_branch = payload["pull_request"]["head"]["ref"]
    repo_full_name = payload["repository"]["full_name"]

    print(f"\n📥 PR #{pr_number} triggered - Branch: {pr_branch} | Action: {pr_action}")

    # Trigger code analysis
    try:
        print("🚀 Starting code analysis via analyze.py...\n")
        subprocess.run(["python", "analyze.py"], check=True)
        print("✅ Analysis finished.")
    except subprocess.CalledProcessError as e:
        print("❌ Analysis failed:", e)

    return "Received", 200

if __name__ == "__main__":
    print("🚀 AutoReviewBot Webhook Listener Running on /webhook")
    app.run(port=5000)
