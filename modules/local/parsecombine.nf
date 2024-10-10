process PARSE_GENBANK {
    publishDir "${params.outdir}", mode: 'copy'
    conda 'bioconda::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    
    input:
    path gbk

    output:
    path "${gbk.baseName}.faa", emit: faa
    path "${gbk.baseName}_nucleotide_sequences.json", emit: nucleotide_seq

    script:
    """
    gbk_parser.py --input ${gbk} --output_faa ${gbk.baseName}.faa --output_json ${gbk.baseName}_nucleotide_sequences.json
    """
}

process COMBINE_FAA_FILES {
    publishDir "${params.outdir}", mode: 'copy'

    input:
    path faa_files

    output:
    path "combined_proteins.faa"

    script:
    """
    cat ${faa_files} > combined_proteins.faa
    """
}