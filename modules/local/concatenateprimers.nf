process CONCATENATE_PRIMERS {
    
    input:
    path parsed_primersearch_primers

    output:
    path 'concatenated_OGprimers.txt', emit: candidate_primers

    script:
    """
    cat $parsed_primersearch_primers > concatenated_OGprimers.txt
    """
}