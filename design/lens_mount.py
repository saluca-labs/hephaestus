"""Parametric bayonet lens-mount coupling for Saluca humanoid joints.

EF-inspired 3-tab quarter-turn lock. Male side has protruding tabs; female
side has matching pass-through slots plus a back channel that captures the
tabs after a 90 degree rotation.

The mount carries mechanical load + power + I2C between body segments.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin
from pathlib import Path
from typing import Literal

from build123d import (
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    Cylinder,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    PolarLocations,
    Rectangle,
    export_step,
    export_stl,
    revolve,
)


@dataclass
class LensMountParams:
    """All dimensions in millimeters / degrees."""

    flange_outer_dia: float = 54.0
    flange_depth: float = 8.0
    inner_bore_dia: float = 44.0

    n_tabs: int = 3
    tab_arc_deg: float = 50.0
    tab_radial_thick: float = 3.0
    tab_axial_thick: float = 2.5
    bayonet_collar_dia: float = 50.0
    bayonet_collar_len: float = 6.0
    slot_clearance_deg: float = 4.0
    slot_clearance_mm: float = 0.3

    n_screw_holes: int = 4
    screw_clearance_dia: float = 3.4
    screw_pcd: float = 49.0

    n_contacts: int = 8
    contact_radius_mm: float = 22.0
    contact_arc_deg: float = 120.0
    contact_pad_dia: float = 2.0
    contact_pad_height: float = 1.0

    channel_axial_clearance: float = 0.4


def _flange_disc(p: LensMountParams) -> Part:
    """Disc with central bore + N mounting screw holes, centered at origin in Z."""
    with BuildPart() as bp:
        Cylinder(radius=p.flange_outer_dia / 2, height=p.flange_depth)
        Cylinder(radius=p.inner_bore_dia / 2, height=p.flange_depth, mode=Mode.SUBTRACT)
        with PolarLocations(p.screw_pcd / 2, p.n_screw_holes):
            Cylinder(
                radius=p.screw_clearance_dia / 2,
                height=p.flange_depth,
                mode=Mode.SUBTRACT,
            )
    return bp.part


def _bayonet_collar(p: LensMountParams) -> Part:
    """Tubular collar protruding axially from the flange. Sits in -Z."""
    with BuildPart() as bp:
        Cylinder(radius=p.bayonet_collar_dia / 2, height=p.bayonet_collar_len)
        Cylinder(
            radius=p.inner_bore_dia / 2,
            height=p.bayonet_collar_len,
            mode=Mode.SUBTRACT,
        )
    # collar centered on origin; shift so its top face is at z = -flange/2 (joins flange bottom)
    z_shift = -(p.flange_depth / 2 + p.bayonet_collar_len / 2)
    return bp.part.locate(Location((0, 0, z_shift)))


def _wedge(inner_r: float, outer_r: float, axial: float, arc_deg: float) -> Part:
    """Annular wedge built by revolving a radial rectangle arc_deg around Z.

    Wedge starts at theta=0 and sweeps +arc_deg. Centered axially on z=0.
    """
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            with Locations(((inner_r + outer_r) / 2, 0)):
                Rectangle(outer_r - inner_r, axial)
        revolve(axis=Axis.Z, revolution_arc=arc_deg)
    return bp.part


def _male_tabs(p: LensMountParams) -> Part:
    """Three radial tabs hanging off the outside of the bayonet collar near its tip."""
    inner_r = p.bayonet_collar_dia / 2
    outer_r = inner_r + p.tab_radial_thick
    half = p.tab_arc_deg / 2
    # tab tip face = furthest -Z point of collar:
    collar_tip_z = -(p.flange_depth / 2 + p.bayonet_collar_len)
    tab_center_z = collar_tip_z + p.tab_axial_thick / 2
    tabs: list[Part] = []
    for i in range(p.n_tabs):
        center_deg = i * (360 / p.n_tabs)
        wedge = _wedge(inner_r, outer_r, p.tab_axial_thick, p.tab_arc_deg)
        rotated = wedge.rotate(Axis.Z, center_deg - half)
        positioned = rotated.locate(Location((0, 0, tab_center_z)))
        tabs.append(positioned)
    out = tabs[0]
    for t in tabs[1:]:
        out = out.fuse(t)
    return out


def _female_pass_slots(p: LensMountParams) -> Part:
    """Pass-through wedges (cut bodies) so male tabs slide axially into the
    female collar."""
    slot_arc = p.tab_arc_deg + p.slot_clearance_deg
    half = slot_arc / 2
    inner_r = p.bayonet_collar_dia / 2 - p.slot_clearance_mm
    outer_r = p.bayonet_collar_dia / 2 + p.tab_radial_thick + p.slot_clearance_mm
    axial = p.bayonet_collar_len + 2 * p.slot_clearance_mm
    z_center = -(p.flange_depth / 2 + p.bayonet_collar_len / 2)
    parts: list[Part] = []
    for i in range(p.n_tabs):
        center_deg = i * (360 / p.n_tabs)
        wedge = _wedge(inner_r, outer_r, axial, slot_arc)
        rotated = wedge.rotate(Axis.Z, center_deg - half)
        positioned = rotated.locate(Location((0, 0, z_center)))
        parts.append(positioned)
    out = parts[0]
    for w in parts[1:]:
        out = out.fuse(w)
    return out


def _female_back_channel(p: LensMountParams) -> Part:
    """Full circumferential channel at the back of the female collar that
    captures rotated tabs. Quarter-turn means male enters at slot, rotates 90
    deg, and the tab seats anywhere in this ring."""
    inner_r = p.bayonet_collar_dia / 2 - p.slot_clearance_mm
    outer_r = p.bayonet_collar_dia / 2 + p.tab_radial_thick + p.slot_clearance_mm
    axial = p.tab_axial_thick + 2 * p.channel_axial_clearance
    ring = _wedge(inner_r, outer_r, axial, 360)
    # Channel sits at the very back (most -Z) of the collar
    collar_tip_z = -(p.flange_depth / 2 + p.bayonet_collar_len)
    channel_center_z = collar_tip_z + axial / 2
    return ring.locate(Location((0, 0, channel_center_z)))


def _contact_pads(p: LensMountParams) -> Part:
    """Cylindrical bumps on the inner mating face (top of flange = +Z face)."""
    if p.n_contacts < 1:
        return Compound(children=[])
    if p.n_contacts == 1:
        positions = [(p.contact_radius_mm, 0)]
    else:
        arc = radians(p.contact_arc_deg)
        start = -arc / 2
        step = arc / (p.n_contacts - 1)
        positions = [
            (p.contact_radius_mm * cos(start + i * step),
             p.contact_radius_mm * sin(start + i * step))
            for i in range(p.n_contacts)
        ]
    z_center = p.flange_depth / 2 + p.contact_pad_height / 2
    pads: list[Part] = []
    for x, y in positions:
        c = Cylinder(radius=p.contact_pad_dia / 2, height=p.contact_pad_height)
        pads.append(c.locate(Location((x, y, z_center))))
    out = pads[0]
    for pad in pads[1:]:
        out = out.fuse(pad)
    return out


class LensMount:
    """Parametric humanoid-segment coupling, EF-bayonet inspired."""

    def __init__(
        self,
        side: Literal["male", "female"] = "male",
        params: LensMountParams | None = None,
    ):
        if side not in ("male", "female"):
            raise ValueError("side must be 'male' or 'female'")
        self.side = side
        self.params = params or LensMountParams()
        self._compound: Compound | None = None

    def build(self) -> Compound:
        if self._compound is not None:
            return self._compound
        p = self.params
        body = _flange_disc(p).fuse(_bayonet_collar(p))

        if self.side == "male":
            body = body.fuse(_male_tabs(p))
        else:
            body = body.cut(_female_pass_slots(p))
            body = body.cut(_female_back_channel(p))

        body = body.fuse(_contact_pads(p))
        result = Compound(label=f"lens_mount_{self.side}", children=[body])
        self._compound = result
        return result

    def export(self, out_dir: str) -> dict[str, str]:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        body = self.build()
        stl_path = out / f"lens_mount_{self.side}.stl"
        step_path = out / f"lens_mount_{self.side}.step"
        export_stl(body, str(stl_path))
        export_step(body, str(step_path))
        return {"stl": str(stl_path), "step": str(step_path)}
