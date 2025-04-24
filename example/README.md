# 🧪 Toy System: L99A Lysozyme + Alkylbenzenes

This folder contains a minimal working example of the full FEP workflow,
from ligand generation to analysis, using a known benchmark system:

- **Protein**: T4 Lysozyme L99A (cavity mutant)
- **Ligands**: Benzene → Toluene → Phenol → Aniline → Isopropylbenzene
- **Binding pocket**: Matches experimental binding data (see `../references/`)

## 📂 Folder Structure

| File | Description |
|------|-------------|
| `protein.pdb` | Raw structure from PDB (e.g., 4W52) |
| `cleaned_protein.pdb` | Output from `prep/clean_protein.py` |
| `lig_A.sdf … lig_E.sdf` | Ligand files can be created via `prep/generate_ligand.py` |
| `ligands.sdf` | All ligands merged into one file (and docked) |
| `charged_ligands.sdf` | All docked ligands with Espaloma partial charges (ML) |
| `transformations.json` | Mappings plus simulation settings for OpenFE |
| `ligand_network.graphml` | Ligand network definition used by OpenFE |
| `easy_rbfe_lig_A_solvent_lig_C_solvent_gpu3.json` | Output for one alchemical transformation |
| `ddg.out` | Example output with relative free energies between compounds |
