"""Build the self-contained results dashboard (dashboard.html in this folder).

Results come from algorithm1/correlation-nn-summary.json; the Files tab comes
from file_catalog.py and the Progress tab from progress.py. Run
view_dashboard.bat to rebuild and open the page.
"""
import json
import sys
from pathlib import Path

from file_catalog import catalog
from progress import progress

here = Path(__file__).resolve().parent
repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else here.parents[1]
src = repo / "algorithm1" / "correlation-nn-summary.json"
out = here / "dashboard.html"

metrics = json.loads(src.read_text())["metrics"]
rows = [
    {
        "method": name,
        "iou": m["iou"]["mean"],
        "lo": m["iou"]["ci95"][0],
        "hi": m["iou"]["ci95"][1],
        "bpm": m["bpm"]["mean"],
    }
    for name, m in metrics.items()
]

headline = [
    ["Ising/foreground", "Ising neural + seed",
     "Best overall result. The network reads every Ising spin-pair correlation and is told one object pixel."],
    ["XXZ/foreground", "XXZ neural + seed",
     "Same setup with the quantum XXZ model. Essentially tied with Ising, so no demonstrated benefit from exchange."],
    ["Ising/none", "Ising neural, no seed",
     "No known pixel at all: the network must find the object from the correlations alone."],
    ["XXZ/none", "XXZ neural, no seed",
     "Seedless XXZ. Slightly above seedless Ising; the handoff's paired difference is +0.0195 [0.0010, 0.0381]."],
    ["image/foreground", "Raw image + seed",
     "Control: a similar small network given the grayscale pixels instead of correlations. Lower than both correlation decoders."],
    ["prior/foreground", "Position + seed prior",
     "Control: knows only pixel positions and the seed. Shows how much 'objects are usually central blobs' gives for free."],
]
missing = [h[0] for h in headline if h[0] not in metrics]
if missing:
    raise SystemExit(f"headline methods missing from JSON: {missing}")

# status: ok = checked against repo; diff = checked, does not match; note = stated, not reproduced
# last field: plain-language explanation shown as a tooltip
env = [
    ["Python", "3.12.4", "ok", "python --version in .venv",
     "The Python version the research environment was tested with. Matching it avoids package incompatibilities."],
    ["pip upgrade", "21.1.3 → 26.2.2", "diff", ".venv currently reports pip 24.0",
     "pip is Python's package installer. The version matters little scientifically, but the log should record what is actually installed."],
    ["Test suite", "299 / 300 passed", "diff", "rerun 2026-10-27: 300 / 300 passed in 120 s, with the run_demo.py fix below in place",
     "The automated checks in algorithm1/tests (physics formulas, conventions, samplers). The handoff's own run also passed 300/300."],
    ["Failing test", "Unicode encoding on Windows", "note", "not reproduced in rerun; likely already fixed by the uncommitted run_demo.py change",
     "Windows defaults to a non-UTF-8 encoding, so writing symbols in circuit diagrams can crash."],
    ["Fix applied", "PYTHONUTF8=1", "note", "not set in rerun shell. The working tree instead has an uncommitted fix: run_demo.py:89 writes circuit.txt with encoding=\"utf-8\"",
     "PYTHONUTF8=1 makes Python use UTF-8 everywhere. The code fix in run_demo.py solves the same problem permanently, for everyone."],
    ["Demo trace distance", "9.03e-15", "ok", "student-smoke/purification/report.json: 9.0306e-15",
     "How far the 4-pixel demo circuit's state is from the exact Gibbs state. ~1e-14 is floating-point noise, i.e. exact. The README quotes 1.95e-14 from an older run; both are at machine precision."],
    ["Ising Petz 128-spin CX count", "1520", "ok", "ising-petz-summary.json, matlab-validation.json, student-smoke resources.json",
     "Two-qubit CNOT gates per sweep of the local Ising circuit at 128 spins. Matches 12N − 16; × 2,000 sweeps gives the handoff's 3.04 million CNOTs."],
    ["Commit", "f93ea2f", "ok", "git HEAD",
     "The exact code version these results correspond to (the handoff's research baseline)."],
]

data = {"source": "algorithm1/correlation-nn-summary.json", "rows": rows, "headline": headline,
        "env": env, "files": catalog(repo), "progress": progress(repo)}
template = (here / "template.html").read_text(encoding="utf-8")
out.write_text(template.replace("__DATA__", json.dumps(data)), encoding="utf-8")
print(f"wrote {out} ({len(rows)} methods, {len(data['files'])} files)")
