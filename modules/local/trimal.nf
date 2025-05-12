
process TRIMAL {
    
    label 'process_high'
    conda 'bioconda::trimal==1.5.0'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/trimal%3A1.5.0--h9948957_2' :
        'quay.io/biocontainers/trimal:1.5.0--h9948957_2' }"
    
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
        trimAl: "\$(${params.trimal_path} --version | sed -n 's/trimAl v\\(.*\\)/\\1/p')"
    END_VERSIONS
    """
}