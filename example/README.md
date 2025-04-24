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
| `lig_A.sdf … lig_E.sdf` | Ligand files created via `prep/generate_ligand.py` |
| `ligands.sdf` | All ligands merged into one file (e.g., for visualization or docking) |
| `mapping.json` | Ligand network definition used by OpenFE |
| `dummy_results.json` | Pretend OpenFE output for demo purposes |
| `docked/` | Docked ligand poses (from Maestro or AutoDock Vina) |

## 🔍 Example Output

To run a dry example analysis:

```bash
python analyze/rank_free_energies.py examples/dummy_results.json

