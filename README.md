# Analysis of FKS hotspots DMS
Repo containing all scripts related to the analysis of deep mutational scanning data for the hotspots of FKS1 and FKS2 (and other related experiments)

## Installation instructions

To run notebooks from your platform using Jupyter Lab, follow these steps:

0. If you are on Windows or if you don't feel comfortable proceeding to the installation from a terminal, start with step 1a. Otherwise, start with step 1b. If you're on Windows and prefer a light standalone app, you can install [JupyterLab Desktop](https://github.com/jupyterlab/jupyterlab-desktop#download) and skip to step 2.

1. a) Install the [Anaconda](https://www.anaconda.com/download) package/environment management system (if you don't already have it). Registration is optional. Select the appropriate installer for your platform.

1. b) Install [Conda](https://docs.conda.io/).

On MacOS, run:
```
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
sh Miniconda3-latest-MacOSX-x86_64.sh
```
On Linux, run:
```
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
```

**IMPORTANT:** If in doubt, respond with "yes" to the following question during installation: "Do you wish the installer to initialize Miniconda3 by running conda init?". In this case Conda will modify your shell scripts (*~/.bashrc* or *~/.bash_profile*) to initialize Miniconda3 on startup. Ensure that any future modifications to your *$PATH* variable in your shell scripts occur **before** this code to initialize Miniconda3.

2. Clone this repository.

If you're using the Anaconda navigator or JupyterLab Desktop, open a prompt. If you don't have git installed, run `conda install git`, then `git clone https://github.com/Landrylab/Durand_et_al_2024.git`.

3. Use it to create a virtual environment with the necessary dependencies and activate it:
```
conda env create -n dms-env --file=DMS/requirements/Durand2024.yml
conda activate dms-env
```
At this stage, if you are using the Anaconda navigator, you can simply launch Jupyter Lab and skip steps 4-6.

4. Export kernel.
`python -m ipykernel install --user --name=dms-env`

At this stage, if you are using Jupyter Lab Desktop, you can close the terminal and skip step 5.

5. Run Jupyter Lab from the DMS folder
`jupyter lab`

6. When opening any notebook, select the kernel *dms-env*

## oPools
oPools were generated using [this notebook](generate_oPools.ipynb).

## Preliminary growth assays
Deletion mutants for the hotspot 1 of FKS1 and FKS2 + the parental strain were cultured in increasing drug concentrations to generate dose-reponse curves, using [this notebook](growth_curves/dose_response.ipynb).

Pools were cultured in concentrations inhibiting 0, 10, 25 and 50% of WT growth. The assay was analyzed using [this notebook](growth_curves/cultures_pools.ipynb)

## DMS cultures
[This notebook](dms_cultures.ipynb) was used to visualize the number of mitotic generations (calculated from cell concentrations measured by flow cytometry) and look at the correlation between cytometry measurements and optical density measurements.

## Variant counts
Variant counts were obtained using [DiMSum v1.3](https://github.com/lehner-lab/DiMSum/tree/master).

### Generate experimental design files
DiMSum requires an experimental design file for every "experiment". Here, we considered an experiment to correspond to a single set of conditions. The conditions are:
- Same genetic background = BY4741 (wild-type allele of paralog) or R1158 (doxycycline repression of paralog)
- Same locus on which the DMS is performed = Hotspot 1 or 2 of either FKS1 or FKS2
- Same type of pool (here, only NNK variants mixed with ortholog variants)
- Same compound (control with or without doxycycline for R1158, or either of 3 echinocandins: caspofungin, anidulafungin or micafungin, supplemented with doxycycline for R1158)

DiMSum normally does not allow for input replicates. To compensate for this, we duplicated every set of output replicates (up to 3) for each input replicate (up to 3). Because we ultimately use only the variant read counts in each "sample" (input 1 or input 2 (...) or output 3), the only consequence is that DiMSum outputs duplicate columns. This was the only way I could see to be able to run the entire DiMSum pipeline and still generate diagnostic plots at every step.

A [python script](dimsum_scripts/novaseq_run2_single_selection_loop_expdesign.py) was used to generate all experimental design files (n=60). Together, they account for all sequencing samples (n=223) and all tested sets of conditions.

Additionally, all experimental design files contain the constant regions to trim (see steps below), the number of mitotic generations and the selection time over two successive rounds of selection (each one stopped when the culture reached an optical density at 595 nm of approximately 1).

### Run the DiMSum pipeline
Since the samples were already demultiplexed, we skipped step 0 of the DiMSum pipeline. The pipeline was run for all samples using [this notebook](dimsum_scripts/dimsum-latest.py). For each of the 60 experiments, the following steps were performed:
1. FastQC on raw reads
2. Trim constant regions using [Cutadapt v2.4](https://cutadapt.readthedocs.io/en/stable/) with the following parameters:
    1. --cutadapt5First = the 30 bp immediately upstream of the modified locus (before F639)
    2. --cutadapt5Second = the 30 bp immediately downstream of the modified locus (after P647)
    3. --cutadaptMinLength = 75% of the length of the locus nucleotide sequence
3. Align paired-end reads (aggregation) using [VSEARCH v2.26.1](https://github.com/torognes/vsearch) and tally unique sequences using [Starcode v1.4](https://github.com/gui11aume/starcode) with default parameters
4. Process variants with the following parameters:
    1. --indels all (kept for diagnostic purpose, filtered out in downstream analyses)
    2. --maxSubstitutions = 9 (to include hotspots from orthologs)
    3. --mixedSubstitutions T (to include hotspots from orthologs)
    4. --fitnessMinInputCountAll 10 (this parameter is only applied for fitness calculations, which are replaced in downstream analyses by a different way of estimating fitness)
5. Calculate fitness and error estimates for diagnostic purposes

Once the job was completed, we fetched all html reports, read count files and fitness data files using [this short homemade script](dimsum_scripts/get_files.sh) and gathered all info related to read filtering using [this script](diagnostics_scripts/get_read_statistics.py).

## Calculate selection coefficients
First, a dataframe containing all expected variants (based on the design of oPools) was generated for every locus using [this notebook](generate_dms_mutants_V2.ipynb).

For every experiment, the "variant_data_merge.tsv" file output by DiMSum containing read counts for every sequenced variant was processed using [this template notebook](template.ipynb).

The notebook produces a lot of diagnostic plots, figures and tables, but ultimately generates a dataframe containing the selection coefficients. To process all 60 experiments, we used [this driver notebook](runmaster.ipynb) and ran it with [papermill v2.5](https://github.com/nteract/papermill).

**IMPORTANT** At this stage, all dataframes are concatenated to generate a single master dataframe with selection coefficients of all conditions.

## Analysis of selection coefficients
The master dataframe generated in the previous step was used to [classify variants, plot distributions and look at cross-resistance](classification_NNK.ipynb)

## Select mutants to reconstruct in the parental strain
Single mutants to be renconstructed are selected across the range of fitness effects + based on previous reports in the literature using [this notebook](select_mutants_for_reconstruction.ipynb).

## Validations
Validation assays were performed in the lab by recreating 29 single mutants in the hotspot 1 of FKS1. Growth curves were anlyzed and transformed using [this notebook](growth_curves/20240129_validations_test3.ipynb). In this notebook, data were also correlated with DMS scores and a linear regression model helped infer the scores of mutants missing from the NNK dataset.

## Generate heatmaps and mappable data
DMS data and inferred DMS scores (see above, section on validations) were pooled to generate heatmaps. We used [this template notebook](heatmaps_template.ipynb) and [this driver notebook](heatmaps_driver.ipynb).

Ultimately, the same data were used to [generate defattr files](chimera.ipynb) for ChimeraX to map the proportion of resistant mutants on Fks1 and Fks2 structures.

## Diagnostics analyses
Analyses of data obtained from preliminary sequencing runs (MiSeq and iSeq):
- [Diversity in NNK libraries](diagnostics_scripts/MiSeqRun_NNK.ipynb)
- [Diversity in libraries of orthologs](diagnostics_scripts/MiSeqRun_orthos.ipynb)

Assessment of read filtering using [this notebook](diagnostics_scripts/get_read_statistics.ipynb).

General diagnostics using [this notebook](diagnostics_scripts/diagnostics_masterdf.ipynb):
- Comparison of NNK variants / ortholog variants ratios (expected vs observed)

Assessment of replicability using [this notebook](diagnostics_scripts/replicability.ipynb).

## Machine-learning assisted prediction of resistance
This section was largely developed by M. Giguere. Some scripts and dataframes were imported from his repo, then edited by me (R. Durand).

The approach is to use a random forest classifier, use a combination of hotspot positions + aminoacid properties as training set, then predict resistance to a specific drug. 2 assays can be performed from [the same notebook](ML/Predict_orthologs.ipynb). In both, the model is trained on all single mutants from Fks1-HS1 (replicate observations are related to synonymous variants).

**Assay 1**. Predict resistance for all WT orthologs (the ones spiked in the NNK libraries, for which we have DMS data). These hotspot sequences range in Hamming distance from 2 to 7 residues away from *S. cerevisiae* WT.

**Assay 2**. Predict resistance for all mutants reported in the literature (Fks1-HS1 or Fks2-HS1). These hotspot sequences are all single mutants *in their native genomic context* (but again will have a Hamming distance of up to 7 residues away from *S. cerevisiae* WT).

For the latter, A. Pageau generated [a list](mardy2/Fks_mutated_hotspot_seq_210624.csv) of the entire hotspot sequences corresponding to these mutants, so that the species-dependent genetic background of the mutation (at least at the hotspot level) is included.

The notebook will also plot the SHAP values for the 5 features contributing the most to the model.

For all this, MG wrote 2 additional notebooks to [generate the confusion matrix](ML/Make_cmatrix.ipynb) and the [ROC curve](ML/Make_ROCcurve.ipynb).
