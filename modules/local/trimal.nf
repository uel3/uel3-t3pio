//input for TrimAl is muscle files, muscle_files uel3-t3pio
//output channel containing each TrimAl file-this is required for consambig
//need to find trimAl v1.2?, earliest version on galaxy project is 1.4 which is also on github, same for quay, earliest is 1.4 -reached out via github about 1.2 availability 
//need to compile from source?
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
    
    trimal -in ${muscle_file} -out ${muscle_file.baseName}.trimAl -fasta -automated1

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        trimAl: "\$(trimal --version | sed -n 's/trimAl v\\(.*\\)/\\1/p')"
    END_VERSIONS
    """
}