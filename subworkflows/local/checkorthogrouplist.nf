include { ORTHOFINDER_CLASS_CHECK } from '../../modules/local/orthofinderclasscheck'
workflow ORTHOGROUP_LIST_PASS_FAIL {
    
	take:
    orthogroupResultsFile

    main:
    ORTHOFINDER_CLASS_CHECK(orthogroupResultsFile)

    check_result = ORTHOFINDER_CLASS_CHECK.out.check_result
        .map { it.trim() }
        .filter { it } // Remove empty lines
        .map { result ->
            if (result == "PASS") {
                return [true, "Orthogroup objects check passed"]
            } else {
                return [false, "Orthogroup objects check failed: ${result}"]
            }
        }

    emit:
    check_result
}


