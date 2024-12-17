process COMPARE_PRIMERS {
    conda 'python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9' :
        'quay.io/biocontainers/python:3.9' }"
    
    input:
    path reference
    path search
    
    output:
    path "matches.txt", emit: matches
    path "unmatched_ref.txt", emit: unmatched_ref
    path "unmatched_search.txt", emit: unmatched_search
    
    script:
    """
    
    compare_legacy_HMAS_RC.py \
        --reference ${reference} \
        --search ${search} \
        --matches matches.txt \
        --unmatched-ref unmatched_ref.txt \
        --unmatched-search unmatched_search.txt
    """
}