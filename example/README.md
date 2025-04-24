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


<p align="center">
  <img src="../images/fep_overview.png" width="600">
</p>

In my FEP calculations, I get the following results for the relative free energy (no error bars due to the lack of repeats, and limited accuracy due to 2ns per leg):

ligand_i	ligand_j	DDG(i->j) (kcal/mol)	uncertainty (kcal/mol)
lig_A	lig_C	-0.1	0.0
lig_A	lig_D	0.1	0.0
lig_A	lig_E	-0.1	0.0
lig_B	lig_D	0.3	0.0

It means for instance that lig_A is getting more stable by 0.1 when transformed to lig_C. 
Knowing lig_A DG value is -5.16 kcal/mol, we get resulting absolute binding free energies: 

Ligand | Predicted ΔG (kcal mol-¹)
lig_A (Benzene) | −5.16  (given)
lig_B (Toluene) | −5.36
lig_C (Phenol) | −5.26
lig_D (Aniline) | −5.06
lig_E (Isopropylbenzene) | −5.26

Interpretation:
• Toluene (lig_B) is predicted to bind ~0.2 kcal mol-¹ more strongly than benzene.
• Phenol and isopropylbenzene tie at −5.26 kcal mol-¹.
• Aniline is the weakest of the set by this calculation.

In general, most of them falls within 1 kcal, thus are not that interesting. One would be looking for a much better compound and then try to confirm the predictions with more sampling time and repeats. 
