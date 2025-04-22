process TRIMAL {
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/trimal:1.4.1--0' :
        'quay.io/biocontainers/trimal:1.4.1--0' }"
    
    input:
    path muscle_file
    
    output:
    path "${muscle_file.baseName}.trimAl", emit: trimmed_alignment
    path "versions.yml", emit: versions
    
    script:
    """
    trimal -in ${muscle_file} -out ${muscle_file.baseName}.trimAl -fasta -automated1
    

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        trimAl: \$(trimal -v | grep -o 'v[0-9]\\+\\.[0-9]\\+\\.[0-9]\\+' | sed 's/v//')
    END_VERSIONS
    """
}