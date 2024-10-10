process ORTHOFINDER_CLASS_CHECK {
    conda 'python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9' :
        'quay.io/biocontainers/python:3.9' }"
    
    input:
    path orthogroupResultsFile

    output:
    stdout emit: check_result

    script:
    """
    class_check_orthofinder.py ${orthogroupResultsFile}
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}