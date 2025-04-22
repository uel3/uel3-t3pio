#!/usr/bin/env python

import argparse
from functools import partial

class OutputRecord:
    def __init__(self):
        self.amplifiers = {}

class Amplifier:
    def __init__(self):
        self.hit_info = ''
        self.length = 0

def readPrimersearch(handle):
    record = OutputRecord()
    current_name = None
    
    for line in handle:
        line = line.strip()
        if not line:
            continue
        if line.startswith('Primer name'):
            current_name = line.split()[-1]
            record.amplifiers[current_name] = []
        elif line.startswith('Amplimer') and 'length' not in line:
            record.amplifiers[current_name].append(Amplifier())
        elif line.startswith('Sequence:'):
            record.amplifiers[current_name][-1].hit_info = line.replace('Sequence: ', '').strip()
        elif line.startswith('Amplimer length:'):
            length = line.split()[-2]
            record.amplifiers[current_name][-1].length = int(length)
    
    return record

def multiHitPrimers(contigs, psObj):
    quality = True
    for obj in psObj:
        # Extract contig name from first word of hit_info
        hit_contig = obj.hit_info.split()[0] if obj.hit_info else ''
        if hit_contig not in contigs and obj.length < 1000:
            quality = False
    return quality

def contigCompare(contigs, psInfo):
    bad_primers = []
    off_target_large = []
    
    for primer, amplifiers in psInfo.amplifiers.items():
        if len(amplifiers) == 1:
            amp = amplifiers[0]
            hit_contig = amp.hit_info.split()[0] if amp.hit_info else ''
            
            if hit_contig not in contigs:
                if amp.length < 1000:
                    bad_primers.append(primer)
                else:
                    off_target_large.append(primer)
        else:
            if not multiHitPrimers(contigs, amplifiers):
                bad_primers.append(primer)
    
    return bad_primers, off_target_large

def process_file(ps_file, contigs):
    with open(ps_file, "r") as fh:
        ps_info = readPrimersearch(fh)
    return contigCompare(contigs, ps_info)

def main(args):
    # Read contig file (one per line)
    with open(args.contigFile, "r") as fh:
        contigs = [line.strip() for line in fh if line.strip()]
    
    bad_primers, off_target_large = process_file(args.psFile, contigs)

    with open(args.outfile, "w") as fh:
        # remove duplicates, and keep original orders
        fh.writelines(primer + "\n" for primer in dict.fromkeys(bad_primers))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Primersearch analysis tool')
    parser.add_argument('psFile', help=' .ps file')
    parser.add_argument('contigFile', help='Text file with one positive contig name per line')
    # parser.add_argument('numCores', type=int, help='Number of CPU cores to use')
    parser.add_argument('outfile', help='Base name for output files')
    
    args = parser.parse_args()
    main(args)