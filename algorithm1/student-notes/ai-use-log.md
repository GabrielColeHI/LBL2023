# AI-use log

The handoff (page 10) asks for a record of AI assistance and how each piece was
verified by a person. This feeds the journal's AI-use disclosure.

| Date | Tool / model | Purpose | Output | Human verification |
|---|---|---|---|---|
| 2026-10-27 | Claude Code (Claude Opus 5.5) | Explain the repo and `run_demo.py` | Verbal explanation | Cross-check against `algorithm1/README.md` |
| 2026-10-27 | Claude Code (Claude Opus 5.5) | Build the results dashboard | `algorithm1/dashboard/` | Values were traced to JSON by script; review the page and the method descriptions against `correlation-nn.md` |
| 2026-10-27 | Claude Code (Claude Opus 5.5) | Rerun tests, check the environment log, trace headline numbers | `student-notes/environment-log.md`, `headline-numbers.md` | Spot-check a few ledger rows by opening the JSON yourself |

Fill in the last column once you've done the check yourself.
