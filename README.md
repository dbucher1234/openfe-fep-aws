# 🔬 OpenFE FEP workflow on AWS

This repo shows a minimal **Free-Energy Perturbation (FEP)** campaign with
[OpenFE](https://github.com/OpenFreeEnergy/openfe) on AWS.  

Provided an educational example for 5 ligands ranked in the T4 Lysozyme L99A (pdb 4W52), which was completed within a few hours on a 8xGPU instance (`g5.48xlarge`).

This repo provides scripts, environment setup, and workflows to prep, execute, and analyze FEP runs.

---

## 📁 What’s Inside

| Folder | Purpose |
|--------|---------|
| [prep/](prep)         | Ligand & system prep scripts (e.g., parmetrize ligands with ML, clean pdb) |
| [run/](run)           | AWS batch scripts, job configs, launch helpers |
| [example/](example) | Toy dataset (small protein + ligands + dummy results) to test |

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

# 2) prep protein (fixpdb if needed)
conda env create -f openfe_env.yml
conda activate openfe
python clean_protein.py

# 3) login to AWS
aws ec2 start-instances --instance-ids *AWS-ID-HERE*
# login by ssh, send by scp: ligands.sdf, protein.pdb + /run

# 4) On AWS
# install OpenFE and its environement:
openfe plan-rbfe-network -M ligands.sdf -p cleaned_protein.pdb -o network_setup/transformations
# will run a default network. For 5 ligands, it creates 8 transformations (4 in solvent + 4 in complex), which is trivial to parallelize on 8 GPUs. 
#  python update_json_params.py can be used for testing & debugging. It changes the repeats from n=3 to n=1, and the lenght of each simulation from 5ns to 2ns. Solvent calculations take about 30min on 1 GPU, and complex calculations about 6h.
nohup ./run.sh > run.log 2>&1 &  # running in the background to remain stable if the shell closes.
