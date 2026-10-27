# Results dashboard

A single self-contained HTML page. It needs no server or internet connection.

**To view it:** double-click `view_dashboard.bat`. It rebuilds the page from the
current repository and opens it in your browser. If you only want to look at the
existing page, open `dashboard.html` directly.

| File | Role |
|---|---|
| `view_dashboard.bat` | Launcher: rebuild, then open the page |
| `build_dashboard.py` | Reads `../correlation-nn-summary.json`, holds the headline-card and environment-log text, and writes `dashboard.html` |
| `file_catalog.py` | Builds the Files tab: lists every repository file and extracts its description from the file itself |
| `template.html` | Page layout, styling and script; the data is inserted at `__DATA__` |
| `dashboard.html` | Generated output; don't edit it by hand |

**Tabs**

- **Results:** neural-decoder study results, explanations, environment log and glossary.
- **Files:** every file in the repository, grouped and searchable. ★ marks the
  handoff's start-here files.

To change card or environment text, edit `build_dashboard.py`. To change layout
or explanations, edit `template.html`. Then rerun the `.bat`.
