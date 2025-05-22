import re
import sys
from collections import defaultdict
from tabulate import tabulate
from typing import List, Dict, Tuple
import textwrap

def read_file(file_path: str) -> List[str]:
    """Reads a text file and returns the lines."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()


def extract_select_queries(lines: List[str]) -> List[str]:
    """Extracts SELECT queries using a regex pattern."""
    pattern = re.compile(
        r"SELECT\s+.+?FROM\s+.+?(?=(?:\sORDER|\sGROUP|\sLIMIT|;|$))",
        re.IGNORECASE | re.DOTALL
    )
    queries = []
    for line in lines:
        queries.extend(pattern.findall(line))
    return queries


def generalize_query(query: str) -> str:
    """Generalizes specific values in a SELECT query."""
    generalize_patterns = [
        (re.compile(r"\b(mailbox_id|parent_id|folder_id|index_id|imap_id|size|mod_metadata|change_date|mod_content|id)\s*=\s*\d+"), r"\1=?"),
        (re.compile(r"\b(uuid|name|subject|tag_names|blob_digest|locator|metadata)\s*=\s*'[^']*'"), r"\1='?'"),
    ]
    for pattern, replacement in generalize_patterns:
        query = pattern.sub(replacement, query)

    # Generalize IN clause
    in_clause_pattern = re.compile(r"\bparent_id\s+IN\s*\(([\d,\s]+)\)", re.IGNORECASE)
    query = in_clause_pattern.sub("parent_id IN (?)", query)

    return query.strip()


def group_queries(queries: List[str]) -> Dict[str, List[str]]:
    """Groups queries by their generalized form."""
    grouped = defaultdict(list)
    for query in queries:
        gen = generalize_query(query)
        grouped[gen].append(query.strip())
    return grouped

def wrap_query(query: str, width: int = 100) -> str:
    """Wraps a query string for better readability in tables."""
    return "\n".join(textwrap.wrap(query, width=width, break_long_words=False, replace_whitespace=False))

def wrap_query(query: str, width: int = 100) -> str:
    """Wraps a query string for better readability in tables."""
    return "\n".join(textwrap.wrap(query, width=width, break_long_words=False, replace_whitespace=False))

def generate_summary_tables(grouped: Dict[str, List[str]], wrap_width: int = 120) -> Tuple[str, str]:
    """Generates summary and detail tables, with query index in details instead of repeating the query."""
    summary_table = []
    details_table = []

    for i, (gen_query, instances) in enumerate(grouped.items(), 1):
        wrapped_gen_query = wrap_query(gen_query, wrap_width)
        wrapped_example_query = wrap_query(instances[0], wrap_width)

        summary_table.append([i, len(instances), wrapped_gen_query])
        details_table.append([i, len(instances), wrapped_example_query, i])  # Only show index for generalized query

    summary_output = tabulate(
        summary_table,
        headers=["#", "Occurrences", "Generalized Query"],
        tablefmt="grid",
        stralign="left"
    )

    details_output = tabulate(
        details_table,
        headers=["#", "Occurrences", "Example Query", "Generalized Query"],
        tablefmt="grid",
        stralign="left"
    )

    return summary_output, details_output

def write_output(file_path: str, summary: str, details: str) -> None:
    """Writes summary and details to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("=== Summary of Generalized SELECT Queries ===\n\n")
        f.write(summary + "\n\n")
        f.write("=== Details of Each Generalized Query ===\n\n")
        f.write(details)


def main():
    if len(sys.argv) != 3:
        print("Usage: python query_generalizer.py <input_file> <output_file>")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    lines = read_file(input_path)
    queries = extract_select_queries(lines)
    grouped = group_queries(queries)
    summary, details = generate_summary_tables(grouped)

    # Print to terminal
    print("\n=== Summary of Generalized SELECT Queries ===\n")
    print(summary)

    print("\n=== Details of Each Generalized Query ===\n")
    print(details)

    # Save to output file
    write_output(output_path, summary, details)
    print(f"\n[✓] Output saved to: {output_path}")


if __name__ == "__main__":
    main()
