/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PRINT PARAMS SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { paramsSummaryLog; paramsSummaryMap } from 'plugin/nf-validation'

def logo = NfcoreTemplate.logo(workflow, params.monochrome_logs)
def citation = '\n' + WorkflowMain.citation(workflow) + '\n'
def summary_params = paramsSummaryMap(workflow)

// Print parameter summary log to screen
log.info logo + paramsSummaryLog(workflow) + citation

WorkflowT3pio.initialise(params, log)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CONFIG FILES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

ch_multiqc_config          = Channel.fromPath("$projectDir/assets/multiqc_config.yml", checkIfExists: true)
ch_multiqc_custom_config   = params.multiqc_config ? Channel.fromPath( params.multiqc_config, checkIfExists: true ) : Channel.empty()
ch_multiqc_logo            = params.multiqc_logo   ? Channel.fromPath( params.multiqc_logo, checkIfExists: true ) : Channel.empty()
ch_multiqc_custom_methods_description = params.multiqc_methods_description ? file(params.multiqc_methods_description, checkIfExists: true) : file("$projectDir/assets/methods_description_template.yml", checkIfExists: true)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT LOCAL MODULES/SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// SUBWORKFLOW: Consisting of a mix of local and nf-core/modules
//
//include { INPUT_CHECK } from '../subworkflows/local/input_check'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT NF-CORE MODULES/SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// MODULE: Installed directly from nf-core/modules
//



// Import modules
include { PARSE_GENBANK               } from '../modules/local/parsegbk'
include { ORTHOFINDER                 } from '../modules/nf-core/orthofinder'
include { PARSE_ORTHOFINDER           } from '../modules/local/orthofinderparser'
include { ORTHOFINDER_PARING          } from '../modules/local/orthofinderparing'
include { COMBINE_JSON                } from '../modules/local/combineparsedjson'
include { MULTIFASTA_GENERATOR        } from '../modules/local/multifastagenerator'
include { MUSCLE                      } from '../modules/nf-core/muscle'
include { TRIMAL                      } from '../modules/local/trimal'
include { CONSAMBIG                   } from '../modules/local/embossconsambig'
include { MULTIQC                     } from '../modules/nf-core/multiqc/main'
include { CUSTOM_DUMPSOFTWAREVERSIONS } from '../modules/nf-core/custom/dumpsoftwareversions/main'
include { PRIMER3                     } from '../modules/local/primer3'
include { BOULDER                     } from '../modules/local/boulder'
include { PARSE_PRIMER3               } from '../modules/local/parse_primer3'
include { PRIMERSEARCH                } from '../modules/local/primersearch'
include { PARSE_PRIMERSEARCH          } from '../modules/local/parse_primersearch'
include { CONCATENATE_PRIMERS         } from '../modules/local/concatenateprimers'
include { COMPARE_PRIMERS             } from '../modules/local/comparelegacyprimers'
include { CONCATENATE_GOOD_PRIMERS    } from '../modules/local/concatenate_good_primers'
include { SNP_REDUNDANCY_FILTER       } from '../modules/local/snp_redundancy_filter'

//Import subworkflows
include { ORTHOGROUP_LIST_PASS_FAIL } from '../subworkflows/local/checkorthogrouplist'
/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

// Info required for completion email and summary
def multiqc_report = []
// Define input parameters

// Create flags for --contig_file and --good_contig_list (for filtering part)
contig_file_ok = params.contig_file && file(params.contig_file).exists()
contig_list_ok = params.good_contig_list && file(params.good_contig_list).exists()

// Validate inputs
workflow T3PIO {

    ch_versions = Channel.empty()

    //
    // SUBWORKFLOW: Read in samplesheet, validate and stage input files
    //

    stool_contigs_ch = Channel.fromPath("${params.contig_file}/*.fna")
    stool_good_contig_list_ch = Channel.fromPath("${params.good_contig_list}")

    // Create a channel with all GenBank files in the specified directory
    gbk_files_ch = Channel.fromPath("${params.input}/*.gbk")
        .ifEmpty { error "No GenBank files found in ${params.input}" }
    // Collect all files to count them before proceeding
    gbk_files_ch.collect().map { files ->
        // Check if number of files matches number_isolates param
        if (files.size() != params.number_isolates) {
            error "Found ${files.size()} GenBank files but expected ${params.number_isolates} based on your config. Please check your input directory or update number_isolates parameter."
        }
        return files
    }.flatten()
    .set { verified_gbk_files_ch }
    // Run the PARSE_GENBANK process for each file
    PARSE_GENBANK(gbk_files_ch)
    // Format the output for ORTHOFINDER
    // Collect all .faa and .json files into a single list
    all_faa_files = PARSE_GENBANK.out.faa_files.collect()
    // Collect all individual JSON files
    nucleotide_files_ch = PARSE_GENBANK.out.nucleotide_files.collect()

    // Combine all JSON files
    COMBINE_JSON(nucleotide_files_ch)

    // Run ORTHOFINDER only after all .faa files are processed
    ORTHOFINDER(all_faa_files)
    ch_versions = ch_versions.mix(ORTHOFINDER.out.versions)
    
    PARSE_ORTHOFINDER(ORTHOFINDER.out.orthogroups)
    ch_versions = ch_versions.mix(ORTHOFINDER.out.versions)

    ORTHOGROUP_LIST_PASS_FAIL(PARSE_ORTHOFINDER.out.orthogroup_results_list)

    ORTHOGROUP_LIST_PASS_FAIL.out.check_result
        .ifEmpty { error "Orthogroup objects check produced no output" }
        .map { passed, message ->
            log.info(message)
            if (!passed) {
                error(message)
            }
            return "Orthogroup check passed. Proceeding with workflow."
        }
        .set { proceed_signal }
    ORTHOFINDER_PARING(PARSE_ORTHOFINDER.out.orthogroup_results_list)
    ch_versions = ch_versions.mix(ORTHOFINDER_PARING.out.versions)
    MULTIFASTA_GENERATOR(ORTHOFINDER_PARING.out.pared_orthogroups,COMBINE_JSON.out.nucleotide_dict)
    ch_versions = ch_versions.mix(MULTIFASTA_GENERATOR.out.versions)
    MUSCLE(MULTIFASTA_GENERATOR.out.multifasta.flatten())
    ch_versions = ch_versions.mix(MUSCLE.out.versions)
    TRIMAL(MUSCLE.out.muscle_files) //using trimAl 1.2
    ch_versions = ch_versions.mix(TRIMAL.out.versions)
    CONSAMBIG(TRIMAL.out.trimmed_alignment) //using emboss 6.4.0
    ch_versions = ch_versions.mix(CONSAMBIG.out.versions)
    
    BOULDER(CONSAMBIG.out.ambiguous_consensus)
    PRIMER3(BOULDER.out.boulder_output)
    ch_versions = ch_versions.mix(PRIMER3.out.versions)
    PARSE_PRIMER3(PRIMER3.out.primer3_output)

    //concatenate all primers into a single file
    all_primers_ch = PARSE_PRIMER3.out.primer_output.collect()
    CONCATENATE_PRIMERS(all_primers_ch)

    // check wheter to skip filtering part
    if (contig_file_ok && contig_list_ok) {
        // PRIMERSEARCH(pairedFiles)
        stool_contigs_ch
        .combine(CONCATENATE_PRIMERS.out.candidate_primers)
        .set {ps_pairedFiles}

        PRIMERSEARCH(ps_pairedFiles) 
        ch_versions = ch_versions.mix(PRIMERSEARCH.out.versions)

        PRIMERSEARCH.out.search_output
        .combine(stool_good_contig_list_ch)
        .set {paired_parse_ps_ch}
        PARSE_PRIMERSEARCH(paired_parse_ps_ch)
        CONCATENATE_GOOD_PRIMERS(PARSE_PRIMERSEARCH.out.primer_output.collect(), CONCATENATE_PRIMERS.out.candidate_primers)

        SNP_REDUNDANCY_FILTER(PRIMER3.out.primer3_output.collect(), CONCATENATE_GOOD_PRIMERS.out.candidate_primers)
    } else {
        log.warn "Neither --contig_file nor --good_contig_list exists. Skipping downstream pipeline."
    }

    if (params.run_compare_primers) {
        if (!params.legacy_file_path) {
            error "Primer search is enabled but no search file provided. Please provide --search_file"
        }
        //CONCATENATE_PRIMERS(PARSE_PRIMER3.out.primer_output.collect())
        CONCATENATE_PRIMERS(PARSE_PRIMERSEARCH.out.primer_output.collect())
        reference = channel.fromPath(params.legacy_file_path)
        COMPARE_PRIMERS(reference, CONCATENATE_PRIMERS.out.candidate_primers)
    }
    CUSTOM_DUMPSOFTWAREVERSIONS (
        ch_versions.unique().collectFile(name: 'collated_versions.yml')
    )
    // MODULE: MultiQC
    workflow_summary    = WorkflowT3pio.paramsSummaryMultiqc(workflow, summary_params)
    ch_workflow_summary = Channel.value(workflow_summary)

    methods_description    = WorkflowT3pio.methodsDescriptionText(workflow, ch_multiqc_custom_methods_description, params)
    ch_methods_description = Channel.value(methods_description)

    ch_multiqc_files = Channel.empty()
    ch_multiqc_files = ch_multiqc_files.mix(ch_workflow_summary.collectFile(name: 'workflow_summary_mqc.yaml'))
    ch_multiqc_files = ch_multiqc_files.mix(ch_methods_description.collectFile(name: 'methods_description_mqc.yaml'))
    ch_multiqc_files = ch_multiqc_files.mix(CUSTOM_DUMPSOFTWAREVERSIONS.out.mqc_yml.collect())
    
    MULTIQC (
        ch_multiqc_files.collect(),
        ch_multiqc_config.toList(),
        ch_multiqc_custom_config.toList(),
        ch_multiqc_logo.toList()
    )
    multiqc_report = MULTIQC.out.report.toList()
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMPLETION EMAIL AND SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow.onComplete {
    if (params.email || params.email_on_fail) {
        NfcoreTemplate.email(workflow, params, summary_params, projectDir, log, multiqc_report)
    }
    NfcoreTemplate.dump_parameters(workflow, params)
    NfcoreTemplate.summary(workflow, params, log)
    if (params.hook_url) {
        NfcoreTemplate.IM_notification(workflow, params, summary_params, projectDir, log)
    }
}

workflow.onError {
    if (workflow.errorReport.contains("Process requirement exceeds available memory")) {
        println("🛑 Default resources exceed availability 🛑 ")
        println("💡 See here on how to configure pipeline: https://nf-co.re/docs/usage/configuration#tuning-workflow-resources 💡")
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
