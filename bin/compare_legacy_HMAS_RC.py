#!/usr/bin/env python3
import argparse
import sys
import os

def reverse_complement(seq):
    """Return the RC of a DNA sequence"""
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A',
                 'R': 'Y', 'Y': 'R', 'K': 'M', 'M': 'K',
                 'B': 'V', 'V': 'B', 'D': 'H', 'H': 'D',
                 'N': 'N'}
    return ''.join(complement.get(base.upper(), base) for base in reversed(seq))

def check_primer_match(ref_pair, search_pair):
    """
    Check if primer pairs match in any orientation including reverse complements
    """
    ref_fwd1, ref_fwd2 = ref_pair
    ref_rev1, ref_rev2 = reverse_complement(ref_fwd1), reverse_complement(ref_fwd2)
    search_fwd1, search_fwd2 = search_pair
    
    # Check original orientation
    if (ref_fwd1 == search_fwd1 and ref_fwd2 == search_fwd2):
        return True
    # Check reverse complements
    if (ref_rev1 == search_fwd1 and ref_rev2 == search_fwd2):
        return True
    # Check mixed orientations
    if (ref_fwd1 == search_fwd1 and ref_rev2 == search_fwd2):
        return True
    if (ref_rev1 == search_fwd1 and ref_fwd2 == search_fwd2):
        return True
    
    return False

def extract_and_search_primers(reference_file, search_file, matches_file, unmatched_ref_file, unmatched_search_file):
    # Ensure output directories exist
    for file_path in [matches_file, unmatched_ref_file, unmatched_search_file]:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Store primer pairs and their full lines from reference file
    primer_pairs = {}
    
    # Read reference file
    with open(reference_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            cols = line.strip().split('\t')
            if len(cols) >= 3:
                primer_pairs[(cols[1], cols[2])] = (line_num, line.strip())
    
    # Track matches and store search file lines
    matched_pairs = set()
    matched_lines = []
    unmatched_search_lines = []
    
    # Search through search file
    with open(search_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            cols = line.strip().split('\t')
            if len(cols) >= 3:
                current_pair = (cols[1], cols[2])
                found_match = False
                
                # Check against all reference pairs
                for ref_pair in primer_pairs:
                    if check_primer_match(ref_pair, current_pair):
                        matched_pairs.add(ref_pair)
                        matched_lines.append((line_num, line.strip(), primer_pairs[ref_pair][0]))
                        found_match = True
                        break
                
                if not found_match:
                    unmatched_search_lines.append((line_num, line.strip()))
    
    # Find unmatched reference primers
    unmatched_ref_primers = {pair: info for pair, info in primer_pairs.items()
                            if pair not in matched_pairs}
    
    # Write matches to file
    with open(matches_file, 'w') as out:
        out.write(f"Found {len(primer_pairs)} primer pairs in reference file\n")
        out.write(f"Found {len(matched_lines)} matches:\n\n")
        for search_line_num, search_line, ref_line_num in matched_lines:
            out.write(f"Search Line {search_line_num} matches Reference Line {ref_line_num}: {search_line}\n")
    
    # Write unmatched reference primers to file
    with open(unmatched_ref_file, 'w') as out:
        out.write(f"Found {len(unmatched_ref_primers)} unmatched reference primers:\n\n")
        for line_num, line in unmatched_ref_primers.values():
            out.write(f"Line {line_num}: {line}\n")
    
    # Write unmatched search lines to file
    with open(unmatched_search_file, 'w') as out:
        out.write(f"Found {len(unmatched_search_lines)} unmatched search lines:\n\n")
        for line_num, line in unmatched_search_lines:
            out.write(f"Line {line_num}: {line}\n")
    
    return 0

def main():
    parser = argparse.ArgumentParser(description='Search for primer pairs in files and output matches and unmatched entries.')
    parser.add_argument('--reference', required=True, help='File containing reference primers')
    parser.add_argument('--search', required=True, help='File to search in')
    parser.add_argument('--matches', required=True, help='Output file for matches')
    parser.add_argument('--unmatched-ref', required=True, help='Output file for unmatched reference primers')
    parser.add_argument('--unmatched-search', required=True, help='Output file for unmatched search lines')
    args = parser.parse_args()
    
    try:
        sys.exit(extract_and_search_primers(
            args.reference,
            args.search,
            args.matches,
            args.unmatched_ref,
            args.unmatched_search
        ))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()