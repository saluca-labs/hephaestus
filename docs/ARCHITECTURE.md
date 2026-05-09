# Architecture

## Overview

Hephaestus is a modular, sensor-rich humanoid substrate, designed in the open under MIT, intended to be assembled from a federation of smart body segments rather than as a single monolithic robot. The architecture treats the body as a graph of self-aware segments that handshake at standardized bayonet couplings, share a common bus for power and data, and report their state up to a central torso aggregator. The CAD geometry is parametric Python code, the simulator description is generated from that code, and the sensor stack is replicated per segment instead of concentrated in a head. The design is opinionated where opinions buy modularity and deferred where deferral preserves option value, with the joint actuator family being the most important deferred decision.

This document captures the architectural calls that are locked, the questions that remain open, and the adjacencies that informed the design.

## Locked architectural decisions

These calls are committed and should not be re-litigated without explicit reason.

### Modular smart segments

Each body segment carries its own ESP32-S3, local battery, IMU, and time-of-flight sensor ring, and daisy-chains to a central torso bus. There is no monolithic controller. The motivation is fault isolation, hot-swap, and per-segment perception. A failed segment should not stop the rest of the body, and a swapped segment should not require a flash of the whole robot. The segment is the unit of design, fab, and replacement.

### Lens-mount-style electromechanical couplings

Every segment-to-segment interface is a bayonet quarter-turn coupling, inspired by camera lens mounts (EF in particular). The coupling carries mechanical load, power rails, I2C lines, and a segment ID. It is parametric: a single Python module produces every variant from a small sensor-pod mount up to a hip-load-bearing mount, with size and contact pattern set by the call site rather than by a separate file per part. Borrowing a coupling pattern from photography buys decades of tolerancing know-how that humanoid robotics has not yet developed on its own.

The first part shipped in this repo is the lens-mount coupling, male and female halves, in `design/lens_mount.py`.

### Distributed perception per segment

Every segment ships with a BNO085 nine-axis IMU and four to six VL53L5CX 8x8 time-of-flight sensors. The IMU lives near the segment's geometric center for clean orientation. One ToF aims into the joint cavity for redundant joint-angle sense. The remaining ToFs form an outward-facing ring for proximity and obstacle awareness. The IMU is shielded with a folded mu-metal enclosure to keep nearby motor magnetic fields from corrupting the magnetometer.

The pattern is a deliberate counterweight to the conventional humanoid posture of overinvesting in head-mounted cameras and underinvesting in full-body proprioception. A body that knows where its own limbs are tends to fall less.

### Tripteron-style exo-shell harness as overlay

Conventional rotational joints carry the rotation. A 3-DOF translational parallel mechanism (tripteron) wraps each joint as an active overlay, providing range-of-motion enforcement, redundant Cartesian endpoint sense, and gravity-compensation or assist torques. The overlay couples to the limb through a passive ball joint so that the underlying revolute or spherical joint is not over-constrained.

The overlay is research scope, not critical path. The exact set of joints that benefit from a tripteron overlay (probably shoulder and hip; probably skip knee and elbow) will be settled empirically.

### Conventional rotational joints underneath

Knee and elbow are revolute, with offset motor and belt or direct drive depending on the actuator pick. Shoulder and hip default to ball joint or 3-RRR spherical parallel mechanism (the rotational analog of tripteron), not tripteron itself. The wrist defaults to a 2-DOF revolute pair, with the option to expand if the end-effector decision moves toward a hand. Joint kinematics borrow topology from K-Scale Kbot (pitch-roll-yaw hip, no ankle roll) without copying exact dimensions.

### 3-RRR spherical mechanism for shoulder, wrist, and head-base candidates

3-RRR is a parallel rotational mechanism with three revolute-revolute-revolute legs, well suited to spherical workspaces. It is the rotational analog of tripteron: where tripteron solves three independent translations, 3-RRR solves three independent rotations. It is a research candidate for shoulder, wrist, and the head-base joint, with a ball-joint-with-three-tendon-actuators fallback if 3-RRR fab proves too tight on a desktop CNC.

### Scapulothoracic plate as the one tripteron-as-primary-joint case

The scapulothoracic complex in human anatomy is mostly translational rather than rotational. That makes it the one location on the body where tripteron is the right primary mechanism, not an overlay. Treating it as its own research path keeps the overlay-vs-primary distinction clean elsewhere.

### Mu-metal shielding for IMU near motors

BNO085 magnetometer drift inside a metal-bearing, motor-bearing segment is a known failure mode. The mitigation is a thin mu-metal foil enclosure folded into a three-walled box around the IMU, antenna face open. The exact tolerance for residual drift after shielding is an open question (see below), but the structural decision to shield is locked.

### Half-scale prototypes, full-scale design

The parametric build123d code defaults to full-scale dimensions. A `scale_factor` parameter, default 1.0, scales geometry uniformly across every part class; setting it to 0.5 produces a half-scale prototype. Joint torque calculations are sized for full-scale; prototype torques fall out roughly proportionally and give the actuator selection more flexibility on the prototype runs. The half-scale prototype maps roughly to the size class of well-known smaller humanoid research platforms, which is convenient for actuator-option sizing reference.

The convention is that prototype runs use `scale_factor=0.5` while locked production geometry stays at `scale_factor=1.0`. The slicer and CAM operate on the post-scale STL or STEP, so the fab pipeline stays scale-agnostic.

### build123d as parametric CAD source of truth

Geometry is Python. STL, STEP, and PNG previews are downstream artifacts, regenerated from source on demand. Earlier experiments with Blender plus Phobos for URDF were abandoned. The motivation is the same one that drove infrastructure-as-code in software: a folder of binary CAD files is hard to diff, hard to compose, and hard to reproduce, while a Python package is all three.

### Custom URDF / MJCF emitter that reads from the build123d Compound graph

Rather than maintain a hand-edited URDF in parallel with the geometry, a custom emitter walks the assembled build123d Compound recursively, treats each labeled part as a URDF link, extracts mass and inertia tensor from the geometry itself, emits joint blocks at lens-mount mating pairs, and references the exported STL files from the URDF. For MJCF, the K-Scale `urdf2mjcf` converter handles the final stage, so the emitter only ever produces URDF and the converter bridges to MuJoCo.

### ksim for sim integration

The K-Scale Labs ksim training infrastructure is the simulator and policy training stack. ksim is JAX-based, runs on a single CUDA GPU, and ships with reference configurations for similar humanoid topologies. Borrowing ksim removes the temptation to roll a custom training stack and keeps focus on the substrate.

## Open architectural questions

These are the calls that are deliberately deferred because deferring them preserves option value or because empirical data is needed first.

### Joint actuator selection (deferred)

The joint actuator family dominates total cost, walking gait quality, and integration effort. A curated option set has been captured separately; it spans custom BLDC plus harmonic drive, harvested or aftermarket motors from existing quadruped platforms, off-the-shelf serial-bus servos, sealed commercial modules, mid-cost CAN-driven brushless designs, hobbyist FOC builds, and PCB-stator axial-flux as an OSS-aligned in-joint direct-drive option. Each option carries its own tradeoff between cost, integration effort, supply chain, and torque density.

The substrate work (couplings, segment shells, sensor pods, build123d library, URDF emitter, power distribution) proceeds against the curated table without locking the choice. Final selection is reserved for a dedicated session once prototype runs need it.

### Bus protocol

The segment-to-torso bus could be RS-485, CAN, or ESP-NOW. RS-485 is the most boring choice and probably the right one for a wired body, but the time-of-flight frame bandwidth at scale (twelve segments, four to six ToF each, 10 Hz) may exceed what RS-485 handles cleanly without compression or downsampling. CAN is the obvious alternative; ESP-NOW would be wireless per segment but loses the I2C-on-the-bayonet idea. The decision is held until the first segment node firmware exists and bandwidth is measured rather than estimated.

### Pi 5 vs Jetson Orin Nano for torso companion compute

The torso aggregator runs the bus master, the state estimator, the high-level control loop, and the persona-layer endpoint. Pi 5 is cheaper and lower power and is fine for sensor aggregation plus light control. Jetson Orin Nano adds a GPU for on-board policy inference at roughly twice the cost and power. The default plan is to start with Pi 5 and swap to Jetson only if RL policy inference becomes the bottleneck.

### End-effectors for v1

The choice is between a rod stub and an actual hand for the first build. A rod stub is days of work, lets the body walk and balance and gesture without solving manipulation, and swaps out at the lens-mount coupling without forearm redesign. A five-finger underactuated hand is a four-to-twelve-week sub-project on its own. A parallel-jaw gripper sits in the middle. The default current plan is rod stub for v1, with a later hand or gripper dropping in as a swap. The call is genuinely open because it changes the wrist-DOF count.

## What is intentionally out of scope here

Future persona integration (the eventual binding of an agent identity to the embodied surface) is deferred. When that work happens, it will live behind a stable interface in a separate, possibly private, package, with the public body code calling into it. The decision keeps this repository focused on the substrate, where the OSS posture has clear leverage, and keeps the persona-binding work where it belongs.

## Adjacencies

These are the prior-art references that shaped the architecture without being copied wholesale.

- **K-Scale Labs Kbot.** Reference geometry for hip topology (pitch-roll-yaw, no ankle roll), reference URDF shape for the emitter to validate against, ksim and urdf2mjcf as upstream training and conversion infrastructure. K-Scale's posture (MIT license, OSS humanoid platform) directly motivates Hephaestus's posture.
- **Henrique Ferrolho's VL53L5CX-BNO08X-viewer.** Reference repository for combining a BNO085 IMU and a VL53L5CX time-of-flight array on an ESP32 with a Python viser viewer. The breadboard validation path for the sensor pod follows this layout closely.
- **build123d.** The parametric CAD library that the geometry source-of-truth invariant rests on. Apache 2.0 upstream.

Other reference threads (parallel mechanism literature, lens-mount tolerance practice, distributed-perception robotics work) sit further out and are surfaced piece by piece in the roadmap.
