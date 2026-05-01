# Handoff — Gladstein et al. Reproducible Notebook Pipeline

**Written:** 2026-03-25
**Purpose:** Full context for continuing this project on another machine (original Apple Silicon Mac). Read this entire document before touching any files.

---

## 1. Project Goal

Build a clean, fully reproducible, GitHub-ready Jupyter notebook pipeline that goes from raw Xenium spatial transcriptomics data to every paper figure for Gladstein et al. (NSCLC, mouse). The pipeline is split into 9 sequential notebooks in `notebooks/`. All notebooks must run end-to-end without manual intervention.

---

## 2. Why We're Moving to Another Machine

The original analysis (cell typing, clustering, all downstream figures) was run on Apple Silicon. When notebook 02 was re-run on PMACS (x86), ARM vs. x86 BLAS floating-point differences produced different PCA eigenvectors → different Leiden cluster numbering and count (23 clusters instead of 21; 18 subclusters instead of 14). The annotations in notebook 02 are keyed to cluster numbers, so the notebook must be run on **the same Apple Silicon machine that produced the original analysis** to guarantee identical cluster assignments. All other notebooks should also be run on Apple Silicon for consistency.

---

## 3. Project Structure (as it exists on this machine)

```
gladstein-et-al/
├── notebooks/
│   ├── 01_object_generation.ipynb      # raw → Gladstein object.h5ad
│   ├── 02_qc_cell_typing.ipynb         # QC, clustering, annotation → Gladstein Cell Typing.h5ad
│   ├── 03_neighborhood_assignment.ipynb # scimap CN → Gladstein Neighborhoods.h5ad
│   ├── 04_tumor_segmentation.ipynb     # tumor seg → Gladstein Neighborhoods plus segmented tumors.h5ad
│   ├── 05_spatial_visualization.ipynb  # Fig 2a/b/c, ED3a-f
│   ├── 06_hotspot_modules.ipynb        # Fig 2f/g, ED4b/c
│   ├── 07_go_enrichment.ipynb          # Fig 2e, ED4a
│   ├── 08_tcell_subclustering.ipynb    # Zheng2021 CD4/CD8 meta-cluster scoring (reviewer-driven)
│   └── 09_tam1_vs_tam2.ipynb           # TAM 1 vs TAM 2 DE + M1/M2 dotplot + scCODA per-tumor compositional
├── data/
│   ├── raw/
│   │   ├── output-XETG00171__0043340__29059__20240913__193721/  (KSH)
│   │   │   ├── cell_feature_matrix.h5
│   │   │   └── cells.csv
│   │   ├── output-XETG00171__0043340__30373__20240913__193721/  (Kras-Ctrl)
│   │   ├── output-XETG00171__0043352__29072__20240913__193721/  (KS)
│   │   ├── output-XETG00171__0043352__29964__20240913__193721/  (KH)
│   │   └── boundaries/
│   │       ├── output-XETG00171__0043340__29059__20240913__193721cell_boundaries.csv
│   │       ├── output-XETG00171__0043340__30373__20240913__193721cell_boundaries.csv
│   │       ├── output-XETG00171__0043352__29072__20240913__193721cell_boundaries.csv
│   │       └── output-XETG00171__0043352__29964__20240913__193721cell_boundaries.csv
│   └── processed/          # h5ad files land here (large, not committed to git)
├── envs/
│   ├── scanpy.yml          # notebooks 01, 02, 04, 05, 07
│   ├── scimap.yml          # notebook 03
│   └── hotspot2.yml        # notebook 06
├── figures/                # all paper figure outputs land here
├── docs/
│   ├── figure_manifest.md  # maps every panel → notebook → output file
│   └── HANDOFF.md          # this file
└── run_nb02_pmacs.bsub     # ignore — PMACS artifact, not needed on Apple Silicon
```

---

## 4. Conda Environments

Three task-based environments. Create each from its YAML before running notebooks.

```bash
conda env create -f envs/scanpy.yml    # creates env named "scanpy"
conda env create -f envs/scimap.yml    # creates env named "scimap"
conda env create -f envs/hotspot2.yml  # creates env named "hotspot2"
```

| Notebook | Environment |
|----------|-------------|
| 01, 02, 04, 05, 07, 08, 09 | `scanpy` (Python 3.9) |
| 03 | `scimap` (Python 3.10) |
| 06 | `hotspot2` (Python 3.11) |

If any env already exists from the original analysis under a different name (e.g., `scanpy_gladstein`), check whether it matches the pinned YAML. If unsure, create fresh from the YAML files — they have all versions pinned.

---

## 5. Notebooks: Status and What Each Does

### 01 — `01_object_generation.ipynb` ✅ Written and tested
- Reads 4 `cell_feature_matrix.h5` files via `sc.read_10x_h5`
- Attaches `cells.csv` spatial coordinates to `obsm['spatial']`
- Concatenates with `adatas[0].concatenate(*adatas[1:])` (deprecated API, kept intentionally)
- Run ID → Genotype mapping: 29059=Kras-H3K36M-Setd2KO, 30373=Kras-Ctrl, 29072=Kras-Setd2KO, 29964=Kras-H3K36M
- Output: `data/processed/Gladstein object.h5ad` (~3.1 GB, 1,343,281 cells)
- **Status:** Runs successfully. If `Gladstein object.h5ad` already exists from the original analysis, you can skip this notebook.

### 02 — `02_qc_cell_typing.ipynb` ⚠️ KEY NOTEBOOK — needs verification
- QC filter (min_genes=55), cell area normalization → log1p, HVG (min_disp=0.2, min_mean=0.0005)
- PCA(100), neighbors(n_neighbors=10, n_pcs=35), UMAP(random_state=1)
- Leiden(resolution=0.5, random_state=1) — **should give 21 clusters on Apple Silicon**
- Subclustering of cluster 1 (AT2/Malignant 2 mixed): PCA(50), neighbors(n_pcs=41), leiden(resolution=1.0, random_state=1) — **should give 14 subclusters**
- Annotation via `main_mapping` and `sub_mapping` (see Section 6 below)
- Key verification cells: dotplot of top 5 marker genes per leiden cluster, per-subcluster spatial grid
- Output: `data/processed/Gladstein Cell Typing.h5ad`

  **What to verify after running:**
  1. Leiden finds exactly 21 clusters (print statement in notebook will confirm)
  2. Subclustering finds exactly 14 subclusters
  3. Check the per-subcluster spatial plots to confirm sub 0 and sub 2 are diffuse (AT2) and all others are nodular (Malignant 2)
  4. Check the rank_genes_groups dotplot against the known marker genes in Section 7 below
  5. Zero unmapped cells (warning cell at end will fire if any)

### 03 — `03_neighborhood_assignment.ipynb` ✅ Written, not yet run on this machine
- scimap cellular neighborhood assignment (k=30, k=30)
- Input: `Gladstein Cell Typing.h5ad`
- Output: `data/processed/Gladstein Neighborhoods.h5ad`

### 04 — `04_tumor_segmentation.ipynb` ✅ Written, not yet run on this machine
- Tumor segmentation + T cell activation scoring (`sc.tl.score_genes`, random_state=1)
- Input: `Gladstein Neighborhoods.h5ad`
- Output: `data/processed/Gladstein Neighborhoods plus segmented tumors.h5ad` + Fig 2d SVGs

### 05 — `05_spatial_visualization.ipynb` ✅ Written, not yet run on this machine
- All UMAP and spatial segmentation plots
- Input: `Gladstein Neighborhoods plus segmented tumors.h5ad` + boundary CSVs
- Output: Fig 2a, 2b, 2c, ED3a–f (SVGs + CSVs in `figures/`)

### 06 — `06_hotspot_modules.ipynb` ✅ Written, not yet run on this machine
- Hotspot gene module analysis (DANB model, n_neighbors=300, top 500 genes, min_gene_threshold=25, fdr_threshold=0.05)
- Input: `Gladstein Neighborhoods plus segmented tumors.h5ad` + boundary CSVs
- Output: Fig 2f, 2g, ED4b, ED4c

### 07 — `07_go_enrichment.ipynb` ✅ Written, not yet run on this machine
- MSigDB Hallmark + canonical pathway enrichment via gseapy Enrichr
- Input: `Gladstein Neighborhoods plus segmented tumors.h5ad`
- Output: Fig 2e (`fig2e.svg`), ED4a (`ed4a_mod6_enrichment.svg`)

### 08 — `08_tcell_subclustering.ipynb` ✅ Written and executed
- T cells classified into CD4/CD8 lineages on raw `Cd4`/`Cd8a`/`Cd8b1` counts (>0); double+/double− excluded
- Lineages scored against the 24 CD4 and 16 CD8 pan-cancer T cell meta-cluster signatures from Zheng et al. 2021 (Science) using `sc.tl.score_genes`; human signatures converted to mouse via the MGI Human–Mouse orthology table
- Per-genotype subset composition + per-tumor subset composition
- Inputs: `data/processed/tcell_subset.h5ad`, `data/processed/zheng2021_table_s3.xlsx`, `data/processed/human_mouse_orthologs.csv`
- Outputs: `data/processed/cd4_tcell_annotated.h5ad`, `data/processed/cd8_tcell_annotated.h5ad`, `figures/08_cd{4,8}_subset_*.csv`, inline dotplots and violins

### 09 — `09_tam1_vs_tam2.ipynb` ✅ Written, not yet executed
- Wilcoxon DE between TAM 1 and TAM 2 (`sc.tl.rank_genes_groups`); top DEG tables exported
- Curated M1/M2 marker dotplot across the 5006-gene panel
- TAM 1 vs TAM 2 percentage per genotype (stacked bar)
- Pearson chi-square on the 4 × 2 contingency table + pairwise Fisher's exact (vs Kras-Ctrl) with Bonferroni
- Inputs: `data/processed/Gladstein Neighborhoods plus segmented tumors.h5ad`
- Outputs: `figures/09_tam_degs_*.csv`, `figures/09_tam_m1m2_dotplot.svg`, `figures/09_tam_proportions_by_genotype.{csv,svg}`, `figures/09_tam_pairwise_fisher.csv`

---

## 6. Cluster Annotations (notebook 02)

### main_mapping (21 clusters, Apple Silicon)

These are confirmed correct from the original analysis. The notebook already contains these; just verify cluster count matches.

```python
main_mapping = {
    '0':  'Malignant 1',
    '1':  'Subclustered',          # placeholder — overwritten by sub_mapping below
    '2':  'Vascular endothelial',
    '3':  'Lung fibroblast',
    '4':  'T cell',
    '5':  'Tumor-associated vasculature',
    '6':  'TAM 1',
    '7':  'Respiratory epithelium',
    '8':  'TAM 2',
    '9':  'AT1 cell',
    '10': 'Vascular endothelial',
    '11': 'Pericyte',
    '12': 'B cell',
    '13': 'CAF',
    '14': 'Plasma cell',
    '15': 'Airway smooth muscle',
    '16': 'Proliferating malignant',
    '17': 'Neutrophil',
    '18': 'Lymphatic endothelial',
    '19': 'Malignant 3',
    '20': 'Mesothelial',
}
```

### sub_mapping (14 subclusters of cluster 1)

Subclusters 0 and 2 are spatially diffuse → AT2. All others are spatially nodular → Malignant 2.

```python
sub_mapping = {
    0:  'AT2 cell',
    1:  'Malignant 2 (AT2-like)',
    2:  'AT2 cell',
    3:  'Malignant 2 (AT2-like)',
    4:  'Malignant 2 (AT2-like)',
    5:  'Malignant 2 (AT2-like)',
    6:  'Malignant 2 (AT2-like)',
    7:  'Malignant 2 (AT2-like)',
    8:  'Malignant 2 (AT2-like)',
    9:  'Malignant 2 (AT2-like)',
    10: 'Malignant 2 (AT2-like)',
    11: 'Malignant 2 (AT2-like)',
    12: 'Malignant 2 (AT2-like)',
    13: 'Malignant 2 (AT2-like)',
}
```

**If the cluster count comes out different from 21 or the subcluster count different from 14:** this means something about the environment or random state differs. Do not proceed — investigate before annotating.

---

## 7. Original Marker Genes Per Cluster (for annotation QC)

Use this to sanity-check the rank_genes_groups dotplot that notebook 02 produces. Top 5 per cluster:

| Cluster | Cell type | Top 5 markers |
|---------|-----------|---------------|
| 0 | Malignant 1 | Slc12a2, Slc2a3, Chil1, Epcam, Sdc1 |
| 1 | Subclustered | Lamp3, Fasn, Hc, Abca3, Elovl1 |
| 2 | Vascular endothelial | Epas1, Egfl7, Pltp, Calcrl, Cdh5 |
| 3 | Lung fibroblast | Pdgfra, Itga8, Lrp1, Prelp, Spon1 |
| 4 | T cell | Lat, Dock2, Ets1, Il7r, Ptprc |
| 5 | Tumor-associated vasculature | Egfl7, Pecam1, Mcam, Cdh5, Vwf |
| 6 | TAM 1 | Gm2a, Il10ra, Prkcd, Csf1r, Spi1 |
| 7 | Respiratory epithelium | Por, Cd24a, Ldhb, Cyb5a, Foxj1 |
| 8 | TAM 2 | Chil3, Atp6v0d2, Sirpa, Cd68, Itgb2 |
| 9 | AT1 cell | Ager, Hopx, Vegfa, Clic5, Rtkn2 |
| 10 | Vascular endothelial | Car4, Cdh5, Pecam1, Acvrl1, Kdr |
| 11 | Pericyte | Gucy1a1, Pdgfrb, Notch3, Postn, Lipg |
| 12 | B cell | Cd79b, Ighm, Cd79a, Syk, Igkc |
| 13 | CAF | Col1a1, Col1a2, Fn1, Fstl1, Fbn1 |
| 14 | Plasma cell | Igkc, Jchain, Igha, Mzb1, Cd79a |
| 15 | Airway smooth muscle | Tagln, Myh11, Actc1, Des, Flna |
| 16 | Proliferating malignant | Mki67, Hnrnpa1, Epcam, Hist2h2bb, H2afz |
| 17 | Neutrophil | Csf3r, Cxcr2, Selplg, Sorl1, Mcl1 |
| 18 | Lymphatic endothelial | Ccl21a, Ccl21b, Flt4, Mmrn1, Maf |
| 19 | Malignant 3 | Anxa2, Ano1, Dusp6, Epcam, Flnb |
| 20 | Mesothelial | C3, Upk3b, Gpc3, C4b, Aldh1a2 |

---

## 8. Key Parameters (for reference / reproducibility audit)

| Step | Parameter | Value |
|------|-----------|-------|
| QC | min_genes | 55 |
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

---

## 9. What to Do on the Other Machine — Step by Step

### Step 1: Copy the project

Copy the entire `gladstein-et-al/` folder from this machine. The `data/processed/` directory contains large h5ads (~3–31 GB) — if storage is tight, you can skip `data/processed/` and regenerate from raw, but it will take time. The `data/raw/` directory with the 4 Xenium run folders and `boundaries/` **must** be present.

### Step 2: Create conda environments

```bash
cd gladstein-et-al
conda env create -f envs/scanpy.yml
conda env create -f envs/scimap.yml
conda env create -f envs/hotspot2.yml
```

If the `scanpy` env already exists on that machine from the original analysis, check that it matches the pinned versions in `envs/scanpy.yml`. The versions matter for reproducibility.

### Step 3: Run notebooks in order

Run each notebook using `jupyter nbconvert`:

```bash
# Notebook 01 (skip if Gladstein object.h5ad already exists from original run)
conda run -n scanpy jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/01_object_generation.ipynb

# Notebook 02 — CRITICAL: verify cluster counts in output
conda run -n scanpy jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/02_qc_cell_typing.ipynb

# Notebook 03
conda run -n scimap jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/03_neighborhood_assignment.ipynb

# Notebook 04
conda run -n scanpy jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/04_tumor_segmentation.ipynb

# Notebook 05
conda run -n scanpy jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/05_spatial_visualization.ipynb

# Notebook 06
conda run -n hotspot2 jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/06_hotspot_modules.ipynb

# Notebook 07
conda run -n scanpy jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/07_go_enrichment.ipynb

# Notebook 08
conda run -n scanpy jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/08_tcell_subclustering.ipynb

# Notebook 09
conda run -n scanpy jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=36000 notebooks/09_tam1_vs_tam2.ipynb
```

Notebooks 02 and 06 are the slowest (hours each). You can run notebook 01 locally in Jupyter if you prefer to watch progress — it's faster.

### Step 4: After notebook 02, check these things

Open the executed notebook and confirm:
1. The print cell says **"Leiden found 21 clusters (originally 21 on Apple Silicon)"**
2. The subcluster print cell says **14 subclusters**
3. The rank_genes_groups dotplot top markers match the table in Section 7
4. The per-subcluster spatial grid shows subclusters 0 and 2 as spatially diffuse (AT2) and the rest as nodular tumors (Malignant 2). If a different pair of subclusters is diffuse, update `sub_mapping` accordingly (just change which keys get `'AT2 cell'`).
5. No unmapped cell warning fires at the end

### Step 5: After all notebooks complete

Check that `figures/` contains the expected output files. See `docs/figure_manifest.md` for the complete list of expected SVG/CSV outputs per panel.

### Step 6: Git setup and commit

Once all notebooks run cleanly and figures look correct:

```bash
cd gladstein-et-al
git init
git add notebooks/ envs/ docs/ figures/
# Do NOT add data/ (too large) — add a .gitignore first
```

Ask Claude to create a `.gitignore` and `README.md` at that point.

---

## 10. What Was Changed in the Notebooks This Session

The notebooks were substantially edited from their original versions. Key changes to notebook 02:

- **Bug fix:** `custom_palette` → `new_palette` in the UMAP cell (was a NameError)
- **Added:** `rank_genes_groups` dotplot cell (top 5 genes per cluster, standard_scale='var')
- **Added:** per-subcluster spatial grid (one panel per subcluster, ncols=6, for AT2 vs Malignant 2 visual verification)
- **Added:** cluster count sanity check print cell after Leiden
- **Updated:** `main_mapping` originally had TBD entries for clusters 21 and 22 (from PMACS x86 run) — these should be **removed** on Apple Silicon (21 clusters only, no TBD entries)
- **Updated:** `sub_mapping` originally had TBD entries for subclusters 14–17 (from PMACS x86 run) — these should be **removed** on Apple Silicon (14 subclusters only)

**Important:** Before running on Apple Silicon, verify that `main_mapping` only has keys '0' through '20' and `sub_mapping` only has keys 0 through 13. If the TBD entries are still there from the PMACS run edits, remove them. Ask Claude to check and fix the notebook before running.

Notebooks 03–07 were written from scratch this session and have not yet been executed anywhere. They are correct based on the original analysis code but should be reviewed by Claude cell-by-cell if any errors arise.

---

## 11. Source of Truth

The original analysis notebooks (unmodified, with outputs from the original Apple Silicon run) are on the external expansion drive:

```
/Volumes/Expansion/All possible info for Gladstein et al/
├── Gladstein QC and Cell Typing.ipynb        # original notebook 02
├── Gladstein object generation.ipynb         # original notebook 01
├── Gladstein Enrichr GO.ipynb                # original notebook 07
├── Gladstein Neighborhoods plus segmented tumors.h5ad  # final h5ad
└── [figure SVGs from original run]
```

If any notebook produces unexpected output, compare against the original notebooks on the expansion drive to identify the discrepancy.
