process PARSE_GENBANK {
    publishDir "${params.outdir}", mode: 'copy'
    conda 'bioconda::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    
    input:
    path gbk

    output:
    path "*.faa", emit: faa_files
    path "nucleotide_sequences", emit: nucleotide_dir
    path "nucleotide_sequences/*.json", emit: nucleotide_files
    path "versions.yml", emit: versions

    script:
    """
    mkdir -p nucleotide_sequences
    for file in ${gbk}; do
        base_name=\$(basename \$file .gbk)
        gbk_parser.py --input \$file --output_faa \${base_name}.faa --output_json nucleotide_sequences/\${base_name}_nucleotide_sequences.json
    done
    # Ensure .faa files were generated
    if [ -z "\$(ls *.faa)" ]; then
        echo "Error: No .faa files were generated" >&2
        exit 1
    fi

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        biopython: \$(python -c "import Bio; print(Bio.__version__)")
    END_VERSIONS
    """
}