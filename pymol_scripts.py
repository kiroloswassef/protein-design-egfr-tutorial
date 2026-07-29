"""
PyMOL scripts for the EGFR de novo design tutorial project.

These are the parts of the pipeline written independently (target preparation
and comparative structural analysis). The backbone generation / sequence
design / structure validation steps use the ColabDesign RFdiffusion notebook
(see README.md > Attribution) and are not included here.

Environment: run inside Google Colab.
"""

# ── Setup ─────────────────────────────────────────────────────────────────
# !pip install pymol-open-source -q
import pymol
from pymol import cmd

pymol.finish_launching(['pymol', '-qc'])


# ── 1. Target preparation: EGFR kinase domain (PDB 1M17) ───────────────────
def prepare_egfr_target():
    """Fetch EGFR (1M17), strip solvent/ligands, isolate chain A,
    and save a clean target PDB for downstream design."""
    cmd.fetch('1M17')
    cmd.remove('solvent')
    cmd.remove('organic')
    cmd.select('egfr_target', 'chain A and polymer.protein')
    cmd.save('/content/target_egfr_clean.pdb', 'egfr_target')

    # Highlight the putative interface region near the ATP-binding pocket
    cmd.select('active_site', 'egfr_target and resi 718-725+765-775')
    cmd.show('sticks', 'active_site')
    cmd.color('yellow', 'active_site')

    cmd.orient('egfr_target')
    cmd.ray(800, 800)
    cmd.png('/content/egfr_prepared.png', dpi=150)
    print("Saved: /content/target_egfr_clean.pdb, /content/egfr_prepared.png")


# ── 2. Comparative analysis: best vs. worst ProteinMPNN design ─────────────
def compare_designs(best_path, worst_path, out_path='/content/comparison.png'):
    """Load two designed structures, color them, structurally align the
    worst design onto the best design, and render a comparison image.

    best_path / worst_path: paths to the .pdb files output by ProteinMPNN
    (e.g. 'outputs/egfr_binder_test/all_pdb/design0_n0.pdb' and
    'outputs/egfr_binder_test/all_pdb/design0_n6.pdb')
    """
    cmd.load(best_path, 'best_design')
    cmd.load(worst_path, 'worst_design')

    cmd.hide('everything')
    cmd.show('cartoon')
    cmd.color('green', 'best_design')
    cmd.color('red', 'worst_design')
    cmd.bg_color('white')

    # Superimpose worst design onto best design; prints RMSD to console
    cmd.align('worst_design', 'best_design')

    cmd.orient()
    cmd.ray(900, 700)
    cmd.png(out_path, dpi=150)
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    prepare_egfr_target()
    # After running the ColabDesign RFdiffusion/ProteinMPNN notebook:
    compare_designs(
        best_path='outputs/egfr_binder_test/all_pdb/design0_n0.pdb',
        worst_path='outputs/egfr_binder_test/all_pdb/design0_n6.pdb',
    )
