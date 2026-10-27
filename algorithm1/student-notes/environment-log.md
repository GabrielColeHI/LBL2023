# Environment log (T01)

Machine: Windows 11 Home, Git Bash / PowerShell. Repository virtual environment
`.venv` at the repository root. Checked 27 October 2026.

| Item | Reported value | Status | How it was checked |
|---|---|---|---|
| Python | 3.12.4 | ✅ matches | `python --version` in `.venv` |
| pip | 21.1.3 → 26.2.2 | ❌ differs | `.venv` reports pip 24.0 |
| Test suite | 299/300 passed | ❌ differs | Rerun: `python -m pytest -q` in `algorithm1/` gave **300 passed in 120.16 s** |
| Failing test | Unicode encoding on Windows | ⚠️ not reproduced | Didn't fail in the rerun. Probably fixed by the change below |
| Fix applied | `PYTHONUTF8=1` | ⚠️ not observed | Not set in the rerun shell. The working tree has an uncommitted code fix instead (below) |
| Demo trace distance | 9.03e-15 | ✅ matches | `results/student-smoke/purification/report.json`: 9.0306e-15 |
| Ising Petz 128-spin CX count | 1520 | ✅ matches | `ising-petz-summary.json`, `ising-petz-matlab-validation.json`, `results/student-smoke/ising-petz/resources.json` |
| Commit | f93ea2f | ✅ matches | `git log -1` |

## Uncommitted change found in the working tree

```diff
- (args.output / "circuit.txt").write_text(str(prepared.circuit.draw(output="text", fold=-1)))
+ (args.output / "circuit.txt").write_text(str(prepared.circuit.draw(output="text", fold=-1)), encoding="utf-8")
```

File: `algorithm1/python/run_demo.py`, line 89. Without it, Windows uses its default
cp1252 encoding, which can't write the box-drawing characters in Qiskit's circuit
diagram. This is a portable fix; `PYTHONUTF8=1` only fixes it per shell.

## Smoke runs (handoff page 9)

| Command | Output | Result |
|---|---|---|
| `run_demo.py --output algorithm1/results/student-smoke/purification` | `report.json`, `circuit.qasm`, `circuit.txt`, `fixture.mat` | Trace distance 9.03e-15 |
| `run_ising_petz.py artifacts --output algorithm1/results/student-smoke/ising-petz` | `resources.json`, QASM/QPY circuits L4–L64, `local-update.png/svg` | CX per sweep 80 / 176 / 368 / 752 / 1520 for 8 / 16 / 32 / 64 / 128 spins |

The CX counts follow the handoff's 12N − 16 formula exactly
(for example, 12·128 − 16 = 1520).

## Not yet done

- Native MATLAB / QCLAB Ising check (`setup_ising_petz; run_ising_petz_demo`).
- Clean-checkout reproduction on a second machine.
