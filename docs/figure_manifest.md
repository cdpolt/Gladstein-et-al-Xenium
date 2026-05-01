# Figure Manifest — Gladstein et al.

Maps every paper figure panel to the notebook and output file that produces it.
All output paths are relative to the project root.

---

## Figure 2

| Panel | Description | Notebook | Output file(s) | Notes |
|-------|-------------|----------|----------------|-------|
| 2a | Per-genotype cell type UMAPs (×4) | `05_spatial_visualization` | `figures/umapKras-Ctrl.svg` `figures/umapKras-H3K36M.svg` `figures/umapKras-H3K36M-Setd2KO.svg` `figures/umapKras-Setd2KO.svg` | Loop over genotypes |
| 2a (spatial) | Cell type segmentation crops — one ROI per genotype (×4) | `05_spatial_visualization` | `figures/seg_Kras-Ctrl_CT.svg` etc. | `seg_plot()` function; coordinates TBD |
| 2b | Cell type abundance per genotype (bar/CSV) | `05_spatial_visualization` | `figures/Kras-Ctrl_cell_type_annotations.csv` `figures/Kras-H3K36M_cell_type_annotations.csv` `figures/Kras-H3K36M-Setd2KO_cell_type_annotations.csv` `figures/Kras-Setd2KO_cell_type_annotations.csv` | Zero-filled tumor abundance tables |
| 2c | Cellular neighborhood abundance per genotype (bar/CSV) | `05_spatial_visualization` | `figures/Kras-Ctrl_cell_neighborhood_annotations.csv` `figures/Kras-H3K36M_cell_neighborhood_annotations.csv` `figures/Kras-H3K36M-Setd2KO_cell_neighborhood_annotations.csv` `figures/Kras-Setd2KO_cell_neighborhood_annotations.csv` | Zero-filled tumor abundance tables |
| 2d | T cell activation dotplot — plasma B-T co-enriched vs malignant neighborhoods | `04_tumor_segmentation` | `figures/tcell_pbtconeigh.svg` `figures/tcell_maligneigh.svg` | `sc.tl.score_genes` on all cells, `random_state=1` |
| 2e | Immune Hallmark enrichment scatter by genotype | `07_go_enrichment` | `figures/fig2e.svg` | 8 selected Hallmark terms; KH/KS/KSH vs Kras-Ctrl |
| 2f | Hotspot module expression dotplot by genotype (malignant cells) | `06_hotspot_modules` | `figures/Genotype module dotplot.svg` | All modules × genotypes, filtered to malignant neighborhoods |
| 2g | Module 6 spatial segplots — H3K36M genotypes (×2) | `06_hotspot_modules` | `figures/Kras-H3K36M_mod6.svg` `figures/Kras-H3K36M-Setd2KO_mod6.svg` | `vmin=0, vmax=9`; specific ROI coordinates |

---

## Extended Data Figure 3 (ED3)

| Panel | Description | Notebook | Output file(s) | Notes |
|-------|-------------|----------|----------------|-------|
| ED3a | All-genotype combined cell type UMAP | `05_spatial_visualization` | `figures/umapall genotypes.svg` | Single UMAP with all 4 genotypes |
| ED3b | Full-lobe cell type segplots (×4 genotypes) | `05_spatial_visualization` | `figures/Large Kras-Ctrl spatial.svg` etc. | `large_seg_plot()` — rasterized |
| ED3c | Marker gene dotplot per cell type (`rank_genes_groups`) | `05_spatial_visualization` | `figures/rgg_dotplot.svg` | Top DE genes per cell type |
| ED3d | Cell type × cellular neighborhood enrichment bubble | `05_spatial_visualization` | `figures/ct_cn_enrichment.svg` | |
| ED3e | Full-lobe cellular neighborhood segplots (×4 genotypes) | `05_spatial_visualization` | `figures/Large Kras-Ctrl neighborhoods spatial.svg` etc. | `large_seg_plot()` — rasterized |
| ED3f | Cellular neighborhood segmentation crops (×4 genotypes) | `05_spatial_visualization` | `figures/seg_Kras-Ctrl_CN.svg` etc. | Same ROI coords as Fig 2a spatial |

---

## Extended Data Figure 4 (ED4)

| Panel | Description | Notebook | Output file(s) | Notes |
|-------|-------------|----------|----------------|-------|
| ED4a | Module 6 canonical pathway enrichment barplot | `07_go_enrichment` | `figures/ed4a_mod6_enrichment.svg` | gseapy `barplot()`, top 20 m2.cp terms |
| ED4b | Module 6 score vs T cell activation scatter (per-genotype regression) | `06_hotspot_modules` | `figures/mod6_vs_tcell_activation.svg` `figures/mod 6 scores.csv` | Source data CSV + scatter with regression lines |
| ED4c | Module 6 spatial segplots — T cell high/low tumors (×4: tumors 36+50, vmax 5+9) | `06_hotspot_modules` | `figures/Kras-Ctrl Mod 6 T cell high (36).svg` `figures/Kras-Ctrl Mod 6 T cell high (36) vmax 9.svg` `figures/Kras-Ctrl Mod 6 T cell low (50).svg` `figures/Kras-Ctrl Mod 6 T cell low (50) vmax 9.svg` | Tumors 36 (T cell high) and 50 (T cell low) |

---

## Reviewer-driven sub-analyses (notebooks 08–09)

| Description | Notebook | Output file(s) | Notes |
|-------------|----------|----------------|-------|
| CD4 / CD8 T cell subset composition by genotype | `08_tcell_subclustering` | `figures/08_cd4_subset_pct_by_genotype.csv` `figures/08_cd8_subset_pct_by_genotype.csv` | Zheng 2021 meta-cluster scores; subset assignment by argmax |
| Per-tumor T cell subset quantification | `08_tcell_subclustering` | `figures/08_cd4_subset_per_tumor.csv` `figures/08_cd8_subset_per_tumor.csv` | One row per (tumor × subset) |
| TAM 1 vs TAM 2 differential expression | `09_tam1_vs_tam2` | `figures/09_tam_degs_TAM1_vs_other.csv` `figures/09_tam_degs_TAM2_vs_other.csv` | Wilcoxon |
| TAM M1/M2 canonical marker dotplot | `09_tam1_vs_tam2` | `figures/09_tam_m1m2_dotplot.svg` | Curated M1 + M2 markers present in the 5006-gene panel |
| TAM 1 vs TAM 2 percentage by genotype | `09_tam1_vs_tam2` | `figures/09_tam_proportions_by_genotype.{csv,svg}` | Stacked bar of all TAM cells per genotype |
| Compositional test: chi-square + pairwise Fisher's | `09_tam1_vs_tam2` | `figures/09_tam_pairwise_fisher.csv` | Omnibus 4×2 chi-square; pairwise vs Kras-Ctrl with Bonferroni |

---

## Intermediate / Verification Outputs (not paper figures)

| Description | Notebook | Output |
|-------------|----------|--------|
| Leiden cluster dotplot (marker gene verification) | `02_qc_cell_typing` | Inline notebook output |
| Per-subcluster spatial grid (AT2 vs Malignant 2 verification) | `02_qc_cell_typing` | Inline notebook output |
| Cell type UMAP (annotation QC) | `02_qc_cell_typing` | Inline notebook output |
| HVG plot | `02_qc_cell_typing` | Inline notebook output |
| PCA variance ratio | `02_qc_cell_typing` | Inline notebook output |
| All-genotype spatial dot embedding | `05_spatial_visualization` | `figures/all_genotypes_spatial.svg` |

---

## Notebook → Output File Summary

| Notebook | Environment | Key inputs | Key outputs |
|----------|-------------|------------|-------------|
| `01_object_generation` | scanpy | `data/raw/output-XETG*/` | `data/processed/Gladstein object.h5ad` |
| `02_qc_cell_typing` | scanpy | `Gladstein object.h5ad` | `data/processed/Gladstein Cell Typing.h5ad` |
| `03_neighborhood_assignment` | scimap | `Gladstein Cell Typing.h5ad` | `data/processed/Gladstein Neighborhoods.h5ad` |
| `04_tumor_segmentation` | scanpy | `Gladstein Neighborhoods.h5ad` | `data/processed/Gladstein Neighborhoods plus segmented tumors.h5ad` + Fig 2d SVGs |
| `05_spatial_visualization` | scanpy | `Gladstein Neighborhoods plus segmented tumors.h5ad` + boundary CSVs | Fig 2a, 2b, 2c, ED3a–f SVGs + CSVs |
| `06_hotspot_modules` | hotspot2 | `Gladstein Neighborhoods plus segmented tumors.h5ad` + boundary CSVs | Fig 2f, 2g, ED4b, ED4c SVGs + CSV |
| `07_go_enrichment` | scanpy | `Gladstein Neighborhoods plus segmented tumors.h5ad` | Fig 2e, ED4a SVGs |
| `08_tcell_subclustering` | scanpy | `tcell_subset.h5ad`, `zheng2021_table_s3.xlsx`, `human_mouse_orthologs.csv` | T cell subset CSVs (`08_cd{4,8}_subset_*.csv`), inline dotplots/violins |
| `09_tam1_vs_tam2` | scanpy | `Gladstein Neighborhoods plus segmented tumors.h5ad` | TAM DE tables, M1/M2 dotplot, TAM proportions, chi-square + pairwise Fisher's |

---

## Key Parameters (for reproducibility)

| Step | Parameter | Value |
|------|-----------|-------|
| QC filter | min_genes | 55 |
| Normalization | method | cell area normalization → log1p |
| HVG | min_disp | 0.2 |
| HVG | min_mean | 0.0005 |
| PCA | n_comps | 100 |
| Neighbors | n_neighbors | 10 |
| Neighbors | n_pcs | 35 |
| UMAP | random_state | 1 |
| Leiden (main) | resolution | 0.5 |
| Leiden (main) | random_state | 1 |
| Leiden (subcluster) | resolution | 1.0 (default) |
| Leiden (subcluster) | random_state | 1 |
| Subcluster PCA | n_comps | 50 |
| Subcluster neighbors | n_pcs | 41 |
| Spatial KNN (scimap) | k | 30 |
| Neighborhood clusters | k | 30 |
| Hotspot model | — | DANB |
| Hotspot neighbors | n_neighbors | 300 |
| Hotspot top genes | — | 500 |
| Hotspot modules | min_gene_threshold | 25 |
| Hotspot modules | fdr_threshold | 0.05 |
| score_genes random_state | — | 1 |
| Global random seed | — | 42 (where applicable) |
