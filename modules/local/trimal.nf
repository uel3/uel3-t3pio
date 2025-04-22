process TRIMAL {
    //container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        //'https://depot.galaxyproject.org/singularity/trimal:1.4.1--0' :
        //'quay.io/biocontainers/trimal:1.4.1--0' }"
    
    input:
    path muscle_file
    
    output:
    path "${muscle_file.baseName}.trimAl", emit: trimmed_alignment
    path "versions.yml", emit: versions
    
    script:
    """
    ${params.trimal_path} -in ${muscle_file} -out ${muscle_file.baseName}.trimAl -fasta -automated1
    

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        trimAl: "\$(${params.trimal_path} --version | sed -E 's/^[^0-9]*([0-9.]+[^[:space:]]*).*$/\1/')"
    END_VERSIONS
    """
}