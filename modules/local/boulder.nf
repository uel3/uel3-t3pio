process BOULDER {
    conda 'conda-forge::biopython=1.78 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.78' :
        'quay.io/biocontainers/biopython:1.78' }"
    tag "${consambig.baseName}"
    
    
    input:
    path consambig

    output:
    path "*.boulder", emit: boulder_output, optional: true

    // path "versions.yml", emit: versions

    shell:
    '''
    prepare_boulderfile.py --fa_file !{consambig} --boulder_file !{params.boulder_file} 

    #cat <<-END_VERSIONS > versions.yml
    #"${task.process}":
    #    biopython: $(python -c "import Bio; print(Bio.__version__)")
    #END_VERSIONS
    '''
}