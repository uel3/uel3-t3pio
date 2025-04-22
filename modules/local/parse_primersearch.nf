process PARSE_PRIMERSEARCH {
    conda 'conda-forge::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    tag "${primersearch.baseName}"

    input:
    tuple path(primersearch), path(good_contig_list)

    output:
    path "*.badprimer", emit: primer_output, optional: true

    shell:
    '''
    base_name=$(basename "!{primersearch}" .ps)
    parse_primersearch_filter.py !{primersearch} !{good_contig_list} "${base_name}.badprimer"



    #cat <<-END_VERSIONS > versions.yml
    #"${task.process}":
    #    biopython: $(python -c "import Bio; print(Bio.__version__)")
    #END_VERSIONS
    '''
}