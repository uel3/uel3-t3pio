process PRIMERSEARCH {
    conda 'bioconda::emboss==6.6.0'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/emboss:6.6.0--hf657eab_5':
        'biocontainers/emboss:6.6.0--h440b012_4' }"
    tag "${trimalFile.baseName}"
    
    input:
    tuple path(trimalFile), path(primersearchFile)

    output:
    path("${trimalFile.baseName}.ps"), emit: search_output, optional: true
    path "primersearch_error.log", emit: error, optional: true
    path "versions.yml", emit: versions, optional: true

    shell:
    '''
    # Run primersearch
    primersearch -seqall !{trimalFile} \
                 -infile !{primersearchFile} \
                 -mismatchpercent 6 \
                 -outfile !{trimalFile.baseName}.ps 2> primersearch_error.log

    # Error handling
    if [ $? -ne 0 ]; then
        echo "Error: Primersearch failed for !{trimalFile.baseName}" >&2
        exit 1
    fi

    
    primersearch_version=$((consambig --version 2>&1) | sed 's/EMBOSS://')

    # it doesn't print out version info correctly..  empty string for now
    cat <<-END_VERSIONS > versions.yml
    "!{task.process}":
        emboss: ${primersearch_version} 
    END_VERSIONS
    '''

}