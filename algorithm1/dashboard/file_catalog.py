"""Describe every file in the repository for the dashboard's Files tab.

Descriptions come from the files themselves (Python docstrings, MATLAB help
lines, Markdown headings, JSON keys), plus a role inferred from the name.
"""
import ast
import json
import re
import subprocess
from pathlib import Path

MAX_DESC = 320

# Files the student handoff (page 8 code map) points to first, with their topic.
START_HERE = {
    "algorithm1/README.md": "Orientation",
    "algorithm1/python/algorithm1.py": "Orientation",
    "algorithm1/python/run_demo.py": "Orientation",
    "algorithm1/matlab/algorithm1_qclab.m": "Orientation",
    "algorithm1/ising-algorithm1.md": "Ising model",
    "algorithm1/emnist-thresholds.md": "Ising model",
    "algorithm1/python/ising_monte_carlo.py": "Ising model",
    "algorithm1/python/ising_thresholds.py": "Ising model",
    "algorithm1/python/ising_grid_transfer.py": "Ising model",
    "algorithm1/python/ising_seed_sampling.py": "Ising model",
    "algorithm1/weizmann-xxz.md": "XXZ sampling",
    "algorithm1/python/xxz_image_gibbs_v2.py": "XXZ sampling",
    "algorithm1/python/xxz_sse_cluster.py": "XXZ sampling",
    "algorithm1/python/run_weizmann_xxz_v2.py": "XXZ sampling",
    "algorithm1/weizmann-petz.md": "Data and metrics",
    "algorithm1/xxz-two-seed-bpm.md": "Data and metrics",
    "algorithm1/python/weizmann_petz_data.py": "Data and metrics",
    "algorithm1/python/weizmann_petz_metrics.py": "Data and metrics",
    "algorithm1/python/segmentation_bpm.py": "Data and metrics",
    "algorithm1/iterative-seeds.md": "Seed readout",
    "algorithm1/python/xxz_two_seed.py": "Seed readout",
    "algorithm1/python/iterative_seed_readout.py": "Seed readout",
    "algorithm1/python/promotion_reliability.py": "Seed readout",
    "algorithm1/correlation-nn.md": "Learned decoder",
    "algorithm1/correlation-nn-summary.json": "Learned decoder",
    "algorithm1/correlation-nn-protocol.json": "Learned decoder",
    "algorithm1/python/correlation_nn_data.py": "Learned decoder",
    "algorithm1/python/correlation_nn.py": "Learned decoder",
    "algorithm1/python/run_correlation_nn.py": "Learned decoder",
    "algorithm1/python/audit_correlation_nn.py": "Learned decoder",
    "algorithm1/ising-petz.md": "Ising circuit",
    "algorithm1/python/ising_petz.py": "Ising circuit",
    "algorithm1/python/ising_petz_populations.py": "Ising circuit",
    "algorithm1/matlab/algorithm1_ising_petz_qclab.m": "Ising circuit",
    "algorithm1/quantum-heat-bath.md": "XXZ channels",
    "algorithm1/local-petz.md": "XXZ channels",
    "algorithm1/python/quantum_glauber.py": "XXZ channels",
    "algorithm1/python/local_petz.py": "XXZ channels",
    "algorithm1/python/local_petz_trajectories.py": "XXZ channels",
    "algorithm1/python/local_petz_tensor.py": "XXZ channels",
}

AREAS = [  # first matching prefix wins
    ("algorithm1/dashboard/", "Dashboard (this page)"),
    ("algorithm1/student-notes/", "Student notes"),
    ("algorithm1/python/", "Python research code"),
    ("algorithm1/matlab/", "MATLAB / QCLAB code"),
    ("algorithm1/tests/", "Automated tests"),
    ("algorithm1/results/", "Generated figures"),
    ("algorithm1/", "Study reports and records"),
    ("_", "Project website (Jekyll)"),
    ("index.md", "Project website (Jekyll)"),
    ("feed.xml", "Project website (Jekyll)"),
    ("", "Earlier projects (quantum walks, MATLAB)"),
]

PY_ROLES = [
    ("test_", "Test"), ("run_", "Experiment runner"), ("analyze_", "Analysis"),
    ("plot_", "Plotting"), ("audit_", "Audit"), ("confirm_", "Confirmation run"),
    ("finish_", "Final stage"), ("extend_", "Extension run"), ("fetch_", "Data download"),
]
JSON_ROLES = [
    ("protocol", "Pre-registered study plan"), ("amendment", "Documented protocol change"),
    ("selection", "Selected parameters"), ("summary", "Final numbers"),
    ("validation", "Validation checks"), ("environment", "Software environment"),
    ("manifest", "Input list"), ("calibration", "Calibration results"),
    ("confirmation", "Confirmation results"), ("case-results", "Per-image results"),
    ("controls", "Control results"), ("audit", "Audit results"), ("diagnostic", "Diagnostics"),
]
EXT_DESC = {
    ".png": "Figure image.", ".svg": "Figure (vector).", ".pdf": "Figure or document (PDF).",
    ".jpg": "Image.", ".jpeg": "Image.", ".fig": "MATLAB figure file (open in MATLAB).",
    ".mlx": "MATLAB live script (open in MATLAB to see code and output together).",
    ".mat": "MATLAB data file.", ".nb": "Mathematica notebook.",
    ".asv": "MATLAB autosave backup of a .m file; safe to ignore.",
    ".mp4": "Video.", ".qasm": "OpenQASM circuit export.", ".qpy": "Qiskit binary circuit export.",
    ".yml": "Configuration file.", ".xml": "XML file.", ".rb": "Ruby plugin for the Jekyll website.",
    ".html": "HTML page or template.", ".tex": "LaTeX source.", ".bat": "Windows script; double-click to run.",
}
NAME_DESC = {
    ".gitignore": "Tells Git which files not to track (virtual environment, large result arrays, caches).",
    ".gitattributes": "Git settings for how files are stored and compared.",
    "pytest.ini": "Configuration for the pytest suite; run it with: python -m pytest -c algorithm1/pytest.ini -q",
    "dashboard.html": "The generated dashboard page. Rebuilt by build_dashboard.py; don't edit it by hand.",
    "template.html": "Layout, styling and script for the dashboard. Data is inserted at build time.",
}
TYPE_OF = {".py": "Python", ".m": "MATLAB", ".mlx": "MATLAB", ".md": "Markdown", ".json": "JSON",
           ".png": "Figure", ".svg": "Figure", ".pdf": "Figure", ".jpg": "Figure", ".jpeg": "Figure",
           ".fig": "Figure", ".mat": "Data", ".txt": "Text", ".html": "HTML", ".bat": "Script"}


def _clip(text):
    text = " ".join(text.split())
    return text if len(text) <= MAX_DESC else text[:MAX_DESC - 1].rstrip() + "…"


def _read(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _python(path):
    src = _read(path)
    try:
        doc = ast.get_docstring(ast.parse(src))
    except SyntaxError:
        doc = None
    if doc:
        return doc.split("\n\n")[0]
    m = re.search(r"^\s*#\s*(.+)$", src, re.M)
    return m.group(1) if m else ""


def _matlab(path):
    lines = [l.strip() for l in _read(path).splitlines()[:15]]
    comments = [l.lstrip("%").strip() for l in lines if l.startswith("%")]
    comments = [c for c in comments if c]
    if not comments:
        return ""
    first = re.sub(r"^[A-Z0-9_]+\s+", "", comments[0])  # drop the "FUNCNAME " help prefix
    return " ".join([first] + comments[1:2])


def _markdown(path):
    text = _read(path)
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)  # Jekyll front matter
    head = re.search(r"^#+\s*(.+)$", text, re.M)
    body = [p for p in re.split(r"\n\s*\n", text) if p.strip() and not p.lstrip().startswith(("#", "!", "|", "<", "```"))]
    parts = [head.group(1) + "." if head else "", body[0] if body else ""]
    return " ".join(p for p in parts if p)


def _json(path):
    try:
        data = json.loads(_read(path))
    except ValueError:
        return "JSON data."
    if isinstance(data, dict):
        keys = list(data)
        shown = ", ".join(keys[:8]) + (", …" if len(keys) > 8 else ".")
        return f"Contains: {shown}"
    return f"List of {len(data)} entries." if isinstance(data, list) else "JSON data."


def _text(path):
    first = next((l for l in _read(path).splitlines() if l.strip()), "")
    return f"Text file. Starts: {first}" if first else "Text file."


def _role(rel, name, ext):
    if ext == ".py":
        return next((r for p, r in PY_ROLES if name.startswith(p)), "Library module")
    if ext == ".json":
        return next((r for p, r in JSON_ROLES if p in name), "Data record")
    if ext == ".md" and rel.startswith("algorithm1/") and "/" not in rel[len("algorithm1/"):]:
        return "Study report"
    if ext == ".m" and name.startswith("test_"):
        return "Test"
    return ""


def describe(repo, rel):
    path = repo / rel
    ext = path.suffix.lower()
    name = path.name
    reader = {".py": _python, ".m": _matlab, ".md": _markdown, ".json": _json, ".txt": _text}.get(ext)
    desc = NAME_DESC.get(name) or (reader(path) if reader else EXT_DESC.get(ext, ""))
    if not desc and name.startswith("test_") and ext == ".py":
        module = name[len("test_"):]
        where = f"python/{module}" if (repo / "algorithm1" / "python" / module).exists() else "that feature"
        desc = f"Automated tests for {where}."
    if not desc:
        desc = EXT_DESC.get(ext, "No description found in the file.")
    area = next(a for p, a in AREAS if rel.startswith(p))
    return {
        "path": rel,
        "dir": rel.rsplit("/", 1)[0] if "/" in rel else "(repository root)",
        "name": name,
        "type": TYPE_OF.get(ext, ext.lstrip(".").upper() or "File"),
        "area": area,
        "role": _role(rel, name, ext),
        "start": START_HERE.get(rel, ""),
        "desc": _clip(desc),
    }


def catalog(repo):
    """Tracked plus untracked-but-not-ignored files, so new work shows up too."""
    out = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=repo, text=True)
    files = sorted({f for f in out.splitlines() if f and (repo / f).is_file()})
    return [describe(repo, f) for f in files]
