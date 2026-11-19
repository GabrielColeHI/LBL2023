"""Data for the dashboard's Progress tab: T01 status, number ledger, reproduced figures, scaling run.

Ledger values are re-read from the JSON files on every build, so a row turns
red if a summary file changes. Figure checks compare regenerated PNGs with the
committed ones pixel by pixel; missing files are reported, not skipped.
"""
import base64
import io
import json
from pathlib import Path

NN = "algorithm1/correlation-nn-summary.json"
PETZ = "algorithm1/ising-petz-summary.json"
TWO = "algorithm1/xxz-two-seed-summary.json"

# [item, status, note]; status: done / open / you (needs the student, not a script)
T01 = [
    ["Environment log", "done", "student-notes/environment-log.md and the Results tab. pip version and test count differ from the handoff."],
    ["Conventions note", "you", "student-notes/conventions.tex is written. Compile it on Overleaf, check it fits one page, reword it yourself."],
    ["Headline-number ledger", "done", "All 26 handoff numbers traced (table below). Row 26 is traced to its report only; its raw data is in the archive."],
    ["Regenerate one plot per study family", "done", "3 families rerun from scratch (table below). The others need the archived sample banks."],
    ["Request manuscript sources and results archive", "you", "Email the PI: manuscript LaTeX and the ~19 GB results archive not in Git."],
    ["MATLAB Ising check", "you", "MATLAB is not installed on this machine. Use MATLAB Online through OSU."],
]

DISCREPANCIES = [
    "pip in .venv is 24.0, not the 26.2.2 the handoff records.",
    "Tests pass 300/300, not 299/300. The Windows Unicode failure is fixed by the run_demo.py UTF-8 change.",
    "Demo trace distance 9.03e-15 vs README 1.95e-14 (both machine precision).",
    "Tie rule differs: algorithm1.py:251 uses strict Γ > 0; Weizmann and two-seed runners treat |·| ≤ 1e-12 as zero.",
    "Local Petz circuit counts: rerun gives 2 more unrouted and 14 more routed CNOTs per sweep than the local-petz.md table "
    "at every size (e.g. 2×16: 7,626 vs 7,624; 39,606 vs 39,592), with identical depths and the locked Qiskit 2.5.2. "
    "The report table is probably from an older code version.",
    "The 'one seed' baseline in the earlier two-seed table is the background-seed rule, not the foreground-seed rule.",
]


def m(key, metric="iou"):
    return ["metrics", key, metric]



def nn_row(key, iou, lo, hi, bpm):
    return [(iou, NN, m(key) + ["mean"]), (lo, NN, m(key) + ["ci95", 0]), (hi, NN, m(key) + ["ci95", 1]),
            (bpm, NN, m(key, "bpm") + ["mean"])]


def two(model, rule, iou, unresolved, bpm):
    base = ["groups", f"{model}/q90__two_max/16", "decisions", rule]
    return [(iou, TWO, base + ["iou", "mean"]), (unresolved, TWO, base + ["unresolved", "mean"]),
            (bpm, TWO, base + ["bpm_iou_r1", "mean"])]


# [#, handoff page, what it is, [(displayed value, file, key path), ...]]; no checks = traced to a report only
LEDGER = [
    [1, 4, "Ising neural, no seed: IoU, CI, BPM", nn_row("Ising/none", "0.5799", "0.5382", "0.6212", "0.4306")],
    [2, 4, "XXZ neural, no seed", nn_row("XXZ/none", "0.5994", "0.5574", "0.6396", "0.4675")],
    [3, 4, "Ising neural + seed", nn_row("Ising/foreground", "0.6648", "0.6252", "0.7034", "0.5222")],
    [4, 4, "XXZ neural + seed", nn_row("XXZ/foreground", "0.6632", "0.6242", "0.7008", "0.5297")],
    [5, 4, "Raw image + seed (control)", nn_row("image/foreground", "0.5441", "0.5067", "0.5821", "0.3747")],
    [6, 4, "Position + seed prior (control)", nn_row("prior/foreground", "0.4824", "0.4453", "0.5189", "0.2283")],
    [7, 4, "Neural + seed on the 75 historical sources, Ising",
     [("0.6660", NN, ["previous_two_seed_comparisons", "Ising", "Ising/foreground", "new", "mean"])]],
    [8, 4, "… XXZ", [("0.6702", NN, ["previous_two_seed_comparisons", "XXZ", "XXZ/foreground", "new", "mean"])]],
    [9, 4, "Two-seed rule on the same sources, Ising",
     [("0.4988", NN, ["previous_two_seed_comparisons", "Ising", "Ising/foreground", "old", "mean"])]],
    [10, 4, "… XXZ", [("0.4973", NN, ["previous_two_seed_comparisons", "XXZ", "XXZ/foreground", "old", "mean"])]],
    [11, 5, "Fixed historical Hamiltonian, neural",
     [("0.6388", NN, ["historical_comparisons", "Ising", "Ising-historical/foreground", "new", "mean"])]],
    [12, 5, "… earlier adaptive readout",
     [("0.4135", NN, ["historical_comparisons", "Ising", "Ising-historical/foreground", "old", "mean"])]],
    [13, 5, "Seed-column networks, Ising and XXZ",
     [("0.5249", NN, m("Ising-column/foreground") + ["mean"]), ("0.4863", NN, m("XXZ-column/foreground") + ["mean"])]],
    [14, 5, "Mismatched matrices, Ising", [("0.3325", NN, ["correlation_pairing_ablation", "Ising/none", "mismatched", "mean"])]],
    [15, 5, "… XXZ", [("0.3366", NN, ["correlation_pairing_ablation", "XXZ/none", "mismatched", "mean"])]],
    [16, 5, "XXZ − Ising, no seed",
     [("0.0195", NN, ["xxz_minus_ising", "none", "iou", "mean"]), ("0.0010", NN, ["xxz_minus_ising", "none", "iou", "ci95", 0]),
      ("0.0381", NN, ["xxz_minus_ising", "none", "iou", "ci95", 1])]],
    [17, 5, "XXZ − Ising, with seed",
     [("-0.0016", NN, ["xxz_minus_ising", "foreground", "iou", "mean"]),
      ("-0.0125", NN, ["xxz_minus_ising", "foreground", "iou", "ci95", 0]),
      ("0.0101", NN, ["xxz_minus_ising", "foreground", "iou", "ci95", 1])]],
    [18, 6, "2×64 Ising strip, 2,000 sweeps: Γ ± SE",
     [("0.01676", PETZ, ["long", 1, "records", 6, "far_aligned"]), ("0.00097", PETZ, ["long", 1, "records", 6, "far_se"])]],
    [19, 6, "Exact Gibbs Γ", [("0.129610", PETZ, ["long", 1, "exact_gibbs_far"])]],
    [20, 6, "Correlation-profile ∞-error", [("0.125", PETZ, ["long", 1, "records", 6, "gamma_linf"])]],
    [21, 6, "CNOTs per sweep at 128 spins (× 2,000 = 3.04M)", [("1520", PETZ, ["resources", 4, "operations", "cx"])]],
    [22, 4, "Earlier table, Ising one seed: IoU, unresolved, BPM", two("Ising", "one_background", "0.4025", "2.17%", "0.3616")],
    [23, 4, "… Ising two seeds", two("Ising", "two_max", "0.4988", "7.02%", "0.4063")],
    [24, 4, "… XXZ primary, one seed", two("XXZ", "one_background", "0.4013", "4.98%", "0.3635")],
    [25, 4, "… XXZ primary, two seeds", two("XXZ", "two_max", "0.4973", "10.80%", "0.4061")],
    [26, 6, "XXZ star-bath far-corner Γ, 2×16, sweep 50: −0.010120 [−0.051376, 0.031136]", []],
]
REPORT_ONLY = {26: "local-petz.md line 216. Raw trajectories are git-ignored; confirm from the results archive."}

# [family, how it was rerun, run time, committed folder, regenerated folder, [figure names], note if not identical]
FIGURES = [
    ["Ising Algorithm 1 (exact Gibbs, small images)",
     "run_ising_algorithm1.py, then plot_ising_algorithm1.py", "60 s",
     "results/ising-algorithm1", "results/student-smoke/ising-algorithm1",
     ["segmentation-examples", "alpha-sweep", "couplings-temperature"], ""],
    ["Ising Petz circuit (T07 resource counts)",
     "run_ising_petz.py artifacts (27 Oct smoke run)", "< 1 min",
     "results/ising-petz/circuits", "results/student-smoke/ising-petz/circuits", ["local-update"], ""],
    ["Local Petz bath (XXZ, 8 spins + circuit scaling)",
     "run_local_petz.py dense and resources, then plot_local_petz.py", "7 min",
     "results/local-petz", "results/student-smoke/local-petz",
     ["local-update", "circuit-scaling", "local-vs-global"],
     "circuit-scaling: CNOT counts +2 / +14 per sweep vs the committed figure (see discrepancies). "
     "local-vs-global: expected to differ; the global-recovery curve needs quantum-glauber/n8, which was not rerun."],
]
NOT_RERUN = [
    ["Neural decoders (correlation-nn)", "Needs the 8,192-snapshot correlation banks from the results archive; retraining takes hours."],
    ["Weizmann XXZ / two-seed / XYZ", "Needs the archived Monte Carlo sample banks and the Weizmann images."],
    ["Weizmann Petz", "Needs the archived bath runs."],
    ["EMNIST Ising", "Needs the EMNIST download (fetch_emnist.py) and long sampler runs."],
]


def lookup(repo, file, path):
    value = json.loads((repo / file).read_text(encoding="utf-8"))
    for k in path:
        value = value[k]
    return value


def matches(shown, value):
    if shown.endswith("%"):
        shown, value = shown[:-1], value * 100
    decimals = len(shown.split(".")[1]) if "." in shown else 0
    return abs(round(value, decimals) - float(shown)) < 10 ** -(decimals + 3)


def ledger(repo):
    rows = []
    for num, page, label, checks in LEDGER:
        cells, ok = [], True
        for shown, file, path in checks:
            try:
                value = lookup(repo, file, path)
                good = matches(shown, value)
            except (OSError, KeyError, IndexError, TypeError):
                value, good = None, False
            ok &= good
            cells.append({"shown": shown, "stored": value, "ok": good, "file": file.split("/")[-1],
                          "path": " → ".join(str(k) for k in path)})
        status = ("ok" if ok else "diff") if checks else "report"
        rows.append({"num": num, "page": page, "label": label, "status": status, "checks": cells,
                     "note": REPORT_ONLY.get(num, "")})
    return rows


def thumbnail(path, width=520):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((width, width * 3))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def compare(a, b):
    import numpy as np
    from PIL import Image
    if not a.exists() or not b.exists():
        return "missing"
    x, y = (np.asarray(Image.open(p).convert("L")) for p in (a, b))
    if x.shape != y.shape:
        return "size differs"
    frac = float((x != y).mean())
    return "identical" if frac == 0 else f"{100 * frac:.1f}% of pixels differ"


def figures(repo):
    base = repo / "algorithm1"
    out = []
    for family, how, time, old, new, names, note in FIGURES:
        figs = []
        for n in names:
            a, b = base / old / f"{n}.png", base / new / f"{n}.png"
            result = compare(a, b)
            figs.append({"name": n, "result": result, "img": thumbnail(b) if b.exists() else "",
                         "path": f"{new}/{n}.png"})
        out.append({"family": family, "how": how, "time": time, "figs": figs, "note": note})
    return out


def scaling(repo):
    folder = repo / "algorithm1" / "results" / "student-scaling"
    if not (folder / "results.json").exists():
        return None
    d = json.loads((folder / "results.json").read_text())
    keep = ["side", "n", "seconds", "iou", "rhat_max", "b"]
    return {"settings": d["settings"], "K": d["K"], "tau": d["tau"], "alpha": d["alpha"],
            "rows": [{k: r[k] for k in keep} for r in d["results"]],
            "img": thumbnail(folder / "sizes.png", 1100) if (folder / "sizes.png").exists() else ""}


def progress(repo):
    return {"t01": T01, "discrepancies": DISCREPANCIES, "ledger": ledger(repo), "figures": figures(repo),
            "not_rerun": NOT_RERUN, "scaling": scaling(repo)}
