import subprocess
import yaml
import os
import json
import yaml

# === Configuration ===
REPO_DIR = "commons-lang"
CHECKSTYLE_JAR = "Downloads\\checkstyle-10.14.1-all.jar"
CHECKSTYLE_CONFIG = "google_checks.xml"
PMD_CMD = "Downloads\\pmd-bin-7.15.0\\bin\\pmd.bat"
SPOTBUGS_CMD = "Downloads\\spotbugs-4.8.3\\bin\\spotbugs.bat"
RULES_FILE = "rules.yaml"

# === Load Java Code Review Rules ===
try:
    with open(RULES_FILE, "r") as f:
        rules = yaml.safe_load(f)
except FileNotFoundError:
    print("❌ rules.yaml not found.")
    exit(1)

# === Compile Project ===
print("🔧 Compiling Java project with Maven...")
try:
    subprocess.run(
        ["C:\\apache-maven-3.9.9\\bin\\mvn.cmd", "clean", "compile"],
        cwd=os.path.join(os.getcwd(), REPO_DIR),
        check=True
    )
except FileNotFoundError:
    print("❌ Maven not found. Make sure mvn.cmd path is correct.")
    exit(1)
except subprocess.CalledProcessError:
    print("❌ Compilation failed. Fix Java errors before continuing.")
    exit(1)

# === Run Checkstyle ===
def run_checkstyle():
    print("\n🔍 Running Checkstyle...")
    target = os.path.join(REPO_DIR, "src", "main", "java")
    result = subprocess.run(
        ["java", "-jar", CHECKSTYLE_JAR, "-c", CHECKSTYLE_CONFIG, target],
        capture_output=True,
        text=True
    )
    return result.stdout

# === Run PMD ===
def run_pmd():
    print("\n🔍 Running PMD...")
    target = os.path.join(REPO_DIR, "src", "main", "java")
    result = subprocess.run(
        [PMD_CMD, "pmd", "-d", target, "-R", "rulesets/java/quickstart.xml", "-f", "text"],
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout

# === Run SpotBugs ===
def run_spotbugs():
    print("\n🔍 Running SpotBugs...")
    target = os.path.join(REPO_DIR, "target", "classes")
    result = subprocess.run(
        [SPOTBUGS_CMD, "-textui", "-effort:max", "-high", target],
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout

# === Match Violations to Rules ===
def match_violation(tool, text):
    for rule_id, info in rules.items():
        if info["linter"].lower() == tool.lower():
            if rule_id.lower().replace("_", "")[:6] in text.lower().replace(" ", ""):
                return rule_id, info
    return None, None

# === Print Formatted Output ===
def print_results(tool_name, output):
    print(f"\n----- {tool_name.upper()} VIOLATIONS -----")
    lines = output.splitlines()
    for line in lines:
        if not line.strip():
            continue
        print(f"{line}")
        rule_id, info = match_violation(tool_name, line)
        if rule_id:
            print(f"  👉 Rule {rule_id}: {info['message']} [Severity: {info['severity']}]\n")

# === Run Linters and Capture Output ===
checkstyle_out = run_checkstyle()
pmd_out = run_pmd()
spotbugs_out = run_spotbugs()

print_results("checkstyle", checkstyle_out)
print_results("pmd", pmd_out)
print_results("spotbugs", spotbugs_out)

# === Utility to Convert Output into JSON ===
def extract_violations(raw_output, tool_name):
    results = []
    lines = raw_output.split("\n")
    for line in lines:
        if line.strip() == "":
            continue
        if ".java" in line:
            parts = line.split(":")
            if len(parts) >= 3:
                file_path = parts[0].strip()
                line_number = int(parts[1].strip())
                message = ":".join(parts[2:]).strip()
                rule_id, data = match_violation(tool_name, message)
                results.append({
                    "file": file_path.replace("\\", "/"),
                    "line": line_number,
                    "message": message,
                    "rule_id": rule_id or "unknown_rule",
                    "severity": data["severity"] if data else "low",
                    "tool": tool_name
                })
    return results

# === Save Structured Violations to JSON ===
violations = (
    extract_violations(checkstyle_out, "checkstyle") +
    extract_violations(pmd_out, "pmd") +
    extract_violations(spotbugs_out, "spotbugs")
)

with open("violations.json", "w") as f:
    json.dump(violations, f, indent=2)

print("✅ Violations saved to violations.json")


def llm_summarize(violations):
    summary = "🔍 Similar issues grouped:\n"
    for sev in ["high", "medium", "low"]:
        msgs = [v["message"] for v in violations if v["severity"] == sev]
        if msgs:
            summary += f"\n**{sev.upper()}**:\n- " + "\n- ".join(msgs[:3])
    return summary

# Use instead of post_summary
summary_body = llm_summarize(violations)
post_summary(len(violations), critical_count)
print(summary_body)

weights = yaml.safe_load(open("weights.yaml"))
for v in violations:
    rule = v.get("rule_id")
    v["weight"] = weights.get(rule, 1.0)
