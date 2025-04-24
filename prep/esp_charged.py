#!/usr/bin/env python
"""
esp_charged.py

Utility script to parmetrize with Espaloma a ligand that has an amine and therefore should have a total charge of 1

"""

import warnings
warnings.filterwarnings("ignore", message=".*Recommend creating graphs by `dgl.graph(data)`.*")

from openff.toolkit.topology import Molecule
from openff.units import unit
import numpy as np
from rdkit import Chem
from rdkit.Chem import SDWriter, AllChem
from espaloma_charge.openff_wrapper import EspalomaChargeToolkitWrapper

# Load all molecules from SDF file
off_mols = Molecule.from_file('ligands.sdf', allow_undefined_stereo=True)
if not isinstance(off_mols, list):
    off_mols = [off_mols]

print(f"Processing {len(off_mols)} molecules...")

# Create the toolkit registry
toolkit_registry = EspalomaChargeToolkitWrapper()

# Open SDWriter for output
with SDWriter('charged_ligands.sdf') as writer:
    for i, off_mol in enumerate(off_mols):
        print(f"\nProcessing molecule {i+1}/{len(off_mols)}")
        
        # Convert to RDKit for initial analysis
        rdkit_mol = off_mol.to_rdkit()
        Chem.SanitizeMol(rdkit_mol)
        
        # Print molecule details
        print(f"Molecule SMILES: {off_mol.to_smiles()}")
        print("Initial atom details:")
        for atom_idx, atom in enumerate(off_mol.atoms):
            rdkit_atom = rdkit_mol.GetAtomWithIdx(atom_idx)
            print(f"Atom {atom_idx}: {atom.symbol} "
                  f"(formal charge: {atom.formal_charge}, "
                  f"H count: {rdkit_atom.GetTotalNumHs()})")
        
        # Set formal charge on protonated amine nitrogen
        found_amine = False
        for atom_idx, atom in enumerate(off_mol.atoms):
            rdkit_atom = rdkit_mol.GetAtomWithIdx(atom_idx)
            if atom.atomic_number == 7:  # Nitrogen
                if rdkit_atom.GetTotalNumHs() == 3:  # protonated amine
                    atom.formal_charge = 1 * unit.elementary_charge
                    found_amine = True
                    print(f"Set +1 formal charge on amine nitrogen at index {atom_idx}")
        
        if not found_amine:
            print("Warning: No protonated amine found in molecule!")
        
        print(f"RDKit formal charge sum: {Chem.GetFormalCharge(rdkit_mol)}")
        
        # Assign charges using Espaloma
        off_mol.assign_partial_charges('espaloma-am1bcc', toolkit_registry=toolkit_registry)
        
        # Print detailed charge information
        total_charge = sum(off_mol.partial_charges.magnitude)
        print(f"Final total charge: {total_charge}")
        print("\nFinal partial charges:")
        for atom, charge in zip(off_mol.atoms, off_mol.partial_charges):
            print(f"Atom {atom.molecule_atom_index} ({atom.symbol}): {charge}")
        
        # Convert to RDKit and write
        charged_rdkit = off_mol.to_rdkit()
        writer.write(charged_rdkit)

print("\nVerifying charges in output file:")
mol_check = Molecule.from_file('charged_ligands.sdf')
if not isinstance(mol_check, list):
    mol_check = [mol_check]

for i, mol in enumerate(mol_check):
    print(f"\nMolecule {i+1} ({mol.name}):")
    if "i_epik_Tot_Q" in mol.properties:
        print(f"Epik Total Charge: {mol.properties['i_epik_Tot_Q']}")
    for j, atom in enumerate(mol.atoms):
        print(f"Atom {j} ({atom.symbol}): {atom.partial_charge}")


