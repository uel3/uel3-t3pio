#!/usr/bin/env python3

import json
import sys

def combine_json_files(input_files, output_file):
    combined_dict = {}
    for file in input_files:
        with open(file, 'r') as f:
            data = json.load(f)
            combined_dict.update(data)

    with open(output_file, 'w') as f:
        json.dump(combined_dict, f, indent=2)

    print(f"Combined JSON file created successfully: {output_file}")
    print(f"Total entries in combined JSON: {len(combined_dict)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: combine_json.py output_file input_file1 input_file2 ...")
        sys.exit(1)

    output_file = sys.argv[1]
    input_files = sys.argv[2:]

    combine_json_files(input_files, output_file)