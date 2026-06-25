# Cell type-wise SDAE Biomarker Discovery Summary

Dataset: /home/nazmul/Research/Celltype SDAE/data/GSE183276_scCv3_with_metadata.h5ad
Original shape: (109741, 37080)
Condition column: condition.l1
Cell type column: subclass.l1
Target classes: ['AKI', 'CKD', 'Ref']
Target cell types: ['PT', 'TAL', 'IMM', 'EC', 'IC', 'PC', 'CNT', 'DCT']
HVG per cell type: 3000
Model: Supervised Denoising Autoencoder
Hidden dims: (512, 128)
Latent dim: 32
Noise probability: 0.2
Balance rule: Ref count if possible; otherwise smallest condition count without replacement.

Important output files:
- /home/nazmul/Research/Celltype SDAE/results_celltype_sdae_3000hvg_biomarkers/tables/selected_celltype_condition_balance_summary.csv
- /home/nazmul/Research/Celltype SDAE/results_celltype_sdae_3000hvg_biomarkers/tables/ALL_celltype_balance_used.xlsx
- /home/nazmul/Research/Celltype SDAE/results_celltype_sdae_3000hvg_biomarkers/tables/ALL_celltype_sdae_test_metrics.xlsx
- /home/nazmul/Research/Celltype SDAE/results_celltype_sdae_3000hvg_biomarkers/tables/ALL_celltype_top_biomarkers_per_class.xlsx
- /home/nazmul/Research/Celltype SDAE/results_celltype_sdae_3000hvg_biomarkers/tables/FINAL_compact_celltype_biomarkers.xlsx
- Per-cell-type HVG, classification report, confusion matrix, latent PCA, model files are saved with prefix `celltype_<CELLTYPE>__...`
