process SNP_REDUNDANCY_FILTER {
    
    input:
    path primer3_files
    path candidate_primers

    output:
    path 'concatenated_primers_snpfiltered.txt', emit: snp_filtered_good_primers
    path 'concatenated_primers_final*.txt', emit: final_primers

    script:
    """
    snp_overlap_filter.py $primer3_files $candidate_primers concatenated_primers_snpfiltered.txt
    run_primerscore.py concatenated_primers_snpfiltered.txt concatenated_primers_final.txt

    """
}