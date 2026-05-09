# Hephaestus

Modular humanoid robotics substrate.

Hephaestus is the OSS home for a modular humanoid platform built from smart body
segments that couple to each other through standardized mechanical and electrical
interfaces. Each segment carries its own perception and compute, and the
mechanical handshake between segments is a parametric lens-mount coupling
generated from code.

## Architecture

- Modular smart segments, each with onboard perception and compute.
- Lens-mount couplings (bayonet-style) between segments for mechanical and
  electrical handshake.
- Distributed perception, with sensor fusion local to each segment before it
  reaches the central control loop.
- build123d as the parametric CAD substrate, so geometry is code, reviewable in
  diff and reproducible from source.

## Status

Early and exploratory. The first part shipped here is the lens-mount coupling
(male and female bayonet halves). Future segments, sensor mounts, and the
distributed perception stack will land incrementally.

## Quick start

```
pip install build123d
python -m design.build_all
```

This exports STL, STEP, and PNG previews into `design/build/` (gitignored).

## References

- Internal handoff doc: `Z:/_planning/HANDOFF_EMBODIED_AGENT_2026-05-08.md`
  (internal-only path on the author's workstation, not in this repo).
- Sensor reference: https://github.com/ferrolho/VL53L5CX-BNO08X-viewer

## License

MIT, see [LICENSE](LICENSE).

## Attribution

See [NOTICE](NOTICE) for upstream credits.
