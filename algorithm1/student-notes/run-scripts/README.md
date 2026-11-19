# Run scripts

**Double-click `run_all.bat`.** It reruns every T01 check (about 12 minutes), prints an
ok / FAILED summary, then opens the rebuilt dashboard. A failed step doesn't stop the
others.

| Step | What it runs | Output |
|---|---|---|
| `tests` | `pytest -q` in `algorithm1/` (expect 300 passed) | terminal only |
| `ising` | Ising Algorithm 1 study and its plots | `results/student-smoke/ising-algorithm1/` |
| `petz` | Ising Petz circuit exports and CNOT counts | `results/student-smoke/ising-petz/` |
| `localpetz` | Local Petz bath: exact 8-spin runs, circuit counts, plots | `results/student-smoke/local-petz/` |
| `scaling` | `benchmark_sizes.py`, 8×8 to 64×64 | `results/student-scaling/` |
| `dashboard` | Rebuilds `dashboard.html`, re-checking the number ledger and figure comparisons | `algorithm1/dashboard/dashboard.html` |

To run one step, open a terminal in this folder and give its name:

```
.\run_all.bat scaling
```

It uses the repository's `.venv` Python and sets `PYTHONUTF8=1`. Nothing writes to
the committed study folders. To make the scaling run longer, edit the options on the
`:run_scaling` line.
