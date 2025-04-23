# 🔬 OpenFE FEP Toolkit on AWS

Run scalable Free Energy Perturbation (FEP) calculations using [OpenFE](https://github.com/OpenFreeEnergy/openfe) on powerful AWS GPU instances (e.g., `g5.48xlarge`).  
This repo provides scripts, environment setup, and workflows to prep, execute, and analyze FEP runs efficiently—plus a toy example that doesn't require GPU.

---

## 📁 What’s Inside

| Folder | Purpose |
|--------|---------|
| `prep/` | Ligand & system prep scripts (e.g., sdf to topology, mapping, JSONs) |
| `run/`  | AWS batch scripts, job configs, launch helpers |
| `analyze/` | Parse OpenFE results, rank compounds, plot ΔG |
| `examples/` | Toy dataset (small protein + ligands + dummy results) to test locally |
| `notebooks/` | Optional: Jupyter tutorials for analysis & visualization |
| `environment.yml` | Conda setup for GPU/OpenMM-based runs |

---

## 🚀 Quick Start

Clone the repo and create your environment:

```bash
git clone https://github.com/dbucher1234/openfe-fep-aws.git
cd openfe-fep-aws
conda env create -f environment.yml
conda activate openfe_fep
