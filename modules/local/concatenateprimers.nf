process CONCATENATE_PRIMERS {
    
    input:
    path parsed_primersearch_primers

    output:
    path 'concatenated_primers_primer3.txt', emit: candidate_primers

    script:
    """
    cat $parsed_primersearch_primers > concatenated_primers_primer3.txt
    """
}