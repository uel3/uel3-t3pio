process PRIMERSEARCH {
    conda 'bioconda::emboss==6.5.7'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'docker://biocontainers/emboss:v6.5.7_cv2' : null}"    //6.6.0--h008e53c_10  6.6.0--h31157b7_10
        // does not have nextflow required 'ps' installed 'docker://biocontainers/emboss:v6.6.0dfsg-7b1-deb_cv1'
    // errorStrategy 'ignore'
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

    
    primersearch_version=$(primersearch --version)

    # it doesn't print out version info correctly..  empty string for now
    cat <<-END_VERSIONS > versions.yml
    "!{task.process}":
        primersearch: ${primersearch_version} 
    END_VERSIONS
    '''

}