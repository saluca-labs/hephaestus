# Hephaestus

Modular humanoid robotics substrate.

Status: pre-alpha, exploratory R&D. Phase 0 in flight.

## Overview

Hephaestus is the OSS home for a modular humanoid platform built from smart body segments that couple to each other through standardized mechanical and electrical interfaces. Each segment carries its own perception, power, and compute. The mechanical handshake between segments is a parametric lens-mount coupling generated from code, so the bayonet that joins a forearm to an upper arm comes out of the same Python file as the bayonet that joins a head to a torso.

The project exists because most humanoid platforms today fall into one of two camps. Either they are monolithic, designed end to end by one team with a single controller and a single perception stack, which makes them hard to extend and harder to repair, or they are research toys that solve one joint and stop. Hephaestus aims for a third path: a federation of segments that each know their own state, fail independently, and can be swapped at the bayonet without redesigning the body. Read the architecture document for the full set of locked design calls.

What makes the substrate different is that the geometry is code, not files. build123d is the source of truth; STL and STEP are downstream artifacts that get rebuilt from the Python every time. Couplings between segments use a lens-mount-style bayonet inspired by camera lens mounts, which buy decades of tolerancing and supply-chain know-how from the photography world. Every segment carries its own ESP32-S3, IMU, and a ring of time-of-flight sensors, so perception is distributed across the body rather than concentrated in a single head-mounted camera. The substrate is intentionally agnostic about which actuator family powers the joints; that decision is curated separately and held open until the prototype runs need it.

## Architecture sketch

- Modular smart segments. Every body segment carries its own ESP32-S3, local battery, IMU, and time-of-flight sensor ring. Segments daisy-chain to a central torso bus.
- Lens-mount-style electromechanical couplings between segments. Bayonet quarter-turn, EF-inspired, parametric. Carries mechanical load plus power plus I2C plus segment ID over a shared contact ring.
- Distributed perception per segment. BNO085 IMU and four to six VL53L5CX 8x8 ToF sensors per segment, fused locally before reaching the torso aggregator.
- Tripteron-style exo-shell harness as overlay above conventional rotational joints. Active ROM enforcement, redundant Cartesian sense, and gravity-comp / assist torque, without replacing the underlying joint.
- Conventional rotational joints underneath. Knee and elbow are revolute; shoulder and hip default to ball joint or 3-RRR spherical, not tripteron.
- build123d as parametric CAD source of truth. Custom emitter walks the build123d Compound graph and produces URDF / MJCF for simulator round-trip.
- ksim (K-Scale Labs) for RL training in MuJoCo, with a stable interface back to torso companion compute.

## Current status

Early R&D, Phase 0 in flight. The first mechanical part has shipped here: the lens-mount coupling, both male and female bayonet halves, parametric and exporting clean STL, STEP, and PNG previews. Sensor breadboard validation is pending parts. Fab tooling (a large-format FDM printer and a desktop CNC) is on order, not delivered. No segment electronics are built yet, no URDF has been emitted, and no joint actuator family has been selected. The architecture document covers the locked decisions that the rest of the substrate will be built against; the roadmap document sequences the pieces.

## Quick start

```
pip install build123d
python -m design.build_all
```

This generates the lens-mount male and female parts and writes STL, STEP, and matplotlib PNG previews into `design/build/` (gitignored).

## Repo layout

```
hephaestus/
  LICENSE              MIT
  NOTICE               upstream credits
  README.md            this file
  design/
    __init__.py
    lens_mount.py      first part: parametric bayonet coupling
    build_all.py       runs every part's build() and writes outputs
  docs/
    ARCHITECTURE.md    locked decisions and open questions
    ROADMAP.md         phased plan and per-phase deliverables
```

## Deeper detail

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the locked architectural decisions and the open questions that remain. See [docs/ROADMAP.md](docs/ROADMAP.md) for the phased delivery plan.

## License

MIT. See [LICENSE](LICENSE).

## Attribution

See [NOTICE](NOTICE) for upstream credits, including K-Scale Labs (Kbot reference geometry, ksim, urdf2mjcf), Henrique Ferrolho (VL53L5CX-BNO08X reference viewer), and the build123d project.
