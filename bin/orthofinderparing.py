#!/usr/bin/env python3

import argparse
import sys

class OrthofinderResults:
    def __init__(self, orthoNumber, seqNames):
        self.orthoNumber = orthoNumber
        self.seqNames = seqNames

def parse_orthofinder_output(file_path):
    orthofinderObjectList = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(': ')
            if len(parts) == 2:
                orthoNumber = parts[0]
                seqNames = parts[1].split()
                orthofinderObjectList.append(OrthofinderResults(orthoNumber, seqNames))
    return orthofinderObjectList

def OrthofinderParing(numberOfIsolates, percentInclusion, orthofinderObjectList):
    paredDownList = []
    numberNeeded = numberOfIsolates * percentInclusion
    
    for orthogroups in orthofinderObjectList:
        seqNameList = []
        for sequences in orthogroups.seqNames:
            seqNameList.append(sequences.split('.')[0])
        seqNameSet = set(seqNameList)
        if len(seqNameList) == len(seqNameSet):
            if len(orthogroups.seqNames) >= numberNeeded:
                paredDownList.append(orthogroups)
    return paredDownList

def nullable_int(val):
    if val.lower() == 'null':
        return None
    return int(val)

def main():
    parser = argparse.ArgumentParser(description='Pare down Orthofinder results based on isolate inclusion criteria.')
    parser.add_argument('--number_isolates', type=int, required=True, help='Number of isolates originally submitted')
    parser.add_argument('--percent_inclusion', type=float, required=True, help='Percent inclusion to be considered an orthogroup')
    parser.add_argument('--orthogroups', type=str, required=True, help='Path to the Orthofinder results file')
    parser.add_argument('--test_size', type=nullable_int, required=False, help='test data size for the orthogroup')
    
    args = parser.parse_args()

    # Parse the Orthofinder results file
    orthofinderObjectList = parse_orthofinder_output(args.orthogroups)

    # Run the OrthofinderParing function
    paredDownList = OrthofinderParing(args.number_isolates, args.percent_inclusion, orthofinderObjectList)
    if args.test_size:
        paredDownList = paredDownList[:args.test_size]

    # Write the results to a file in the same format as the input
    with open('pared_orthogroups.txt', 'w') as f:
        for og in paredDownList:
            f.write(f"{og.orthoNumber}: {' '.join(og.seqNames)}\n")

    print(f"Paring complete. Original orthogroups: {len(orthofinderObjectList)}, Pared orthogroups: {len(paredDownList)}")

if __name__ == "__main__":
    main()