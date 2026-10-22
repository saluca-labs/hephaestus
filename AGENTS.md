# AGENTS.md

Instructions for AI coding agents working in this repository.

## What this is

A design repository for a modular humanoid robot. The only code is one parametric part, a lens-mount bayonet coupling in build123d (Python CAD), and the script that builds it; everything else is design intent.

## Read in this order

1. [README.md](README.md): status and the two known geometry issues (one tab instead of three; the halves do not interlock).
2. [design/lens_mount.py](design/lens_mount.py): `LensMountParams` (every dimension) and `LensMount` (`build()`, `export(out_dir)`).
3. [design/build_all.py](design/build_all.py): the only entry point; builds both sides and renders the preview.
4. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/ROADMAP.md](docs/ROADMAP.md): intended design and phases, not built work.

## What you can and cannot see

- You can see: the coupling geometry code, the build script, the architecture and roadmap documents, and one captured preview image (`docs/img/`).
- You cannot see, because it does not exist anywhere in this repository: segment electronics, firmware, a bus protocol implementation, a URDF or MJCF emitter, simulator or ksim integration, a `scale_factor` parameter, tests, or package metadata. The joint actuator choice is open. Persona integration is planned for a separate package that does not exist yet.
- Build outputs (`design/build/`) are gitignored; you only see them after running the build.

## The only numbers to trust

| Number | Source |
|---|---|
| Default dimensions (mm, degrees) | `LensMountParams` in `design/lens_mount.py` |
| Five artifacts per full build (2 STL, 2 STEP, 1 PNG) | `main()` in `design/build_all.py` |
| Fused male tab volume 173.44 mm^3, equal to one wedge | measured; the script is in README "Status" |
| Female cutters remove 189.77 mm^3 | measured; same script |

Sensor counts, torques, bandwidths and scale factors in `docs/ARCHITECTURE.md` and `docs/ROADMAP.md` are design targets, not measurements.

## Quickstart for an agent

```bash
python -m design.build_all
```

```python
from design.lens_mount import LensMount, LensMountParams
solid = LensMount(side="male", params=LensMountParams()).build()
```

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

Passing looks like four `[build]` lines (male and female, STL and STEP), one `[build] preview` line, and `wrote 5 artifact(s)`. A `[preview] skipped` line means matplotlib or trimesh is missing. Then open `design/build/lens_mount_preview.png` and look at it: a geometry change is checked by looking at the part and measuring volumes, not by the exit code.

## Conventions

- Geometry is code. STL, STEP and PNG files are build outputs in `design/build/` (gitignored); never commit them as sources.
- Every dimension lives in a dataclass of parameters (millimetres and degrees), as `LensMountParams` does; no magic numbers inside build functions.
- New parts get a class with `build()` and `export(out_dir)` and are added to `design/build_all.py`.
- Dependencies: build123d for geometry; matplotlib and trimesh only for previews.
- No em-dashes in docs. Use a plain hyphen.

## Do not

- Describe planned hardware (segments, electronics, firmware, URDF, ksim) as built. Only the lens-mount coupling exists.
- Describe the coupling as a working three-tab bayonet. As generated it has one tab and the halves do not interlock.
- Change LICENSE or NOTICE.
- Commit secrets, hostnames, internal paths (for example drive-letter paths from a private machine) or personal emails.

## Done means

`python -m design.build_all` writes all five artifacts, the preview has been looked at, and README.md, llms.txt and llms-full.txt still describe the code (regenerate llms-full.txt from README.md, docs/ARCHITECTURE.md and docs/ROADMAP.md in the same change). If the "How it works" diagram in README.md no longer matches `design/`, update it in the same change.
