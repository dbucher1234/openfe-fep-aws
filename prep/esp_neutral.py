"""
esp_neutral.py

Utility script to parmetrize with Espaloma a neutral ligand

"""

import warnings
warnings.filterwarnings("ignore", message=".*Recommend creating graphs by `dgl.graph(data)`.*")

from openff.toolkit.topology import Molecule
from openff.units import unit
import numpy as np
from rdkit import Chem
from rdkit.Chem import SDWriter
from espaloma_charge import charge

# Load all molecules from SDF file
off_mols = Molecule.from_file('ligands.sdf', allow_undefined_stereo=True)
if not isinstance(off_mols, list):
    off_mols = [off_mols]

print(f"Processing {len(off_mols)} molecules...")

# Open SDWriter for output
with SDWriter('charged_ligands.sdf') as writer:
    for i, off_mol in enumerate(off_mols):
        print(f"\nProcessing molecule {i+1}/{len(off_mols)}")
        
        # Convert to RDKit for Espaloma charging
        rdkit_mol = off_mol.to_rdkit()
        
        # Calculate charges using Espaloma
        charges = charge(rdkit_mol)
        
        # Convert charges to proper unit array and assign to OpenFF molecule
        charges_array = np.array(charges) * unit.elementary_charge
        off_mol.partial_charges = charges_array
        
        # Convert back to RDKit with charges
        charged_rdkit = off_mol.to_rdkit()
        
        # Write molecule with all properties preserved
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
