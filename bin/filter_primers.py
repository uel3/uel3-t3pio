#!/usr/bin/env python

import argparse
from pathlib import Path

def filter_good_primers(parsed_primersearch_bad_primers, all_primers_path, output_path, bad_primers_output_path):
    bad_primers = set()

    # Read all bad primers, skipping empty files and removing duplicates
    for bad_file in parsed_primersearch_bad_primers:
        if Path(bad_file).is_file():
            with open(bad_file, 'r') as f:
                for line in f:
                    primer = line.strip()
                    if primer:
                        bad_primers.add(primer)

    # Save bad primers to a file
    with open(bad_primers_output_path, 'w') as f:
        for primer in bad_primers:
            f.write(f"{primer}\n")

    # Filter all_primers based on bad_primers
    with open(all_primers_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            first_col = line.split('\t')[0]
            if first_col not in bad_primers:
                outfile.write(line)

def main():
    # Initialize argparse
    parser = argparse.ArgumentParser(description="Filter good primers from a list based on bad primers.")
    
    # Define arguments
    parser.add_argument('--bad_primers', nargs='+', required=True, help="Space-separated list of paths to bad primer files.")
    parser.add_argument('--all_primers', required=True, help="Path to the all primers file (tab-delimited, at least 3 columns).")
    parser.add_argument('--output', required=True, help="Output file for good primers after filtering.")
    parser.add_argument('--bad_primers_output', required=True, help="Output file for saving bad primers.")
    
    # Parse arguments
    args = parser.parse_args()

    # Call the filter function with parsed arguments
    filter_good_primers(args.bad_primers, args.all_primers, args.output, args.bad_primers_output)

if __name__ == "__main__":
    main()
