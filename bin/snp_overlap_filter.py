#!/usr/bin/env python

import os
import argparse

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
#Returns ('List') of ('Class Objects') Primers, and a dictionary of snp list
        
def primerScore(primer):
    spot = 0
    position = 1
    for letter in primer:
        if letter not in ('ATGC'):
            spot = position
        position += 1
    score = spot/(len(primer))
    return score

def snpOverlapFilter(snp_dict):
    keys = list(snp_dict.keys())
    to_delete = set()  # Store primers that need to be removed
    keyTrac = [] #track which primers have already been used to check, Sean's hackedOverlapFilter.py #103

    ### **Step 1: Remove same captured SNP primers (based on primer score)**
    for i in range(len(keys)):
        keyTrac.append(i) #keep track of used primers
        for j in range(i + 1, len(keys)):  # Compare each pair once
            key1, key2 = keys[i], keys[j]

            # If already marked for deletion, skip
            if key1 in to_delete or key2 in to_delete:
                continue

            snplist1, left1, right1 = snp_dict[key1]
            snplist2, left2, right2 = snp_dict[key2]

            # Convert to sorted tuples for direct comparison (order-independent)
            set1, set2 = set(snplist1), set(snplist2)

            # If snplists are exactly the same, choose the one with the lower score
            if set1 == set2:
                score1 = primerScore(left1) + primerScore(right1)
                score2 = primerScore(left2) + primerScore(right2)

                if score1 < score2:
                    to_delete.add(key2)
                # we keep tied primer score primers
                # elif score1 == score2: #Sean's hackedOverlapFilter.py #123
                #     if j not in keyTrac:
                #         to_delete.add(key2)
                # if score1 < score2:
                #     to_delete.add(key2)
                # elif score1 > score2:
                #     to_delete.add(key1)
                        
    ### Remove primers
    deleted_dict = {}  # List to store deleted keys
    for key in to_delete:
        deleted_dict[key] = snp_dict[key]
        del snp_dict[key]
        

    ### **Step 2: Remove primers where snplist is a subset of another**
    keys = list(snp_dict.keys())
    to_delete = set() 
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):  # Compare each pair once
            key1, key2 = keys[i], keys[j]

            snplist1, left1, right1 = snp_dict[key1]
            snplist2, left2, right2 = snp_dict[key2]

            set1, set2 = set(snplist1), set(snplist2)

            # Check if one snplist is a subset of the other
            # use logic in Sean's hackedOverlapFilter.py from line #131
            if set1.issubset(set2):
                score1 = primerScore(left1) + primerScore(right1)
                score2 = primerScore(left2) + primerScore(right2)
                if score1 > score2:
                    # del snp_dict[key1]
                    to_delete.add(key1)
            #     if score1 < score2:
            #         to_delete.add(key2)
            elif set2.issubset(set1):
                score1 = primerScore(left1) + primerScore(right1)
                score2 = primerScore(left2) + primerScore(right2)
                if score2 > score1:
                    to_delete.add(key2)

    ### Remove primers
    for key in to_delete:
        deleted_dict[key] = snp_dict[key]
        del snp_dict[key]

    return snp_dict, deleted_dict


def primer3Parser(primer3_file, valid_primer_list):

    with open(primer3_file,'r') as f:
        primer_lines = f.read()
    
    primer3Dict = {}
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

        if 'N' not in primer.leftSeq and 'N' not in primer.rightSeq:
            if any(letter not in "ATGCN" for letter in sequence):
                clearedPrimers.append(primer)
                continue

            #check for single base 'N'
            def check_isolated_N(string):
                # Handle the case where the string has only one character
                if len(string) == 1:
                    return string == 'N'  # Return True if it's 'N', False otherwise
                
                # Iterate through the string and check each 'N'
                for i in range(1, len(string) - 1):
                    if string[i] == 'N':
                        if string[i - 1] != 'N' and string[i + 1] != 'N':
                            return True  # Found an isolated 'N'
                return False

            if check_isolated_N(sequence):
                clearedPrimers.append(primer)


    #filtering...  keep only valid_primer_list
    clearedclearedPrimers = []  
    orthogroup = os.path.basename(primer3_file).split('.')[0]
    for primer in clearedPrimers:    
        full_primer = f"{orthogroup}primerGroup{primer.number}"
        if full_primer in valid_primer_list:
            clearedclearedPrimers.append(primer)


    #snp info
    snpdict = {}
    for primer in clearedclearedPrimers:
        sequence = primer.orthogroupInfo.sequence[(primer.leftHit+primer.leftLen)-1:(primer.rightHit)-1]
        a = 0
        snplist = []
        while a < len(sequence):
            site = sequence[a]
            if site not in ('ATGC'):
                snpSite = primer.leftHit + a 
                snplist.append(snpSite) #logic for finding snp positions in the amplicon
            a += 1

        snpdict[primer] = [snplist, primer.leftSeq, primer.rightSeq]

    final_snpdict, deleted_snpdict = snpOverlapFilter(snpdict)
    final_clearedPrimers = final_snpdict.keys()


    for key in final_snpdict:
        snplist, left, right = final_snpdict[key]
        final_snpdict[key] = (snplist, left, right, primerScore(left)+primerScore(right))
        

    return(final_snpdict, deleted_snpdict)  #test hack only



def read_column_from_file_b(file_b_path):
    """Read the 4th column from file B and store values in a dictionary by OG identifier."""
    primer_groups = {}
    with open(file_b_path, 'r') as file_b:
        for line in file_b:
            parts = line.strip().split()
            # if len(parts) >= 4:
            #     og_key = parts[3]
            if len(parts) >= 1: # if the file_b has only 1 column
                og_key = parts[0]
                og_prefix = og_key.split('primerGroup')[0]  # Extract OG ID prefix
                if og_prefix not in primer_groups:
                    primer_groups[og_prefix] = []
                primer_groups[og_prefix].append(og_key)
    return primer_groups

# def process_primer3_files(primer3_folder, file_b_path, output_file, deleted_primers_file):
def process_primer3_files(primer3_files, primer_file, output_file):
    """Process each .primer3 file, filter using file B, and save output."""
    primer_groups = read_column_from_file_b(primer_file)
    print (f"primer_groups size is: {len(primer_groups)}")
    output_lines = []

    deleted_lines = []
    
    for primer3_file in primer3_files:
        og_id = os.path.basename(primer3_file).split('.')[0]  # Extract OG identifier

        if og_id in primer_groups:

            cleared_dict, deleted_dict = primer3Parser(primer3_file, primer_groups[og_id])

            orthogroup = os.path.basename(primer3_file).split('.')[0]

            for primers in cleared_dict:   
                output_lines.append(f"{orthogroup}primerGroup{primers.number}\t{cleared_dict[primers][1]}\t{cleared_dict[primers][2]}")  
    
    with open(output_file, 'w') as out_file:
        out_file.write("\n".join(output_lines) + "\n")

# # Example usage
# primer3_folder = "/scicomp/home-pure/qtl7/test/t3pio/uel3-t3pio/test_primer3_01132025_2/Primer3"
# # file_b_path = "/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/Metagenomes_primersearch/32677_masterPrimer_coal_bad_removed.stool.overlapped.primers"
# # file_b_path = "/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/test2/T3Pio/T3Pio_Main/27752_primers_list"
# file_b_path = "/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/test2/T3Pio/T3Pio_Main/stool_good_primers_updated"
# # output_file = "/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/Metagenomes_primersearch/32677_masterPrimer_coal_bad_removed.stool.overlapped.snpfiltered.primers"
# # output_file = "/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/test2/T3Pio/T3Pio_Main/stool_good.snpfiltered_primers_list_updated_hitpositions"
# output_file = "/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/test2/T3Pio/T3Pio_Main/kept_snp_filtered_primers_subsettested"
# deleted_primers_file = "/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/test2/T3Pio/T3Pio_Main/deleted_snp_filtered_primers_subsettested"
# process_primer3_files(primer3_folder, file_b_path, output_file, deleted_primers_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SNP overlapping filtering')
    parser.add_argument('p3File', nargs='+', help='a string list of primer3 output file')
    parser.add_argument('primerFile', help='Text file with one primer per line')
    # parser.add_argument('numCores', type=int, help='Number of CPU cores to use')
    parser.add_argument('outFile', help='Base name for output files')
    
    args = parser.parse_args()
    process_primer3_files(args.p3File, args.primerFile, args.outFile)