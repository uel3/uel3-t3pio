process CONCATENATE_GOOD_PRIMERS {

    input:
    path parsed_primersearch_bad_primers
    path all_primers

    output:
    path 'concatenated_primers_specificity.txt', emit: candidate_primers

    script:
    """
    # Concatenate all bad primer files and save to temp_bad_primers.txt
    cat ${parsed_primersearch_bad_primers} > temp_bad_primers.txt

    # Extract first column from bad primers and save to temp_bad_primers_first_col.txt
    # Sort and deduplicate the bad primers and save to temp_bad_primers_sorted.txt
    cut -f1 temp_bad_primers.txt | sort -u > temp_bad_primers_sorted.txt

    # Extract first column from all primers and save to temp_all_primers_first_col.txt
    # Sort and deduplicate the all primers and save to temp_all_primers_sorted.txt
    cut -f1 "${all_primers}" | sort -u > temp_all_primers_sorted.txt

    # Get the difference (lines in all_primers but not in bad_primers) and save to temp_diff.txt
    comm -13 temp_bad_primers_sorted.txt temp_all_primers_sorted.txt > temp_diff.txt

    # Filter the good primers using the diff and save the result to final output file
    grep -Ff temp_diff.txt "${all_primers}" > concatenated_primers_specificity.txt

    # Clean up temporary files
    rm -rf temp_bad_primers.txt temp_bad_primers_sorted.txt temp_all_primers_sorted.txt temp_diff.txt

    """
}