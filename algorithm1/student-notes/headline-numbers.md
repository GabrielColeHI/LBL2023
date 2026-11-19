# Headline-number ledger (T01)

Each number quoted in the student handoff, the file and key it comes from, and
the value stored there. All values match at the precision the handoff displays.
Checked 27 October 2026 at commit `f93ea2f`.

Abbreviation: `NN` = `algorithm1/correlation-nn-summary.json`.

## Neural decoder study (handoff page 4)

| # | Handoff value | Source and key | Stored value |
|---|---|---|---|
| 1 | Ising neural, no seed: IoU 0.5799 [0.5382, 0.6212], BPM 0.4306 | `NN` → `metrics["Ising/none"]` | 0.57993 [0.53818, 0.62118], BPM 0.43059 |
| 2 | XXZ neural, no seed: 0.5994 [0.5574, 0.6396], BPM 0.4675 | `NN` → `metrics["XXZ/none"]` | 0.59941 [0.55740, 0.63965], BPM 0.46746 |
| 3 | Ising neural + seed: 0.6648 [0.6252, 0.7034], BPM 0.5222 | `NN` → `metrics["Ising/foreground"]` | matches |
| 4 | XXZ neural + seed: 0.6632 [0.6242, 0.7008], BPM 0.5297 | `NN` → `metrics["XXZ/foreground"]` | matches |
| 5 | Raw image + seed: 0.5441 [0.5067, 0.5821], BPM 0.3747 | `NN` → `metrics["image/foreground"]` | matches |
| 6 | Position + seed prior: 0.4824 [0.4453, 0.5189], BPM 0.2283 | `NN` → `metrics["prior/foreground"]` | matches |

## Comparisons (handoff pages 4–5)

| # | Handoff value | Source and key | Stored value |
|---|---|---|---|
| 7 | Neural + seed on the 75 historical sources: Ising 0.6660 | `NN` → `previous_two_seed_comparisons.Ising["Ising/foreground"].new` | 0.665958 |
| 8 | … XXZ 0.6702 | `NN` → `previous_two_seed_comparisons.XXZ["XXZ/foreground"].new` | 0.670166 |
| 9 | Two-seed rule: Ising 0.4988 | same, `.old` | 0.498846 |
| 10 | … XXZ 0.4973 | same, `.old` | 0.497251 |
| 11 | Fixed historical Hamiltonian: neural 0.6388 | `NN` → `historical_comparisons.Ising["Ising-historical/foreground"].new` | 0.638751 |
| 12 | … earlier adaptive readout 0.4135 | same, `.old` | 0.413487 |
| 13 | Seed-column networks: Ising 0.5249, XXZ 0.4863 | `NN` → `metrics["Ising-column/foreground"]`, `metrics["XXZ-column/foreground"]` | 0.524927, 0.486322 |
| 14 | Mismatched matrices: Ising 0.3325 | `NN` → `correlation_pairing_ablation["Ising/none"].mismatched` | 0.332543 |
| 15 | … XXZ 0.3366 | `NN` → `correlation_pairing_ablation["XXZ/none"].mismatched` | 0.336608 |
| 16 | XXZ − Ising, no seed: +0.0195 [0.0010, 0.0381] | `NN` → `xxz_minus_ising.none.iou` | 0.019478 [0.001038, 0.038081] |
| 17 | XXZ − Ising, with seed: −0.0016 [−0.0125, 0.0101] | `NN` → `xxz_minus_ising.foreground.iou` | −0.001642 [−0.012506, 0.010123] |

## Ising circuit (handoff page 6)

| # | Handoff value | Source and key | Stored value |
|---|---|---|---|
| 18 | 2×64 strip, 2,000 sweeps: Γ = 0.01676 ± 0.00097 | `ising-petz-summary.json`, sweep-2000 entry: `far_aligned`, `far_se` | 0.016762 ± 0.000974 |
| 19 | Exact Gibbs Γ = 0.129610 | same file: `exact_gibbs_far` | 0.129610 |
| 20 | Correlation-profile ∞-error ≈ 0.125 | same entry: `gamma_linf` | 0.125377 |
| 21 | 3.04 million CNOTs (128 spins × 2,000 sweeps) | 1520 CX per sweep (`ising-petz-summary.json`, `operations.cx`) × 2,000 | 3,040,000 |

## Earlier one- vs two-seed table (handoff page 4)

Traced 10 November 2026. Source: `algorithm1/xxz-two-seed-summary.json`, under
`groups["<model>/q90__two_max/16"].decisions.<rule>.<metric>.mean` (the group name is a
single key containing slashes), with `<model>` =
`Ising` or `XXZ` and `<rule>` = `one_background` (one seed) or `two_max` (two seeds).
The same table appears in `xxz-two-seed-bpm.md` lines 116–119.

| # | Row (16×16) | IoU (`iou`) | Unresolved (`unresolved`) | BPM r=1 (`bpm_iou_r1`) |
|---|---|---|---|---|
| 22 | Ising, one seed | 0.4025 → 0.402491 | 2.17% → 0.021732 | 0.3616 → 0.361594 |
| 23 | Ising, two seeds | 0.4988 → 0.498846 | 7.02% → 0.070184 | 0.4063 → 0.406334 |
| 24 | XXZ primary, one seed | 0.4013 → 0.401299 | 4.98% → 0.049816 | 0.3635 → 0.363492 |
| 25 | XXZ primary, two seeds | 0.4973 → 0.497251 | 10.80% → 0.108031 | 0.4061 → 0.406128 |

All match. Note: the "one seed" baseline in this table is the **background**-seed rule
(`one_background`, C(B,i) < 0), not the foreground-seed rule. Worth stating explicitly in
the manuscript.

## Local Petz star bath (handoff page 6)

| # | Handoff value | Source | Stored value |
|---|---|---|---|
| 26 | XXZ star-bath far-corner Γ on 2×16, sweep 50: −0.010120 [−0.051376, 0.031136] | `local-petz.md` line 216 (128 trajectories, b = 6, bond dimension 32, all-+x start) | −0.010120 [−0.051376, 0.031136] — matches the report |

Caveat: the raw trajectory data behind this row is under `results/local-petz/`, which
is git-ignored, so it is not in the repository. Only the report table is. Confirming it
from raw data needs the results archive from the PI. This record uses the older linear
coupling law.

## Still to trace

Nothing from the handoff. Row 26 is traced to the report only (see caveat).
