# Gladstein et al. — Xenium spatial transcriptomics analysis

Reproducible Jupyter notebook pipeline for the Xenium spatial transcriptomics analysis in Gladstein et al. (mouse NSCLC). Four genotypes profiled with a 5006-gene mouse Xenium panel: Kras-Ctrl, Kras-H3K36M, Kras-Setd2KO, Kras-H3K36M-Setd2KO.

## Pipeline

| Notebook | Environment |
|----------|-------------|
| `01_object_generation` | `scanpy` |
| `02_qc_cell_typing` | `scanpy` |
| `03_neighborhood_assignment` | `scimap` |
| `04_tumor_segmentation` | `scanpy` |
| `05_spatial_visualization` | `scanpy` |
| `06_hotspot_modules` | `hotspot2` |
| `07_go_enrichment` | `scanpy` |
| `08_tcell_subclustering` | `scanpy` |
| `09_tam1_vs_tam2` | `scanpy` |

Run notebooks 01–09 in order. Notebook 02 is sensitive to the BLAS implementation and reproduces the published 21-cluster Leiden solution on Apple Silicon; running on x86 will produce a different cluster count.

## Environments

```bash
conda env create -f envs/scanpy.yml
conda env create -f envs/scimap.yml
conda env create -f envs/hotspot2.yml
```

## Data

Raw Xenium data and processed h5ad objects are not included in the repository (file sizes preclude version control). Raw data are deposited at [GEO accession to be added]. Run notebook 01 against the raw data to regenerate the processed objects in `data/processed/`.

## Repository layout

```
notebooks/   # numbered analysis notebooks (01–09)
envs/        # conda environment specs
figures/     # all paper figure outputs (SVG + source-data CSVs)
docs/        # HANDOFF.md, figure_manifest.md
```

See `docs/figure_manifest.md` for the mapping from paper panels to notebook outputs.
