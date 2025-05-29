process MATCH_PRIMER {
    conda 'conda-forge::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"

    input:
    path (primers_files)
    

    output:
    // path "*.primer", emit: primer_output, optional: true
    // path "*.amplicon", emit: amplicon_output
    // val (matching_statement), emit: primer_matching_result
    path "matching_results", emit: primer_matching_result_file

    // path "versions.yml", emit: versions

    shell:
    '''
    match_primer.py --primers_files "!{primers_files}" \
                        --oligo_file "!{params.oligo_file}" \
                        --output "matching_results" 

    #cat <<-END_VERSIONS > versions.yml
    #"${task.process}":
    #    biopython: $(python -c "import Bio; print(Bio.__version__)")
    #END_VERSIONS
    '''
}