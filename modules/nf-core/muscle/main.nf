process MUSCLE {
    label 'process_high'
    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/muscle%3A5.3--h4ac6f70_0' :
        'biocontainers/muscle:5.3--h4ac6f70_0' }"

    input:
    path multifasta

    output:
    path "*.muscle"                                , emit: muscle_files
    //path "*.log"                                   , emit: log
    path "versions.yml"                            , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = multifasta.baseName
    
    """
    muscle \\
        -super5 $multifasta \\
        -output ${prefix}.muscle \\
        -quiet

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        muscle: \$(muscle -version |  sed 's/^MUSCLE v//; s/by.*\$//')
    END_VERSIONS
    """
}
