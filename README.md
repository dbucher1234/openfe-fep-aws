# 🔬 OpenFE FEP workflow on AWS

This repo illustrates a **minimal Free-Energy Perturbation (FEP)** campaign with
[OpenFE](https://github.com/OpenFreeEnergy/openfe) on the cloud (AWS).  

Provided an educational example ranking five ligands bound to T4 lysozyme L99A (PDB ID: 4W52), completed within a few hours on an 8-GPU AWS instance (g5.48xlarge).

This repo provides scripts, environment setup, and workflows to prep, execute, and analyze FEP runs.

---

## 📁 What’s Inside

| Folder | Purpose |
|--------|---------|
| [prep/](prep)         | Ligand & system prep scripts (e.g., parmetrize ligands with ML, clean pdb) |
| [run/](run)           | AWS batch scripts, job configs, launch helpers |
| [example/](example) | Toy dataset (small protein + ligands + dummy results) to test |

---

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

Below are the ligands, with their experimental binding affinities: 
<p align="center">
  <img src="../images/fep_overview.png" width="600">

In my FEP calculations, I get the following results for the relative free energy (no error bars due to the lack of repeats, and limited accuracy due to 2ns per leg). Knowing lig_A DG value is -5.16 kcal/mol, we can approximate absolute binding free energies: 

<p align="center">
  <img src="../images/fep_results.png" width="600">
</p>
The predicted affinity for the compounds is the following:

<p align="center">
 <img src="../images/fep_ranking.png" width="600">
</p>

**Interpretation:**

Toluene (lig_B) is predicted to bind ~0.2 kcal mol⁻¹ more tightly than benzene (lig_A). Aniline (lig_D) is the weakest of the set by this calculation, in agreement with experiments. 

That said, none of the compounds stands out — which also aligns with experimental data. In a real drug discovery setting, you’d typically look for compounds predicted to be >1 kcal mol⁻¹ better before prioritizing synthesis. Promising hits could be confirmed before synthesis with additional sampling and repeat FEP runs.

---

## 📚 References

- Chang, C.-E.; Gilson, M. K. *J. Am. Chem. Soc.* **2007**, **129**, 943–953.  
- Boyce, S. E.; Dalby, A.; **et al.** *J. Mol. Biol.* **2009**, **394**, 747–763.  
- Morton, S. J.; Matthews, B. W. *Biochemistry* **2009**, **48**, 9466–9478. (PDB 3GUN)  
- Merski, M.; Fischer, M.; **et al.** *Proc. Natl. Acad. Sci. U.S.A.* **2015**, **112**, 5021–5026.  
- Raza, A.; Awan, H. M.; **et al.** *J. Chem. Inf. Model.* **2021**, **61**, 4599–4615.  
- **Espaloma charges:** Qiu, Y.; Smith, D. G. A.; Boothroyd, S.; Chen, J.; Chodera, J. D.  
  “Espaloma: Graph Neural Networks for Small-Molecule Force-Field Parameters.”  
  *J. Chem. Theory Comput.* **2022**, **18**, 5634–5646.  
- Young, T. J.; Unke, O. T.; Hargreaves, M.; Abraham, R. L.; **et al.**  
  “OpenFE: An Open-Source Framework for Alchemical Free-Energy Calculations.”  
  *J. Open Source Softw.* **2023**, **8**, 5170. <https://doi.org/10.21105/joss.05170>

---

## 🚀 Quick Start

Clone the repo and create your environment:

```bash
# 0) clone 
git clone https://github.com/dbucher1234/openfe-fep-aws.git
cd openfe-fep-aws

# 1) prep ligands (optional: use ML partial charges instead of AM1/BCC to save time)
conda env create -f espaloma_env.yml
conda activate esp
cd prep
python esp_neutral.py ligands.sdf 

# 2) prep protein (pdbfix if needed)
conda env create -f openfe_env.yml
conda activate openfe
python clean_protein.py

# 3) login to AWS
aws ec2 start-instances --instance-ids *AWS-ID-HERE*
# login by ssh, send by scp: ligands.sdf, protein.pdb + /run

# 4) On AWS
# install OpenFE and its environement, and then:
openfe plan-rbfe-network -M ligands.sdf -p cleaned_protein.pdb -o network_setup/transformations
# will create a default network.
For 5 ligands, it creates 8 transformations (4 in solvent + 4 in complex), which is trivial to parallelize on 8 GPUs. 
# python update_json_params.py can be used for testing & debugging.
# It changes the repeats from n=3 to n=1, and the lenght of each simulation from 5ns to 2ns.

# Solvent calculations take about 30min on 1 GPU, and complex calculations about 6h. To run:
nohup ./run.sh > run.log 2>&1 &  # running in the background to remain stable if the shell closes.
python check_completion.py  # provide info about running and completed calculations.
# resubmit.py can be used to resubmit only jobs that did not complete.

# 5) Gathering results
# if running a full calculations (3 repeats per leg): openfe gather --report dG
# if running a partial calculation (1 repeat):
openfe gather --allow-partial --report ddg . > ddg.out &
# write a script to rank compound from their relative free energy, or just ask ChatGPT to do it. 
