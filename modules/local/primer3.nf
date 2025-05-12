process PRIMER3 {
     conda 'bioconda::primer3==2.6.1'
     container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/primer3:2.6.1--pl5321hdbdd923_4' :
        'quay.io/biocontainers/primer3:2.6.1--pl5321hdbdd923_4' }"
    tag "${boulder.baseName}"
    
    input:
    path boulder

    output:
    path "*.json", emit: primer3_file, optional: true
    path "*.boulder", emit: boulder_file, optional: true
    path "*.primer3", emit: primer3_output, optional: true

    path "versions.yml", emit: versions, optional: true

    shell:
    '''
    base_name=$(basename "!{boulder}" .boulder)
    primer3_core "!{boulder}" > "${base_name}.primer3"

    primer3_version=$(primer3_core -ab)

    cat <<-END_VERSIONS > versions.yml
    "!{task.process}":
        primer3: "${primer3_version}"
    END_VERSIONS
    '''
}