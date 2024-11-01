#!/usr/bin/env python3

import argparse
import sys
import json
import os

def parse_orthogroups(orthogroups_file):
    orthogroups = {}
    with open(orthogroups_file, 'r') as f:
        for line in f:
            parts = line.strip().split(': ')
            if len(parts) == 2:
                ortho_number = parts[0]
                seq_names = parts[1].split()
                orthogroups[ortho_number] = seq_names
    return orthogroups

def load_nucleotide_sequences(nucleotide_json_files):
    nucleotide_dict = {}
    for json_file in nucleotide_json_files:
        with open(json_file, 'r') as f:
            nucleotide_dict.update(json.load(f))
    return nucleotide_dict

def main():
    parser = argparse.ArgumentParser(description='Generate multifasta files from orthogroups and parsed GenBank data.')
    parser.add_argument('--orthogroups', required=True, help='Path to the pared orthogroups file')
    parser.add_argument('--nucleotide_json', required=True, nargs='+', help='JSON file containing nucleotide sequences')
    
    args = parser.parse_args()

    # Parse orthogroups file
    orthogroups = parse_orthogroups(args.orthogroups)

    # Load nucleotide sequences
    nucleotide_dict = load_nucleotide_sequences(args.nucleotide_json)

    # Generate multifasta files
    for ortho_number, seq_names in orthogroups.items():
        output_file = f"{ortho_number}.fasta"
        with open(output_file, 'w') as f:
            for sequence in seq_names:
                # Try both with and without ">" prefix
                sequence_key = f">{sequence}"
                if sequence_key in nucleotide_dict:
                    f.write(f">{sequence}\n")
                    f.write(f"{nucleotide_dict[sequence_key]}\n")
                else:
                    print(f"Warning: Sequence {sequence} not found in nucleotide data", file=sys.stderr)

        print(f"Generated multifasta file: {output_file}")
        print(f"Number of sequences: {len(seq_names)}")

if __name__ == "__main__":
    main()