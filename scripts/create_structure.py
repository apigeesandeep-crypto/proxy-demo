#!/usr/bin/env python3
"""
create_structure.py
Creates the Apigee proxy folder scaffolding for proxy-demo-1.
"""

import os
import sys

PROXY_NAME = "proxy-demo-1"

# Directory structure for an Apigee API proxy bundle
DIRECTORIES = [
    f"apiproxy",
    f"apiproxy/proxies",
    f"apiproxy/targets",
    f"apiproxy/policies",
    f"apiproxy/resources",
    f"apiproxy/resources/jsc",
    f"apiproxy/resources/xsl",
]


def create_directories(base_path: str = ".") -> None:
    for directory in DIRECTORIES:
        full_path = os.path.join(base_path, directory)
        os.makedirs(full_path, exist_ok=True)
        print(f"[OK] Created directory: {full_path}")


def main():
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"==> Scaffolding proxy bundle under: {os.path.abspath(base_path)}")
    create_directories(base_path)
    print("==> Directory scaffolding complete.")


if __name__ == "__main__":
    main()

