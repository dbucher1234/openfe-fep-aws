# 🔬 OpenFE FEP Test Run on AWS

Educational example on the T4 Lysozyme L99A (pdb 4W52) of how I ranked ligands using Free Energy Perturbation (FEP) calculations with [OpenFE](https://github.com/OpenFreeEnergy/openfe) running on AWS 8xGPU instances (using `g5.48xlarge`, NVIDIA A10G, 192 vCPUs).  

This repo provides scripts, environment setup, and workflows to prep, execute, and analyze FEP runs.

---

## 📁 What’s Inside

| Folder | Purpose |
|--------|---------|
| [prep/](prep)         | Ligand & system prep scripts (e.g., sdf to topology, mapping, JSONs) |
| [run/](run)           | AWS batch scripts, job configs, launch helpers |
| [analyze/](analyze)   | Parse OpenFE results, rank compounds, plot ΔG |
| [examples/](examples) | Toy dataset (small protein + ligands + dummy results) to test locally |
| [environment.yml](environment.yml) | Conda setup for GPU/OpenMM-based runs |

---

## 🚀 Quick Start

Clone the repo and create your environment:

```bash
git clone https://github.com/dbucher1234/openfe-fep-aws.git
cd openfe-fep-aws
conda env create -f environment.yml
conda activate openfe_fep
