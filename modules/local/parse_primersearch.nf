process PARSE_PRIMERSEARCH {
    conda 'conda-forge::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    tag "${primer3.baseName}"

    input:
    tuple path(primer3), path(trimal), path(primersearch)
    val (number_isolates)

    output:
    path "*.boulder", emit: boulder_output, optional: true
    path "*.amplicon", emit: amplicon_output

    // path "versions.yml", emit: versions

    shell:
    '''
    parse_primersearch.py --primer3_file !{primer3} \
                          --trimal_file !{trimal} \
                          --primersearch_file !{primersearch} \
                          --number_isolates !{number_isolates}

    #cat <<-END_VERSIONS > versions.yml
    #"${task.process}":
    #    biopython: $(python -c "import Bio; print(Bio.__version__)")
    #END_VERSIONS
    '''
}