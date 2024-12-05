process PARSE_PRIMER3 {
    conda 'conda-forge::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    
    input:
    path primer3

    output:
    path "*.boulder", emit: boulder_output, optional: true
    path "*.Primers", emit: primer_output, optional: true

    // path "versions.yml", emit: versions

    shell:
    '''
    parse_primer3.py --primer3_file !{primer3} 

    #cat <<-END_VERSIONS > versions.yml
    #"${task.process}":
    #    biopython: $(python -c "import Bio; print(Bio.__version__)")
    #END_VERSIONS
    '''
}