process MUSCLE {
    
    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/muscle:3.8.1551--h7d875b9_6' :
        'biocontainers/muscle:3.8.1551--h7d875b9_6' }"

    input:
    path multifasta

    output:
    path "*.muscle"                                , emit: muscle_files
    path "*.log"                                   , emit: log
    path "versions.yml"                            , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = multifasta.baseName
    
    """
    muscle \\
        -in $multifasta \\
        -out ${prefix}.muscle \\
        -quiet \\
        -loga ${prefix}.log
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        muscle: \$(muscle -version |  sed 's/^MUSCLE v//; s/by.*\$//')
    END_VERSIONS
    """
}
