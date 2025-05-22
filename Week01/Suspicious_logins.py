import sys
import re
from collections import defaultdict
from tabulate import tabulate
# Global variable to hold the log lines
log_lines = []

# Load the log file
def load_file(evidence_file_path):
    global log_lines
    try:
        with open(evidence_file_path, 'r') as file:
            log_lines = file.readlines()
    except FileNotFoundError:
        print(f"[ERROR] File not found: {evidence_file_path}")
        sys.exit(1)

# Search for failed SSH logins
def search_pattern():
    failed_attempts = []

    pattern = re.compile(
        r'^(?P<timestamp>\w{3}\s+\d{1,2}\s[\d:]+)\s.*sshd\[\d+\]:\sFailed password for (invalid user )?(?P<user>\w+) from (?P<ip>\d{1,3}(?:\.\d{1,3}){3})'
    )

    for line in log_lines:
        match = pattern.search(line)
        if match:
            failed_attempts.append({
                'timestamp': match.group("timestamp"),
                'username': match.group("user"),
                'ip': match.group("ip")
            })

    return failed_attempts

# Display results


def print_results():
    failed_logins = search_pattern()
    attempts_by_ip = defaultdict(int)

    detailed_table = []
    for attempt in failed_logins:
        detailed_table.append([
            attempt['timestamp'],
            attempt['ip'],
            attempt['username']
        ])
        attempts_by_ip[attempt['ip']] += 1

    # Print detailed failed attempts
    print("\n=== Failed SSH Login Attempts ===\n")
    print(tabulate(detailed_table, headers=["Timestamp", "IP Address", "Username"], tablefmt="grid"))

    # Summary by IP
    summary_table = [[ip, count] for ip, count in attempts_by_ip.items()]
    print("\n=== Summary: Total Failed Attempts by IP ===\n")
    print(tabulate(summary_table, headers=["IP Address", "Failed Attempts"], tablefmt="grid"))

# Main 
def main():
    if len(sys.argv) < 2:
        print("Usage: python Suspicious_logins.py <path to file>")
        sys.exit(1)

    evidence_file_path = sys.argv[1]
    load_file(evidence_file_path)
    print_results()

if __name__ == "__main__":
    main()
