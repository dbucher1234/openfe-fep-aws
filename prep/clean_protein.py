#!/usr/bin/env python
"""
clean_pdb.py

Utility script to take a raw PDB structure (often straight from the PDB
or a docking program), patch up common issues with **PDBFixer**, and
write out a clean, simulation-ready file.  Specifically, it:

1. Loads the input PDB.
2. Detects and adds any missing residues and heavy atoms.
3. Adds hydrogens appropriate for pH 7.0.
4. Saves the repaired coordinates to <output_pdb>.

Run directly, it converts `protein.pdb` → `cleaned_protein.pdb`.
conda create -n openfe_prep -c conda-forge python=3.10 openmm pdbfixer
conda activate openfe_prep
python clean_pdb.py            # runs with protein.pdb → cleaned_protein.pdb

"""

from pdbfixer import PDBFixer
from openmm.app import PDBFile


def clean_pdb(input_pdb: str, output_pdb: str) -> None:
    """Fix missing residues/atoms and protonate at pH 7."""
    fixer = PDBFixer(filename=input_pdb)

    # Identify and patch gaps in the structure
    fixer.findMissingResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()

    # Add hydrogens appropriate for physiological pH
    fixer.addMissingHydrogens(pH=7.0)

    # Write the cleaned structure to disk
    with open(output_pdb, "w") as f:
        PDBFile.writeFile(fixer.topology, fixer.positions, f)


if __name__ == "__main__":
    input_pdb = "protein.pdb"
    output_pdb = "cleaned_protein.pdb"
    clean_pdb(input_pdb, output_pdb)
