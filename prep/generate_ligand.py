#!/usr/bin/env python
"""
generate_ligand.py

This script generates 3D structures for a small set of drug-like ligands
using RDKit. Each molecule is defined by its SMILES string and written to
an individual .sdf file in the examples/toy-system/ directory.

Ligands: benzene, toluene, phenol, aniline, isopropylbenzene

I then docked the ligands to the prepared proteins using Maestro but AutoDock Vina is an open-source option
"""
import os
from rdkit import Chem
from rdkit.Chem import AllChem

# Define your five ligands with SMILES
lig_smiles = {
    "lig_A": "c1ccccc1",          # Benzene
    "lig_B": "Cc1ccccc1",         # Toluene
    "lig_C": "c1ccc(cc1)O",       # Phenol
    "lig_D": "c1ccccc1N",         # Aniline
    "lig_E": "CC(C)c1ccccc1"      # Isopropylbenzene
}

# Ensure output directory exists
output_dir = "examples/toy-system"
os.makedirs(output_dir, exist_ok=True)

# Generate each ligand
for name, smi in lig_smiles.items():
    mol = Chem.MolFromSmiles(smi)
    mol.SetProp("_Name", name)
    # Add explicit Hs for embedding
    mol = Chem.AddHs(mol)
    # Embed 3D coordinates
    AllChem.EmbedMolecule(mol, randomSeed=42)
    # (Optional) Remove Hs if you want a cleaner SDF
    mol = Chem.RemoveHs(mol)
    # Write out SDF
    out_path = os.path.join(output_dir, f"{name}.sdf")
    writer = Chem.SDWriter(out_path)
    writer.write(mol)
    writer.close()
    print(f"Generated {out_path}")

print("\nAll 5 ligands generated in examples/toy-system/")

