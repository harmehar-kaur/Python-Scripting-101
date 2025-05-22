import re
import os
import sys
from datetime import datetime
from typing import Optional, List, Tuple


TIMESTAMP_REGEX = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S,%f"


def extract_timestamp(line: str) -> Optional[datetime]:
    match = re.search(TIMESTAMP_REGEX, line)
    if match:
        try:
            return datetime.strptime(match.group(), TIMESTAMP_FORMAT)
        except ValueError:
            return None
    return None


def read_log_lines(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def sort_log_lines(lines: List[str]) -> List[str]:
    lines_with_timestamps: List[Tuple[datetime, str]] = []

    for line in lines:
        timestamp = extract_timestamp(line)
        if timestamp:
            lines_with_timestamps.append((timestamp, line))

    lines_with_timestamps.sort(key=lambda x: x[0])
    return [line for _, line in lines_with_timestamps]


def write_sorted_logs(sorted_lines: List[str], output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(sorted_lines)


def main(input_path: str, output_path: Optional[str] = None):
    if not os.path.isfile(input_path):
        print(f"[ERROR] File not found: {input_path}")
        sys.exit(1)

    if not output_path:
        output_path = os.path.join(
            os.path.dirname(input_path),
            f"sorted_{os.path.basename(input_path)}"
        )

    print(f"[INFO] Reading log file: {input_path}")
    log_lines = read_log_lines(input_path)

    print(f"[INFO] Sorting {len(log_lines)} lines by timestamp...")
    sorted_lines = sort_log_lines(log_lines)

    print(f"[INFO] Writing sorted logs to: {output_path}")
    write_sorted_logs(sorted_lines, output_path)

    print(f"[✓] Done. Sorted log saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sort_logs.py <input_file_path> [output_file_path]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    main(input_file, output_file)
