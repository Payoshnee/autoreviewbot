import csv
import json
import os

# Load violations
with open("violations.json", "r") as f:
    violations = json.load(f)

# Create CSV log
with open("feedback_log.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        "file", "line", "tool", "rule_id", "severity", "message", "developer_action"
    ])
    writer.writeheader()

    for v in violations:
        writer.writerow({
            "file": v["file"],
            "line": v["line"],
            "tool": v["tool"],
            "rule_id": v["rule_id"],
            "severity": v["severity"],
            "message": v["message"],
            "developer_action": ""  # To be filled manually or later by script
        })

print("✅ feedback_log.csv created — ready for tracking developer responses.")
