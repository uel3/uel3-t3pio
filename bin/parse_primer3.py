#!/usr/bin/env python
import argparse
import json
import subprocess
from Bio import SeqIO
import re

class Orthogroup:
    """"Parsed orthogroup info

    Attributes:
        orthogroup: String representing the orthogroup
        sequence: String representing the sequence
    """
    def __init__(self,orthogroup,sequence):

        #Returns an orthogroup object
        self.orthogroup = orthogroup
        self.sequence = sequence

class Primers:

    """
    Attributes:
        orthogroupInfo: String representing which orthogroup
        number: Int representing primer number
        leftSeq: String representing thge left sequence
        rightSeq: String representing the right sequence
    """
    
    def __init__(self,orthogroupInfo,number,leftSeq,rightSeq,leftHit,rightHit,leftLen,rightLen):
        self.orthogroupInfo = orthogroupInfo
        self.number = number
        self.leftSeq = leftSeq
        self.rightSeq = rightSeq
        self.leftHit = leftHit
        self.rightHit = rightHit
        self.leftLen = leftLen
        self.rightLen = rightLen

#########################################################
#('Def') primer3Parser() comments
#Takes as input a ('Dictionary') containing the STDOUT from primer3
#Initiates the ('List') primerPairObjectList which will hold the ('Class Objects') Primers
#Initiates the ('List') primerInfoList to hold the ('Strings') from the input ('Dictionary')
#Uses indexing on the ('List') primerInfoList to pull out ('Int') totalPrimersReturned
#('Int') totalPrimersReturned is used for the while loop to iterate through ('List') primerInfoList to pull out:
#
#('String') leftSequence
#('String') rightSequence
#('Int') leftHit
#('Int') rightHit
#('Int') leftLength
#('Int') rightLength
#Pulled information is stored in ('Class Object') Primers 
#Returns ('List') of ('Class Objects') Primers

def primer3Parser(primer3_file):

    with open(primer3_file,'r') as f:
        primer_lines = f.read()
    
    primer3Dict = {}
    # primer3Dict[(r2.split('\n')[0]).split('=')[1]] = r2.replace('=', '\n').split('\n')[1:]
    primer3Dict[(primer_lines.split('\n')[0]).split('=')[1]] = primer_lines.replace('=', '\n').split('\n')[1:]

    primerPairObjectList = []

    for k in primer3Dict.keys():
        
        primerInfoList = primer3Dict[k]
        try:

            totalPrimersReturned = int(primerInfoList[primerInfoList.index('PRIMER_PAIR_NUM_RETURNED') + 1])

            if totalPrimersReturned != 0:
                
                orthogroupObj = Orthogroup(primerInfoList[0][:9],primerInfoList[2])

                count = 0
                while count < totalPrimersReturned:
                    leftSequence = (primerInfoList[primerInfoList.index('PRIMER_LEFT_'+str(count)+'_SEQUENCE') + 1])
                    rightSequence = (primerInfoList[primerInfoList.index('PRIMER_RIGHT_'+str(count)+'_SEQUENCE') + 1])
                    leftHit = int((primerInfoList[primerInfoList.index('PRIMER_LEFT_'+str(count)) + 1]).split(',')[0])
                    rightHit = int((primerInfoList[primerInfoList.index('PRIMER_RIGHT_'+str(count)) + 1]).split(',')[0])
                    leftLength = int((primerInfoList[primerInfoList.index('PRIMER_LEFT_'+str(count)) + 1]).split(',')[1])
                    rightLength = int((primerInfoList[primerInfoList.index('PRIMER_RIGHT_'+str(count)) + 1]).split(',')[1])
                    
                    primerObj = Primers(orthogroupObj,count,leftSequence,rightSequence,leftHit,rightHit,leftLength,rightLength)
                    primerPairObjectList.append(primerObj)
                    count += 1

        except ValueError as e:
            print (f" ******************* caught error:  {str(e)}")
            continue

    #PrimerFlankingRegionCheck
    #Checks the sequence for inclusion of SNPs
    clearedPrimers = []
    for primer in primerPairObjectList:
        sequence = primer.orthogroupInfo.sequence[(primer.leftHit+primer.leftLen)-1:(primer.rightHit)-1]
        for letter in sequence:
            if letter not in ('ATGCN'):
                clearedPrimers.append(primer)
                break


    primerFileList = []
    for primers in clearedPrimers: #primerPairObjectList: 
        primerInfoList = []
        primerInfoList.append(str(primers.number)+'\t'+primers.leftSeq+'\t'+primers.rightSeq)
        primerFileList.append(primerInfoList)

    f = open(primer3_file.split('.')[0]+'.Primers','w')
    for primerInfo in primerFileList:
        for primers in primerInfo:
            print(primers,file=f)
    f.close()

    return(clearedPrimers)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="parse primer3 outputs.")
    parser.add_argument("--primer3_file", required=True, help="Input primer3 file")
    args = parser.parse_args()

    primer3Parser(args.primer3_file)