process ORTHOFINDER_PARING {
    
    input:
    path orthogroupResultsFile

    output:
    path "pared_orthogroups.txt", emit: pared_orthogroups
    path "versions.yml"         , emit: versions

    script:
    def args = task.ext.args ?: ''
    """
    echo "Debug: args are $args"
    orthofinderparing.py $args --orthogroups $orthogroupResultsFile
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}