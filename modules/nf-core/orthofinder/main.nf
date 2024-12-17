process ORTHOFINDER {
    //tag "$meta.id"
    label 'process_high'

    conda "${moduleDir}/environment.yml"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        // 'https://depot.galaxyproject.org/singularity/orthofinder:2.5.5--hdfd78af_2':
        // 'biocontainers/orthofinder:2.5.5--hdfd78af_2' }"
        'https://depot.galaxyproject.org/singularity/orthofinder%3A2.1.2--py27_0':
        null }"


    input:
    path faa_files

    output:
    path "orthofinder_results", emit: orthofinder
    path "orthofinder_results/Orthogroups.txt", emit: orthogroups
    path "versions.yml", emit: versions

    script:
    def args = task.ext.args ?: ''
    def date = new java.util.Date().format('MMddHHmm')
   
    """
    mkdir -p faa_dir
    mv ${faa_files} faa_dir/
    
    mkdir -p orthofinder_results
    orthofinder \\
        -f faa_dir \\
        -t $task.cpus \\
        -a $task.cpus \\
        -og \\
        -n ${date}_orthofinder \\
        $args
    
    mv faa_dir/Results_${date}_orthofinder*/* orthofinder_results/

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        orthofinder: \$(orthofinder -h | sed -n 's/.*version \\(.*\\) Copy.*/\\1/p')
    END_VERSIONS
    """
}
