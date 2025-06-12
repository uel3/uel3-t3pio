process PARSE_PRIMER3 {
    conda 'conda-forge::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    tag "${primer3.baseName}"    
    errorStrategy 'terminate'
    
    input:
    path primer3

    output:
    path "*.Primers", emit: primer_output, optional: true
    path "*.binding", emit: primer_binding, optional: true
    path "*.fasta", emit: primer_amplicon, optional: true

    shell:
    '''
    parse_primer3.py --primer3_file !{primer3} 

    '''
}