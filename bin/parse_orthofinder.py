#!/usr/bin/env python3
import argparse
import sys

class OrthofinderResults:
    def __init__(self, orthoNumber, seqNames):
        self.orthoNumber = orthoNumber
        self.seqNames = seqNames

def orthoFinderParser(OrthofinderTxt):
    with open(OrthofinderTxt) as f:
        orthogroupInfo = f.readlines()
   
    orthogroupResultsList = []
    for line in orthogroupInfo:
        line = line.strip('\n').split(': ')
        if len(line) != 2:
            print(f"Warning: Unexpected line format: {line}", file=sys.stderr)
            continue
        orthoNumber = line[0]
        seqNames = line[1].split(' ')
        orthogroup = OrthofinderResults(orthoNumber, seqNames)
        orthogroupResultsList.append(orthogroup)
   
    print(f"Processed {len(orthogroupResultsList)} orthogroups", file=sys.stderr)
    return orthogroupResultsList

def main():
    parser = argparse.ArgumentParser(description='Parse OrthoFinder results')
    parser.add_argument('--input', required=True, help='Input OrthoFinder results file')
    parser.add_argument('--output', required=True, help='Output parsed results file')
    args = parser.parse_args()

    print(f"Processing input file: {args.input}", file=sys.stderr)
    results = orthoFinderParser(args.input)

    print(f"Writing results to: {args.output}", file=sys.stderr)
    with open(args.output, 'w') as out_file:
        for result in results:
            out_file.write(f"{result.orthoNumber}: {' '.join(result.seqNames)}\n")

    print("Parsing completed", file=sys.stderr)

if __name__ == "__main__":
    main()

