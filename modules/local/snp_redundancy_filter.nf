process SNP_REDUNDANCY_FILTER {
    conda 'conda-forge::pandas=2.2.3 python=3.9'
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/scanpy%3A1.7.0--py_0' :
        'quay.io/biocontainers/biopython:1.78' }"
    
    input:
    path primer3_files
    path candidate_primers

    output:
    path 'concatenated_primers_snpfiltered.txt', emit: snp_filtered_good_primers, optional: true
    path 'concatenated_primers_final*.txt', emit: final_primers, optional: true
    path "seed_used.txt", optional: true

    script:
    """
    snp_overlap_filter.py $primer3_files $candidate_primers concatenated_primers_snpfiltered.txt

    if [[ "${params.random}" == "true" ]]; then
        if [ "${params.seed}" = "null" ] || [ -z "${params.seed}" ]; then
            echo "random option selected, but no seed provided."
            run_primerscore.py concatenated_primers_snpfiltered.txt concatenated_primers_final.txt --random ${params.random} --seed_text seed_used.txt
        elif expr "${params.seed}" + 0 >/dev/null 2>&1; then
            echo "Running with seed = ${params.seed}"
            run_primerscore.py concatenated_primers_snpfiltered.txt concatenated_primers_final.txt --seed ${params.seed} --random ${params.random} --seed_text seed_used.txt
        else
            echo "Error: --seed must be an integer if provided. Got '${params.seed}'"
            exit 1
        fi
    else
        echo "Random mode not enabled."
        run_primerscore.py concatenated_primers_snpfiltered.txt concatenated_primers_final.txt
    fi
    


   

    """
}
