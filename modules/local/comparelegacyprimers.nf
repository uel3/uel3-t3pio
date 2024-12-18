process COMPARE_PRIMERS {
    conda 'python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9' :
        'quay.io/biocontainers/python:3.9' }"
    
    input:
    path reference
    path search
    
    output:
    path "${reference.baseName}_matches.txt", emit: reference_primer_matches
    path "${reference.baseName}_unmatched.txt", emit: unmatched_reference_primers
    path "${search.baseName}_unmatched.txt", emit: unmatched_search_file_primers
    
    script:
    """
    
    compare_legacy_HMAS.py \
        --reference ${reference} \
        --search ${search} \
        --matches ${reference.baseName}_matches.txt \
        --unmatched-ref ${reference.baseName}_unmatched.txt \
        --unmatched-search ${search.baseName}_unmatched.txt
    """
}