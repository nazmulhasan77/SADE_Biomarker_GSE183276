# SDAE Biomarker Discovery Summary

Dataset: /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/data/GSE183276_scCv3_with_metadata.h5ad
Original filtered shape: (109741, 37080)
Balanced model shape: (12000, 37080)
HVG data shape: (12000, 3000)
Condition column: condition.l1
Classes: ['AKI', 'CKD', 'Normal']
N_TOP_HVG: 3000
Model: Supervised Denoising Autoencoder
Hidden dims: (512, 128)
Latent dim: 32
Noise probability: 0.2
Test accuracy: 0.8988
Test macro F1: 0.8982
Test weighted F1: 0.8982

Important output files:
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/tables/selected_3000_hvg_by_variance.csv
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/tables/training_history.csv
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/tables/test_metrics.csv
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/tables/confusion_matrix.csv
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/tables/gene_importance_all_classes.csv
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/tables/top_biomarker_genes_per_class.xlsx
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/tables/top_biomarker_expression_summary.xlsx
- /home/nazmul/Research/SDAE_GSE183276_3000HVG_supervised_biomarker_ready/results_sdae_3000_variance_biomarkers/models/supervised_sdae_best_model.pt
