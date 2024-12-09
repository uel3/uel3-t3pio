#!/usr/bin/env python
import argparse
import json
import subprocess
from Bio import SeqIO
import re


#('Def') BoulderIOParser() comments
#Takes as input ('String') boulderFile file path
#Parses ('List') designInfo
#Returns ('List') primerDesignInfo
def BoulderIOParser(boulderFile):

    with open(boulderFile, 'r') as f:
        
        designInfo = f.readlines()

    f.close()
    
    primerDesignInfo = []

    for info in designInfo:
        
        primerDesignInfo.append(info.strip('\n'))

    return(primerDesignInfo)


#Takes as input ('String') file path to a consambig file ('consambigFile')
#####('List') of ('Strings') containing all the global primer3 values used in a boulder file
#reads in ('consambigFile') and creates the Sequence information for primer3
#generates the boulder file
#Runs primer3
#####Captures stdout from primer3 and generates a ('Dictionary') ('primer3Dict')
#Returns ('Dictionary') (dictionary[Orthogroup]:['Primer3',...,'Output'] as a json file
# def RunPrimer3(consambigFile, primer3List, outputJsonFile):
def prepare_boulder(consambigFile, primer3List):
    # Extract base filename for the Primer3 input file
    primer3BoulderFile = consambigFile.split('.')[0] + ".boulder"
    
    # Read consensus sequence information
    consensusInfo = list(SeqIO.parse(consambigFile, 'fasta'))
    
    # Create the Primer3 input file
    with open(primer3BoulderFile, 'w') as f:
        orthogroup = f"SEQUENCE_ID={consensusInfo[0].id}"
        consensusSeq = f"SEQUENCE_TEMPLATE={re.sub(r'[a-z]', 'N', str(consensusInfo[0].seq).strip())}"
        
        print(orthogroup, file=f)
        print(consensusSeq, file=f)
        
        for i in primer3List:
            print(i, file=f)
    
    # # Run Primer3 and capture the output
    # r1 = subprocess.Popen(['primer3_core', primer3BoulderFile], stdout=subprocess.PIPE)
    # r2 = r1.stdout.read().decode('ascii')
    
    # # Parse the Primer3 output into a dictionary
    # primer3Dict = {}
    # primer3Dict[(r2.split('\n')[0]).split('=')[1]] = r2.replace('=', '\n').split('\n')[1:]
    
    # # Save the dictionary as a JSON file
    # with open(outputJsonFile, 'w') as jsonFile:
    #     json.dump(primer3Dict, jsonFile, indent=4)
    
    # return outputJsonFile
            
    return primer3BoulderFile


    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="generate boulder file for primer3.")
    parser.add_argument("--fa_file", required=True, help="Input consambig.fa file")
    parser.add_argument("--boulder_file", required=True, help="Input boulder file template for primer3")
    args = parser.parse_args()

    prepare_boulder(args.fa_file, BoulderIOParser(args.boulder_file))