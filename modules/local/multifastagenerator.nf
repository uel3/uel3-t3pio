process MULTIFASTA_GENERATOR {
    conda 'python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9' :
        'quay.io/biocontainers/python:3.9' }"
    
    input:
    path pared_orthogroups
    path combined_nucleotide_json

    output:
    path "*.fasta", emit: multifasta
    path "versions.yml", emit: versions

    script:
    """
    multifastagenerator.py \
        --orthogroups $pared_orthogroups \
        --nucleotide_json $combined_nucleotide_json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
