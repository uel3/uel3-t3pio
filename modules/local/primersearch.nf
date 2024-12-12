process PRIMERSEARCH {
    conda 'bioconda::emboss==6.6.0'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/emboss:6.6.0--hf657eab_5':
        'biocontainers/emboss:6.6.0--h440b012_4' }"
    tag "${trimalFile.baseName}"
    errorStrategy "ignore"
    
    
    input:
    tuple path(trimalFile), path(primersearchFile)

    output:
    path("${trimalFile.baseName}.ps"), emit: search_output, optional: true
    path "primersearch_error.log", emit: error, optional: true
    path "versions.yml", emit: versions, optional: true

    shell:
    '''
    # Run primersearch
    if [[ -s "!{trimalFile}" ]] && [[ -s "!{primersearchFile}" ]]; then
        primersearch -seqall !{trimalFile} \
                    -infile !{primersearchFile} \
                    -mismatchpercent 6 \
                    -outfile !{trimalFile.baseName}.ps
    else
        echo "Error: Primersearch failed for !{trimalFile.baseName}" >> primersearch_error.log
    fi
    
    primersearch_version=$((consambig --version 2>&1) | sed 's/EMBOSS://')

    # it doesn't print out version info correctly..  empty string for now
    cat <<-END_VERSIONS > versions.yml
    "!{task.process}":
        emboss: ${primersearch_version} 
    END_VERSIONS
    '''

}