# De Novo Protein Design Pipeline: PyMOL → RFdiffusion → ProteinMPNN → AlphaFold

**Author:** Kirolos Abdelmeseh Wassef (Koko)
**Status:** Learning project / proof-of-concept
**Environment:** Google Colab (T4 GPU)

## Overview

This is a hands-on learning project built while preparing for an M.Sc. in Chemical Biology at
Xiamen University (Prof. Liu-Lin Yang's lab), focused on ADC synthesis, peptide synthesis, and
AI-assisted protein design. The goal was to walk through a complete, minimal AI-driven protein
design workflow end-to-end — from preparing a real drug target to generating and validating a
novel protein backbone — using tools that are standard in the field (RFdiffusion, ProteinMPNN,
AlphaFold) alongside PyMOL for structural preparation and visualization.

This is **not** a research result — it is a documented tutorial project demonstrating the
workflow and tool literacy.

## Pipeline

```
1. Target preparation (PyMOL)
        ↓
2. Backbone generation (RFdiffusion)
        ↓
3. Sequence design (ProteinMPNN)
        ↓
4. Structure validation (AlphaFold)
        ↓
5. Comparative analysis (PyMOL)
```

## 1. Target Preparation — PyMOL

Target: **EGFR kinase domain** (PDB: [1M17](https://www.rcsb.org/structure/1M17)), a clinically
relevant receptor tyrosine kinase and a well-known small-molecule/antibody drug target in
oncology.

```python
cmd.fetch('1M17')
cmd.remove('solvent')
cmd.remove('organic')
cmd.select('egfr_target', 'chain A and polymer.protein')
cmd.save('/content/target_egfr_clean.pdb', 'egfr_target')
```

Steps performed:
- Removed crystallographic solvent and co-crystallized ligands
- Isolated chain A (protein only)
- Selected and visualized a putative interface region (residues 718–725 and 765–775, near the
  ATP-binding pocket) using `sticks` and `surface` representations

*(see `screenshots/egfr_prepared.png`)*

## 2. Backbone Generation — RFdiffusion

Used the [ColabDesign RFdiffusion notebook](https://colab.research.google.com/github/sokrypton/ColabDesign/blob/v1.1.1/rf/examples/diffusion.ipynb)
to generate a novel 100-residue protein backbone unconditionally (no target constraints, as a
first proof-of-concept run).

| Parameter | Value |
|---|---|
| contigs | 100 |
| iterations | 50 |
| num_designs | 1 |

Runtime: ~2.5 min on a Colab T4 GPU.

*(see `screenshots/rfdiffusion_backbone.png`)*

## 3. Sequence Design — ProteinMPNN

The generated backbone was passed to ProteinMPNN to design 8 candidate amino acid sequences
compatible with that fold.

| Parameter | Value |
|---|---|
| num_seqs | 8 |
| mpnn_sampling_temp | 0.1 |
| rm_aa | C (cysteine excluded) |
| num_recycles | 1 |

## 4. Structure Validation — AlphaFold

Each of the 8 MPNN sequences was refolded with AlphaFold to check whether it actually adopts the
intended backbone shape. Key metrics:

| Design | pLDDT ↑ | RMSD ↓ | pAE ↓ | Verdict |
|---|---|---|---|---|
| **design 0** | 0.881 | **0.909** | 4.983 | **Best** — high confidence, near-perfect match to target backbone |
| design 3 | 0.879 | 5.202 | 1.847 | Good confidence, moderate structural deviation |
| design 5 | 0.876 | 4.832 | 1.784 | Good confidence, moderate structural deviation |
| design 6 | 0.784 | **8.765** | 7.739 | **Worst** — low confidence, large structural deviation |

- **pLDDT**: AlphaFold's per-residue confidence (0–1, higher = better)
- **RMSD**: deviation (Å) between the AlphaFold-predicted fold and the RFdiffusion backbone
  (lower = the sequence actually folds into the intended shape)
- **pAE**: predicted alignment error, a measure of confidence in relative domain positioning
  (lower = better)

**Interpretation:** design 0 is the only sequence that both folds with high confidence (pLDDT)
*and* reproduces the intended backbone geometry (low RMSD) — i.e., the only design that would be
a reasonable candidate to consider for further work. design 6 illustrates a failure mode: a
sequence can still receive a plausible pLDDT while folding into a completely different,
extended/unstructured shape (high RMSD) — a reminder that a single metric is not sufficient for
evaluating a design.

## 5. Comparative Analysis — PyMOL

Best (design 0, green) vs. worst (design 6, red) designs were loaded into PyMOL and
structurally aligned:

```python
cmd.load('outputs/egfr_binder_test/all_pdb/design0_n0.pdb', 'best_design')
cmd.load('outputs/egfr_binder_test/all_pdb/design0_n6.pdb', 'worst_design')
cmd.color('green', 'best_design')
cmd.color('red', 'worst_design')
cmd.align('worst_design', 'best_design')
```

*(see `screenshots/comparison.png`)*

The visual result matches the numerical metrics: design 0 forms a compact, well-packed
helical bundle typical of a stable folded protein, while design 6 is an extended, loosely
structured chain — a visibly poor design.

## Key takeaways

- Confirmed a working, GPU-free-tier-friendly setup for RFdiffusion/ProteinMPNN/AlphaFold on
  Google Colab (no local installation required — sidesteps an incompatible local Windows 7
  machine entirely)
- Practiced reading and cross-validating AI protein design outputs using multiple metrics
  (pLDDT, RMSD, pAE) rather than trusting a single number
- Built a reusable PyMOL preparation → visualization workflow for both real (PDB-derived) and
  AI-generated structures

## Next steps

- [ ] Repeat with **hotspot-conditioned** binder design targeting the EGFR ATP-binding region
      specifically (`ppi.hotspot_res`), rather than unconditional generation
- [ ] Explore motif scaffolding for a defined functional site
- [ ] Apply the same pipeline to a target more directly relevant to the ADC/antibody engineering
      project (e.g., a linker-payload interface model)

## Tools used

- [PyMOL (open-source)](https://github.com/schrodinger/pymol-open-source)
- [RFdiffusion](https://github.com/RosettaCommons/RFdiffusion) (RosettaCommons)
- [ProteinMPNN](https://github.com/dauparas/ProteinMPNN)
- [AlphaFold](https://github.com/google-deepmind/alphafold)
- [ColabDesign](https://github.com/sokrypton/ColabDesign) notebook wrapper
- Google Colab (T4 GPU, free tier)
