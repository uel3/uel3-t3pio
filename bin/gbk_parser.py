#!/usr/bin/env python3
import os
import json
import argparse
import glob
import sys
from Bio import SeqIO

def gbk_parser(gbk_file, out_faa, out_json):
    nucleotide_dictionary = {}
    
    sample_name = os.path.splitext(os.path.basename(gbk_file))[0]
    
    with open(gbk_file, 'r') as infile, open(out_faa, 'w') as faa_out:
        feature_count = 0
        for record in SeqIO.parse(infile, 'genbank'):
            for feature in record.features:
                if feature.type == 'CDS':
                    feature_count += 1
                    locus_tag = feature.qualifiers['locus_tag'][0]
                    translation = feature.qualifiers['translation'][0]
                    faa_out.write(f">{sample_name}.{record.name}.{locus_tag}\n{translation}\n")
                   
                    nucleotide_seq = feature.location.extract(record).seq
                    nucleotide_dictionary[f">{sample_name}.{record.name}.{locus_tag}"] = str(nucleotide_seq)
       
        if feature_count == 0:
            raise ValueError(f"No CDS features found in {gbk_file}")
   
    with open(out_json, 'w') as json_out:
        json.dump(nucleotide_dictionary, json_out)

    print(f"Successfully processed {gbk_file}")
    print(f"FAA output: {out_faa}")
    print(f"JSON output: {out_json}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse GenBank file and extract protein and nucleotide sequences.")
    parser.add_argument("--input", required=True, help="Input GenBank file")
    parser.add_argument("--output_faa", required=True, help="Output FAA file")
    parser.add_argument("--output_json", required=True, help="Output JSON file for nucleotide sequences")
    args = parser.parse_args()

    try:
        gbk_parser(args.input, args.output_faa, args.output_json)
        print("Processing complete.")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
