process COMBINE_JSON {
    conda 'python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.9' :
        'quay.io/biocontainers/python:3.9' }" 
    
    input:
    path json_files

    output:
    path "combined_nucleotide_sequences.json", emit: nucleotide_dict
    path "versions.yml", emit: versions

    script:
    """
    combinejson.py combined_nucleotide_sequences.json ${json_files}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}