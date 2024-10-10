process PARSE_ORTHOFINDER {
    
    conda 'python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9' :
        'quay.io/biocontainers/python:3.9' }"
    
    input:
    path orthofinderTxt

    output:
    path 'orthofinder_parsed_results.txt', emit: orthogroup_results_list
    path "parse_orthofinder.log"         , emit: log
    path "versions.yml"           , emit: versions

    script:
    """
    parse_orthofinder.py --input ${orthofinderTxt} --output orthofinder_parsed_results.txt 2> parse_orthofinder.log

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
