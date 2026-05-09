# Hephaestus roadmap

## Status

Phase 0 is in flight. The first mechanical part has been parametrized and is exporting clean STL, STEP, and PNG previews. Sensor breadboard validation is pending parts. Fab tooling (large-format FDM printer and desktop CNC) is on order, not delivered. No segment electronics have been built yet, no URDF has been emitted, and no joint actuator family has been selected. The phases below sequence the work; explicit dates are deliberately not locked, and phrasing leans on dependency anchors (post parts arrival, after Phase X completes) rather than calendar deadlines.

## Phase 0: substrate shakedown (in flight)

The goal of Phase 0 is to prove out the lowest-level substrate (parametric CAD, the first mechanical part, the sensor breadboard, the fab pipeline tooling) before any segment is built.

- build123d substrate. The CAD library is in active use. The lens-mount module is the seed; the next step is to promote it into a proper package with a top-level robot composer that takes a config file and emits every part for a named variant.
- Lens-mount coupling parametric. Male and female bayonet halves export cleanly to STL, STEP, and PNG. A `scale_factor` parameter is to be threaded through the part so half-scale prototype mates can be validated.
- Sensor pod breadboard validation. Once the first BNO085, VL53L5CX, and ESP32-S3 dev board land, the breadboard is wired per the Ferrolho reference layout, the viser viewer is run end to end, and clean reads are confirmed in hand before any segment is fabricated.
- Hardware arrival. The large-format FDM printer and the desktop CNC are on order. First end-to-end fab pipeline run uses the lens-mount male and female pair as the test article.
- Pipeline documentation. The end-to-end path from build123d to slicer to printer is documented as a repeatable process, including slicer profile per material.
- Cleanup. Stale exporter code from the abandoned Blender / Phobos pipeline is removed.

## Phase 1: one validated forearm segment (post parts arrival)

The goal of Phase 1 is to take one body segment, the smallest and simplest available (forearm), all the way through fab, sensor integration, power, and bench validation. The forearm is chosen because it is a single-axis cylinder with low geometric risk and the smallest electronics envelope.

- One validated forearm segment. The segment shell is parametrized, prints in one piece without internal supports, accepts a male lens-mount on one end and a female on the other, and houses the sensor pod, battery, and ESP32-S3 carrier without forced cable routing.
- Sensor pod inside the segment. BNO085 plus four to six VL53L5CX, mounted on a small carrier (perfboard for v1, KiCad PCB later), with the IMU shielded by a folded mu-metal enclosure. Stable orientation stream and 8x8 ToF frames at >= 10 Hz.
- Power harness for one segment. Local 18650 or 21700 pack, BMS, 3.3V and 5V regulators, current sense, over-current cutoff, and lens-mount contact allocation across the eight-pad ring (bus power, logic power, I2C, ID).
- Fab pipeline shakedown. End-to-end FDM run on the lens-mount pair plus the forearm shell, with dimensional tolerance characterized against the CAD. End-to-end CNC run on at least one load-bearing aluminum bracket, with tolerance characterized against the CAD.
- Bench validation gate. The forearm passes its own sensor checkout (clean reads, no stale frames, lens-mounts mate cleanly, power holds for >= 30 minutes under load) before any further segment work.

Phase 1 depends on Phase 0 closing and the ordered hardware delivering. The sensor breadboard validation can run in parallel with the printer and CNC arriving.

## Phase 2: limb assembly, joint mechanisms, simulator round-trip

The goal of Phase 2 is to take the validated single segment up into a limb (forearm plus upper arm joined at an elbow joint), make the geometry round-trip cleanly to a simulator, and ship the per-segment firmware that lets a torso aggregator command joint targets.

- Joint mechanisms. Per-joint variants land in the build123d library: revolute knee and elbow with offset motor and belt or direct drive (depending on the actuator pick), ball joint or 3-RRR spherical for shoulder and hip, 2-DOF revolute pair for wrist. The actuator final pick is a separate dedicated session; the substrate work proceeds against the curated option set.
- End-effector v1. Rod stub by default: a parametric rod with a male lens-mount on one end and a domed cap on the other. Swaps out at the bayonet without forearm redesign if a hand or gripper is later wired in.
- URDF / MJCF emitter. A custom emitter walks the assembled build123d Compound, extracts mass and inertia, emits link and joint blocks, references mesh STL files. The K-Scale `urdf2mjcf` converter handles the final stage to MuJoCo. The emitted URDF is validated against a known reference URDF for shape (link count, joint count, visual rendering).
- ESP32-S3 segment firmware. Per-segment firmware reads IMU plus four to six ToF, manages I2C addressing across the ToF array, talks to the torso aggregator over the bus, drives any local actuator, runs a safety state machine that refuses motion on stale sensors or dropped torso heartbeat, and supports OTA flash from torso.
- Torso companion compute. Pi 5 (default) or Jetson Orin Nano (if RL inference becomes the bottleneck) hosts the bus master, the state estimator, the control loop, and the persona-layer endpoint. Bus aggregation reads telemetry from all attached segments at >= 50 Hz.
- ksim sim round-trip. Emitted MJCF loads cleanly into ksim, a standing-balance policy trains in MuJoCo first, walking and reaching follow. Domain randomization across mass, friction, and motor delay hardens against the sim-to-real gap.
- Tripteron exo-shell harness in parallel. As a research arm, build a parametric tripteron in build123d, mount it on one elbow as an overlay, characterize the endpoint Cartesian sense and assist torque benefit. Not on the critical path.
- Bench validation gates. Per-stage checklists at sensor checkout, sub-assembly motion test, full-body suspended pose, suspended walking on a treadmill. The safety rig (suspended harness on overhead structure) is non-optional for any stage that involves a body large enough to fall.

Phase 2 depends on Phase 1 closing. Many of its sub-pieces (URDF emitter, segment firmware, torso compute) are independent and can run in parallel inside the phase.

## Phase 3: walking biped and future persona integration

The goal of Phase 3 is to take the body from "limb that moves under command" to "biped that walks under a sim-trained policy" and, beyond that, to the eventual binding to an agent persona that drives the body intentionally.

- Walking biped. Free-standing walk on flat ground with a sim-trained policy, with the demo bar set at ten steps without intervention. Gets there through the validation gate sequence: sensor checkout, sub-assembly motion, suspended standing, suspended walking, free walking.
- Bench validation, full sequence. Every gate from per-segment checkout through free walking has a written checklist; no stage advances until its gate passes; safety incidents are zero across the sequence.
- Future persona integration. The body becomes the physical surface for an agent persona. That integration is intentionally deferred to a separate package, behind a stable interface, with the public body code calling into it. The interface contract (what observations the persona gets, what actions it can issue, the safety contract that bounds those actions) is the deliverable that Phase 3 owes whether or not the persona itself is ready when the body is. Body action surface stays scripted-policy-capable so the substrate is useful even before the persona binds.

Phase 3 depends on Phase 2 closing. The persona-binding sub-piece is gated by a separate workstream that is not part of this repository.

## Cross-cutting work

Some pieces span multiple phases and do not slot cleanly into one. They run as side threads:

- Power distribution maturity. The first-segment power module lands in Phase 1; bus-level power arbitration, hot-swap, and BMS at the torso harden through Phase 2 as more segments come online.
- Fab pipeline maturity. The pipeline lands in Phase 1; slicer profile tuning per material, CAM template library, and post-process notes per part class accrete through every phase as new part classes appear.
- build123d library growth. The library scaffold lands in Phase 0; new part classes (segments, joints, end-effectors, power housings) accrete as each phase introduces them. Every part propagates `scale_factor` uniformly. Every part has a `build()` test under pytest.
- Sourcing strategy. Premium-fast suppliers for known-good prototype parts; bulk overseas suppliers for scaled buys with longer lead times; same-day local suppliers for hardware and stock. Strategy is steady; only the per-part sourcing decisions change phase to phase.
