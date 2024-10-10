#!/usr/bin/env python3

import sys

class OrthofinderResults:
    def __init__(self, orthoNumber, seqNames):
        self.orthoNumber = orthoNumber
        self.seqNames = seqNames

def orthoFinderParser(OrthofinderTxt):
    with open(OrthofinderTxt) as f:
        orthogroupInfo = f.readlines()
    
    orthogroupResultsList = []
    for i, line in enumerate(orthogroupInfo, 1):
        try:
            line = line.strip('\n').split(' ')
            orthoNumber = line[0].strip(':')
            seqNames = line[1:]
            orthogroup = OrthofinderResults(orthoNumber, seqNames)
            orthogroupResultsList.append(orthogroup)
        except Exception as e:
            print(f"Error parsing line {i}: {e}", file=sys.stderr)
            print(f"Line content: {line}", file=sys.stderr)
    
    return orthogroupResultsList

def OrthofinderClassCheck(orthogroupResultsList):
    for i, orthogroupObject in enumerate(orthogroupResultsList, 1):
        if not isinstance(orthogroupObject.orthoNumber, str):
            print(f"FAIL: Orthogroup {i} has non-string orthoNumber: {type(orthogroupObject.orthoNumber)}", file=sys.stderr)
            return False
        if not isinstance(orthogroupObject.seqNames, list):
            print(f"FAIL: Orthogroup {i} has non-list seqNames: {type(orthogroupObject.seqNames)}", file=sys.stderr)
            return False
        if not orthogroupObject.seqNames:
            print(f"FAIL: Orthogroup {i} has empty seqNames", file=sys.stderr)
            return False
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 class_check_orthofinder.py <orthofinder_results_file>")
        sys.exit(1)

    try:
        orthogroupResultsList = orthoFinderParser(sys.argv[1])
        print(f"Parsed {len(orthogroupResultsList)} orthogroups", file=sys.stderr)
        
        if OrthofinderClassCheck(orthogroupResultsList):
            print("PASS")
        else:
            print("FAIL")
    except Exception as e:
        print(f"FAIL: An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)