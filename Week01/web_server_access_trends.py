"""
Parse access logs to:
 Count total requests per IP
 Printed using ChatGPT to PDF, powered by PDFCrowd HTML to PDF API. 6/22
Identify top 5 IPs
 Show most requested URLs
 Filter only status code `500` or `404'

"""
import re
import sys
from collections import defaultdict, Counter
from tabulate import tabulate
import io

ip_counter = Counter()
url_counter = Counter()
error_entries = []

def load_txt(evidence_file):
    """Loads the log file and returns its lines."""
    with open(evidence_file, 'r') as f:
        return f.readlines()

def search_trends(log_lines):
    """
    Parses access logs:
    - Counts total requests per IP
    - Tracks most requested URLs
    - Filters status 500 and 404
    """
    pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s-\s-\s\[(?P<timestamp>[^\]]+)\]\s"(?P<method>\w+)\s(?P<url>\S+)\sHTTP/[\d.]+"\s(?P<status>\d+)\s(?P<size>\d+)'
    )

    for line in log_lines:
        match = pattern.search(line)
        if match:
            ip = match.group("ip")
            url = match.group("url")
            status = int(match.group("status"))

            ip_counter[ip] += 1
            url_counter[url] += 1

            if status in (404, 500):
                error_entries.append({
                    "IP": ip,
                    "URL": url,
                    "Status": status,
                    "Timestamp": match.group("timestamp")
                })

def print_results():
    output = io.StringIO()

    def print_section(title, data, headers):
        output.write(f"\n[{title}]\n")
        output.write(tabulate(data, headers=headers, tablefmt="grid") + "\n")

    # Prepare tables
    ip_table = [{"IP": ip, "Requests": count} for ip, count in ip_counter.items()]
    top_ips = ip_counter.most_common(5)
    top_urls = url_counter.most_common(10)

    print_section("Total Requests Per IP", ip_table, "keys")
    print_section("Top 5 IPs by Requests", top_ips, ["IP", "Requests"])
    print_section("Top Requested URLs", top_urls, ["URL", "Hits"])
    print_section("Entries with Status Code 500 or 404", error_entries, "keys")

    # Output to console
    print(output.getvalue())

    # Save to file
    with open("log_report.txt", "w") as f:
        f.write(output.getvalue())

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file_path>")
        sys.exit(1)

    filepath = sys.argv[1]
    log_lines = load_txt(filepath)
    search_trends(log_lines)
    print_results()

if __name__ == "__main__":
    main()
