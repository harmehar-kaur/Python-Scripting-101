import re
import sys
import os
from datetime import datetime
from collections import defaultdict
from tabulate import tabulate
from typing import Optional


# Regex to extract timestamp and SOAP request type
LOG_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*soap - (\w+Request)")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S,%f"


def extract_requests(file_path: str) -> dict:
    request_times = defaultdict(list)

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = LOG_PATTERN.search(line)
            if match:
                timestamp_str, request_type = match.groups()
                try:
                    timestamp = datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)
                    request_times[request_type].append(timestamp)
                except ValueError:
                    continue  # Skip lines with bad timestamp format

    return request_times


def summarize_requests(request_times: dict) -> str:
    table_data = []

    for request_type, times in request_times.items():
        times.sort()
        intervals = [
            (t2 - t1).total_seconds()
            for t1, t2 in zip(times[:-1], times[1:])
        ]
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        first_request = times[0].strftime("%Y-%m-%d %H:%M:%S")
        last_request = times[-1].strftime("%Y-%m-%d %H:%M:%S")

        table_data.append([
            request_type,
            len(times),
            f"{avg_interval:.2f} s",
            first_request,
            last_request
        ])

    return tabulate(
        table_data,
        headers=["Request Type", "Count", "Avg Interval", "First Seen", "Last Seen"],
        tablefmt="grid"
    )


def main(input_path: str, output_path: Optional[str] = None):
    if not os.path.isfile(input_path):
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    print(f"[INFO] Processing file: {input_path}")
    request_data = extract_requests(input_path)
    summary_table = summarize_requests(request_data)

    print("\n=== SOAP Request Type Summary ===\n")
    print(summary_table)

    if not output_path:
        output_path = os.path.join(
            os.path.dirname(input_path),
            "soap_request_summary.txt"
        )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=== SOAP Request Type Summary ===\n\n")
        f.write(summary_table)

    print(f"\n[✓] Summary saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python soap_summary.py <input_log_file> [output_summary_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    main(input_file, output_file)
