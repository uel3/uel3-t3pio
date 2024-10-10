process COMBINE_FAA_FILES {
    publishDir "${params.outdir}", mode: 'copy'

    input:
    path faa_files

    output:
    path("combined_proteins.faa"), emit: combined_proteins

    script:
    """
    cat ${faa_files} > combined_proteins.faa
    """
}
