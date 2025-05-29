process ORTHOFINDER_PARING {
    conda 'python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9' :
        'quay.io/biocontainers/python:3.9' }"
    input:
    path orthogroupResultsFile

    output:
    path "pared_orthogroups.txt", emit: pared_orthogroups
    path "versions.yml"         , emit: versions

    script:
    def args = task.ext.args ?: ''
    """
    echo "Debug: args are $args"
    orthofinderparing.py $args --orthogroups $orthogroupResultsFile --test_size ${params.og_group_size}
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}