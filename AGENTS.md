# AGENTS.md

Instructions for AI coding agents working in this repository.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install build123d matplotlib trimesh
```

Python 3.10 or later; tested with 3.12 and build123d 0.13.0. There is no package metadata or lock file.

## Test

There is no test suite yet. The check is a full build:

```bash
python -m design.build_all
```

Passing looks like four `[build]` lines (male and female, STL and STEP), one `[build] preview` line, and `wrote 5 artifact(s)`. A `[preview] skipped` line means matplotlib or trimesh is missing. Then open `design/build/lens_mount_preview.png` and look at it: a geometry change is checked by looking at the part, not by the exit code.

## Conventions

- Geometry is code. STL, STEP and PNG files are build outputs in `design/build/` (gitignored); never commit them as sources.
- Every dimension lives in a dataclass of parameters (millimetres and degrees), as `LensMountParams` does; no magic numbers inside build functions.
- New parts get a class with `build()` and `export(out_dir)` and are added to `design/build_all.py`.
- Dependencies: build123d for geometry; matplotlib and trimesh only for previews.
- No em-dashes in docs. Use a plain hyphen.

## Do not

- Describe planned hardware (segments, electronics, firmware, URDF, ksim) as built. Only the lens-mount coupling exists.
- Change LICENSE or NOTICE.
- Commit secrets, hostnames, internal paths (for example drive-letter paths from a private machine) or personal emails.

## Done means

`python -m design.build_all` writes all five artifacts, the preview has been looked at, and README.md, llms.txt and llms-full.txt still describe the code (regenerate llms-full.txt from README.md, docs/ARCHITECTURE.md and docs/ROADMAP.md in the same change).
