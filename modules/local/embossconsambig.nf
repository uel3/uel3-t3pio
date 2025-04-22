process CONSAMBIG {
    //container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        //'https://depot.galaxyproject.org/singularity/emboss:6.6.0--hf657eab_5':
        //'biocontainers/emboss:6.6.0--h440b012_4' }"
    
    input:
    path trimmed_alignment
    
    output:
    path "${trimmed_alignment.baseName}.fa", emit: ambiguous_consensus
    path "versions.yml", emit: versions
    
    script:
    """
    /scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/library_versions_t3pio/EMBOSS-6.4.0/emboss/consambig -sequence ${trimmed_alignment} -outseq ${trimmed_alignment.baseName}.fa -name ${trimmed_alignment.baseName} -snucleotide -sformat1 fasta -osformat2 fasta

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        emboss: \$(echo \$(/scicomp/groups/OID/NCEZID/DFWED/EDLB/projects/T3Pio_Data/library_versions_t3pio/EMBOSS-6.4.0/emboss/consambig -version 2>&1) | sed 's/EMBOSS://')
    END_VERSIONS
    """
}