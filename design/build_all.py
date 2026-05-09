"""Build every parametric part and write artifacts to design/build/.

Run from repo root:  python -m design.build_all
Or directly:         python Z:/_research/embodied/design/build_all.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Allow direct invocation without -m
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(THIS_DIR.parent))

from design.lens_mount import LensMount  # noqa: E402

OUT_DIR = THIS_DIR / "build"


def _human_size(n: int) -> str:
    for unit in ("B", "KiB", "MiB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024  # type: ignore[assignment]
    return f"{n:.1f} GiB"


def _try_render_preview(out_path: Path) -> bool:
    """Attempt a 3D matplotlib preview from the male STL. Best-effort."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        import trimesh

        male_stl = OUT_DIR / "lens_mount_male.stl"
        female_stl = OUT_DIR / "lens_mount_female.stl"
        meshes = []
        for p in (male_stl, female_stl):
            if p.exists():
                meshes.append((p.stem, trimesh.load(str(p))))

        fig = plt.figure(figsize=(10, 5))
        for i, (name, mesh) in enumerate(meshes):
            ax = fig.add_subplot(1, len(meshes), i + 1, projection="3d")
            tris = mesh.vertices[mesh.faces]
            coll = Poly3DCollection(
                tris, alpha=0.6, edgecolor="k", linewidth=0.05, facecolor="#888888"
            )
            ax.add_collection3d(coll)
            mn, mx = mesh.bounds
            ax.set_xlim(mn[0], mx[0])
            ax.set_ylim(mn[1], mx[1])
            ax.set_zlim(mn[2], mx[2])
            ax.set_title(name)
            ax.set_box_aspect((mx - mn).tolist())
        plt.tight_layout()
        plt.savefig(out_path, dpi=120)
        plt.close(fig)
        return True
    except Exception as exc:  # pragma: no cover
        print(f"[preview] skipped: {exc!r}")
        return False


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    artifacts: list[Path] = []
    for side in ("male", "female"):
        t0 = time.perf_counter()
        mount = LensMount(side=side)
        out = mount.export(str(OUT_DIR))
        dt = time.perf_counter() - t0
        for kind, p in out.items():
            path = Path(p)
            artifacts.append(path)
            print(f"[build] {side:6s} {kind:4s} {path.name:32s} "
                  f"{_human_size(path.stat().st_size):>10s}  ({dt:.2f}s total for side)")

    preview = OUT_DIR / "lens_mount_preview.png"
    if _try_render_preview(preview):
        artifacts.append(preview)
        print(f"[build] preview      {preview.name:32s} "
              f"{_human_size(preview.stat().st_size):>10s}")

    print()
    print(f"wrote {len(artifacts)} artifact(s) to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
