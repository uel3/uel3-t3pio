process PARSE_GENBANK {
    conda 'conda-forge::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    
    input:
    path gbk

    output:
    path "*.faa", emit: faa_files
    path "*_nucleotide_sequences.json", emit: nucleotide_files
    path "versions.yml", emit: versions

    script:
    """
    for file in ${gbk}; do
        base_name=\$(basename \$file .gbk)
        echo "Processing \$file"
        gbk_parser.py --input \$file --output_faa \${base_name}.faa --output_json \${base_name}_nucleotide_sequences.json
        echo "Finished processing \$file"
        ls -l \${base_name}.faa \${base_name}_nucleotide_sequences.json
    done
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        biopython: \$(python -c "import Bio; print(Bio.__version__)")
    END_VERSIONS
    """
}