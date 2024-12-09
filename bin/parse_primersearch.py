#!/usr/bin/env python
import argparse
from Bio import SeqIO
import parse_primer3 as pp3

class PrimerSearchResults:
    
    def __init__(self,primerInfo,sequenceName,ampLen,leftHit,rightHit,sequence):
        self.primerInfo = primerInfo
        self.sequenceName = sequenceName
        self.ampLen = ampLen
        self.leftHit = leftHit
        self.rightHit = rightHit
        self.sequence = sequence

#########################################################
#('Def') PrimersearchValidator() comments:
#Takes as input ('List') ampliconInfo
##### ('Int') numberIsolates
#Uses list comprehension to pull sequence names from ('List') ampliconInfo
#####Creates ('Set') sequencesSet of ('List') sequences
#####Checks for equal length to ensure no duplicate isolates pulled
#Checks correct number sequences present against ('Int') numberIsolates
#Returns ('True') if proper number of isolates and no duplicates present
#Returns ('False') if improper number of isolates and/or duplicates present
def PrimersearchValidator(ampliconInfo,numberIsolates):

    sequenceStrings = [ seq for seq in ampliconInfo if 'Sequence' in seq]
    
    sequences = []

    for seqs in sequenceStrings:
        
        seqs = seqs.strip('\t')
        seqs = seqs.strip('\n')
        seqs = seqs.split(':')[1]
        seqs = seqs.strip(' ')
        sequences.append(seqs.split('.')[0])

    sequencesSet = set(sequences)

    if len(sequences) != len(sequencesSet):
        
        return(False)

    if len(sequences) != numberIsolates:

        return(False)
    else:
        
        return(True)
    
        

#########################################################
#('Def') PrimersearchComber() comments:
#Takes as input ('List') ampliconInfo
#####('Primer') ('Object') primer
#####('Dictionary') sequenceRecordDict
#Parses ('List') ampliconInfo to find forwardHit/reverseHit/ampliconLen/sequenceName
#####for each isolate record present in ('List') ampliconInfo
#Pulls isolate sequence from ('Dictionary') sequenceRecordDict and slices ('String') for amplicon
#####sequence 
#Stores information in ('Object') ('PrimerSearchResults') for each isolate
#Returns ('List') of ('PrimerSearchResults') ('Objects')
def PrimersearchComber(ampliconInfo,primer,sequenceRecordDict):

    primersearchObjects = []
    
    for line in ampliconInfo:
        
        if line.startswith('Amplimer'):
            try: 
                forwardHit = int(ampliconInfo[ampliconInfo.index(line)+3].split(' ')[5])
                reverseHit = int((ampliconInfo[ampliconInfo.index(line)+4].split(' ')[5]).replace('[','').replace(']',''))
                print(ampliconInfo[ampliconInfo.index(line)+1])
                ampliconLen = int(ampliconInfo[ampliconInfo.index(line)+5].split(' ')[2])
                sequenceName = str(ampliconInfo[ampliconInfo.index(line)+1].split(' ')[1].strip(' ').strip('\n'))

                sequence = str(sequenceRecordDict[sequenceName].seq)
                sequence = (sequence.replace('-',''))

                sequence = sequence[forwardHit+primer.leftLen:ampliconLen-reverseHit-primer.rightLen]

                primersearchObject = PrimerSearchResults(primer,sequenceName,ampliconLen,forwardHit,reverseHit,sequence)

                primersearchObjects.append(primersearchObject)
            except IndexError as ie:
                print (str(ie))
                continue


    return(primersearchObjects)

#########################################################
#('Def') PrimersearchParser() comments:
#Takes as input ('String') primersearchFile file path
#####('Int') numberIsolates
#####('List') of ('Primer') ('Objects')
#####('String') trimalFile file path
#('IO') reads in primersearchFile to ('List') primersearchInfo
#Stores trimalFile into ('SeqIO') ('Dictionary') ('Object') sequenceRecordDict
#Indexes ('List') primersearchInfo on 'Primer name' + ('Primer') ('Object') primer.numer
#Slices ('List') primersearchInfo using index and ('Int') numerIsolates * 6 into ('List') ampliconInfo
#Sends ('List') ampliconInfo and ('Int') numberIsolates to ('Def') PrimersearchValidator()
#Sends ('List') ampliconInfo and ('Primer') ('Object') to ('Def') PrimersearchComber
#Returns ('List') of ('PrimerSearchResults') ('Objects')
def PrimersearchParser(primersearchFile,numberIsolates,primerObjectList,trimalFile):

    with open(primersearchFile,'r') as f:
        primersearchInfo = f.readlines()
    f.close()

    primersearchObjectLists = []
    
    primersearchObjectList = []


    sequenceRecordDict =SeqIO.to_dict(SeqIO.parse(trimalFile,'fasta'))


    for primer in primerObjectList:
        
        ampliconInfoStartIndex = primersearchInfo.index('Primer name '+str(primer.number)+'\n')

        ampliconInfo = primersearchInfo[ampliconInfoStartIndex:ampliconInfoStartIndex+(numberIsolates*6)+1]

        validationMark = PrimersearchValidator(ampliconInfo,numberIsolates)

        if validationMark == True:
            # print (f"ampliconInfo is: {ampliconInfo}")
            # print (f"primer is: {primer}")
            # print (f"sequenceRecordDict is: {sequenceRecordDict}")
            parsedInfo = PrimersearchComber(ampliconInfo,primer,sequenceRecordDict)
        
            primersearchObjectLists.append(parsedInfo)

        else:

            break

    for primersearchObjects in primersearchObjectLists:

        primersearchObjectList = primersearchObjectList + primersearchObjects

    return(primersearchObjectList)

#print out the cleared primers to a file with extension .Primers
def print_primers(trimal_file, primersearchObjectList):

    primerFileList = []
    for pss in primersearchObjectList: #primerPairObjectList: 
        primerInfoList = []
        primerInfoList.append(str(pss.primerInfo.orthogroupInfo.orthogroup)+'\t'+str(pss.primerInfo.number)+ \
                              '\n'+str(pss.ampLen)+'\t'+str(pss.leftHit)+'\t'+str(pss.rightHit)+ \
                                '\n'+pss.sequenceName+'\n'+pss.sequence)
        primerFileList.append(primerInfoList)

    f = open(trimal_file.split('.')[0]+'.Primers','w')
    for primerInfo in primerFileList:
        for primers in primerInfo:
            print(primers,file=f)
    f.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="parse primersearch outputs.")
    parser.add_argument("--primer3_file", required=True, help="Input primer3 file")
    parser.add_argument("--trimal_file", required=True, help="Input trimal file")
    parser.add_argument("--primersearch_file", required=True, help="Input primersearch file")
    parser.add_argument('--number_isolates', type=int, required=True, help='Number of isolates originally submitted')
    args = parser.parse_args()

    ps_list = PrimersearchParser(args.primersearch_file, \
                                args.number_isolates, \
                                pp3.primer3Parser(args.primer3_file), \
                                args.trimal_file)
    print_primers(args.trimal_file, ps_list)
    
    