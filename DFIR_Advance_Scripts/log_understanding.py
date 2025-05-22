import os
import sys
import gzip
import csv
import re
import textwrap
from tabulate import tabulate

log_lines = []

def load_file(evidence_file_path):
    global log_lines
    _, ext = os.path.splitext(evidence_file_path)

    try:
        if ext == '.gz':
            with gzip.open(evidence_file_path, 'rt', encoding='utf-8') as file:
                log_lines = file.readlines()
        elif ext in ['.txt', '.log', '.csv']:
            with open(evidence_file_path, 'r', encoding='utf-8') as file:
                if ext == '.csv':
                    reader = csv.reader(file)
                    log_lines = [' '.join(row) for row in reader]
                else:
                    log_lines = file.readlines()
        else:
            print(f"[ERROR] Unsupported file type: {ext}")
            print("Supported file types: .txt, .log, .csv, .gz")
            sys.exit(1)

    except FileNotFoundError:
        print(f"[ERROR] File not found: {evidence_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load file: {str(e)}")
        sys.exit(1)

def detect_log_format(log_sample):
    if all(',' in line and re.search(r'\[\d{2}/[A-Za-z]+/\d{4}', line) for line in log_sample):
        return 'Custom Access Log'
    elif all('"' in line and 'HTTP/' in line for line in log_sample):
        return 'Apache Access Log'
    elif all(',' in line for line in log_sample):
        return 'CSV Structured'
    elif all('=' in line for line in log_sample):
        return 'Key=Value Log'
    else:
        return 'Unknown'

def parse_custom_access_log(line):
    pattern = re.compile(
        r'(?P<source_file>.+?):(?P<byte_offset>\d+):(?P<client_ip>[\d.]+), (?P<proxy_ip>[\d.]+) - - '
        r'\[(?P<timestamp>.*?)\] "(?P<method>GET|POST|PUT|DELETE|HEAD|OPTIONS) (?P<url>.*?) (?P<protocol>HTTP/[\d.]+)" '
        r'(?P<status>\d{3}) (?P<response_size>\d+|-) "(?P<referer>.*?)" "(?P<user_agent>.*?)" (?P<custom_code>\d+)'
    )
    match = pattern.match(line.strip())
    if match:
        return match.groupdict()
    return None

def wrap_text(text, width=60):
    if not text or text == '-':
        return text
    return textwrap.fill(str(text), width=width)

def infer_fields_from_unknown(lines, delimiter=None):
    structured_entries = []
    delimiter = delimiter or detect_delimiter(lines)
    
    for line in lines:
        parts = line.strip().split(delimiter)
        if len(parts) < 2:
            continue
        entry = {}
        for i, val in enumerate(parts):
            entry[f"field_{i+1}"] = wrap_text(val.strip())
        structured_entries.append(entry)
    
    return structured_entries

def detect_delimiter(lines):
    sample = lines[0]
    for delim in ['|', ',', ';', '\t']:
        if delim in sample:
            return delim
    return None  # Default to whitespace if nothing else

def extract_fields(log_format):
    structured_entries = []

    if log_format == 'Custom Access Log':
        for line in log_lines:
            entry = parse_custom_access_log(line)
            if entry:
                for field in ['source_file', 'url', 'referer', 'user_agent']:
                    entry[field] = wrap_text(entry[field])
                structured_entries.append(entry)

    elif log_format == 'Unknown':
        structured_entries = infer_fields_from_unknown(log_lines[:100])  # Sample 100 lines

    return structured_entries

def main():
    if len(sys.argv) < 2:
        print("Usage: python log_understanding.py <logfile>")
        sys.exit(1)

    file_path = sys.argv[1]
    load_file(file_path)

    sample = log_lines[:10]
    log_format = detect_log_format(sample)
    print(f"[INFO] Detected log format: {log_format}")

    results = extract_fields(log_format)
    print(f"[INFO] Extracted {len(results)} structured entries.")

    if results:
        keys = results[0].keys()
        print(tabulate([r.values() for r in results[:10]], headers=keys, tablefmt="fancy_grid", showindex=True))
    else:
        print("[INFO] No structured entries to display.")

if __name__ == "__main__":
    main()
