import argparse
import multiprocessing 
from functools import partial
import glob

'''
python primer_SpecificityTest_positive.py /scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/StoolBugsMultifastas_primersearch/ /scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/StoolBugsMultifastas_primersearch_2023/bugs_samonella_contigs_list 10 stool_primer_specificity_result
'''
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
        # elif line.startswith('Amplimer'):
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
            # if obj.length > 100:
            #     print (f"hit_contig is: {hit_contig}, obj.length is {obj.length}")
            quality = False
    return quality

def multiHitWriter(primer, psObj):
    with open(f"{primer}--MultiHitInfo", "w") as fh:
        for obj in psObj:
            fh.write(f"{obj.hit_info}\n{obj.length}\n")

def contigCompare(contigs, psInfo):
    bad_primers = []
    off_target_large = []
    
    for primer, amplifiers in psInfo.amplifiers.items():
        if len(amplifiers) == 1:
            amp = amplifiers[0]
            hit_contig = amp.hit_info.split()[0] if amp.hit_info else ''
            
            if hit_contig not in contigs:
                if amp.length < 1000:
                    # bad_primers.append(primer)
                    bad_primers.append(f"{primer}_{amp.length}")
                else:
                    off_target_large.append(primer)
        else:
            if not multiHitPrimers(contigs, amplifiers):
                bad_primers.append(primer)
            # multiHitWriter(primer, amplifiers)
    
    return bad_primers, off_target_large

def process_file(ps_file, contigs):
    with open(ps_file, "r") as fh:
        ps_info = readPrimersearch(fh)
    return contigCompare(contigs, ps_info)

def main(args):
    # Read contig file (one per line)
    with open(args.contigFile, "r") as fh:
        contigs = [line.strip() for line in fh if line.strip()]
    
    # Get all .ps files in directory
    ps_files = glob.glob(f"{args.psFilePath}/*.ps")
    
    # Parallel processing
    with multiprocessing.Pool(args.numCores) as pool:
        results = pool.map(partial(process_file, contigs=contigs), ps_files)
    
    # Write outputs
    with open(args.outfile, "w") as fh:
        # fh.write("\n".join([p for res in results for p in res[0]]))
        # remove duplicates, and keep original orders
        fh.write("\n".join(list(dict.fromkeys(p for res in results for p in res[0]))))
    
    with open(f"{args.outfile}_large_offtargets", "w") as fh:
        fh.write("\n".join([p for res in results for p in res[1]]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Primersearch analysis tool')
    parser.add_argument('psFilePath', help='Directory containing .ps files')
    parser.add_argument('contigFile', help='Text file with one positive contig name per line')
    parser.add_argument('numCores', type=int, help='Number of CPU cores to use')
    parser.add_argument('outfile', help='Base name for output files')
    
    args = parser.parse_args()
    main(args)


'''
FLOWCHART

┌───────────────────────────────┐
│     Command-Line Execution    │
└───────────────────────────────┘
       │
       ├─ Parse arguments:
       │   - psFilePath (directory with .ps files)
       │   - contigFile (text file, 1 contig/line)
       │   - numCores (multiprocessing)
       │   - outfile (base output name)
       │
       ▼
┌───────────────────────────────┐
│        Load Contig List       │
└───────────────────────────────┘
       │
       ├─ Read contigFile:
       │   → ["contig123", "contig456", ...]
       │
       ▼
┌───────────────────────────────┐
│   Get Primersearch Files      │
└───────────────────────────────┘
       │
       ├─ glob.glob("*.ps")
       │   → ["file1.ps", "file2.ps", ...]
       │
       ▼
┌───────────────────────────────┐
│  Parallel Processing (Pool)   │
└───────────────────────────────┘
       │
       ├─ For each .ps file:
       │   │
       │   ├─ process_file():
       │   │   │
       │   │   ├─ readPrimersearch():
       │   │   │   - Parse primer names
       │   │   │   - Extract Amplimer objects
       │   │   │     (hit_info + length)
       │   │   │
       │   │   ├─ contigCompare():
       │   │   │   │
       │   │   │   ├─ Single Amplimer:
       │   │   │   │   → Check contig membership
       │   │   │   │   → <1000bp → bad_primers
       │   │   │   │   → ≥1000bp → off_target_large
       │   │   │   │
       │   │   │   ├─ Multiple Amplimers:
       │   │   │   │   → multiHitPrimers()
       |   |   |   |      Check ALL amplimers:
       │   │   │   │      - If ANY hit is invalid (contig not approved + length <1000)
       │   │   │   │        → quality=False → badPrimers
       │   │   │   │      - Else → Valid
       │   │   │   │
       │   │   │   └─ Return classification
       │   │   │
       │   │   └─ Return (bad_primers, off_target_large)
       │   │
       │   └─ Collect results
       │
       ▼
┌───────────────────────────────┐
│         Write Outputs         │
└───────────────────────────────┘
       │
       ├─ Main output:
       │   args.outfile → All bad primers
       │
       ├─ Secondary output:
       │   args.outfile + "_large_offtargets"
       │   → Primers with long off-targets
       │
       ▼
'''