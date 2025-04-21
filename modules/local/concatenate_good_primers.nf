process CONCATENATE_GOOD_PRIMERS {
    conda 'conda-forge::pandas=2.2.3 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/scanpy%3A1.7.0--py_0' :
        'quay.io/biocontainers/biopython:1.78' }"

    input:
    path parsed_primersearch_bad_primers
    path all_primers

    output:
    path 'concatenated_primers_specificity.txt', emit: candidate_primers
    // path 'concatenated_badprimers.txt', emit: bad_primers, optional: true

    script:
    """
    filter_primers.py --bad_primers $parsed_primersearch_bad_primers \
                      --all_primers $all_primers \
                      --output concatenated_primers_specificity.txt \
                      --bad_primers_output concatenated_badprimers.txt

    """
}