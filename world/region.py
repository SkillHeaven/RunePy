from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

import numpy as np
import gzip

from constants import REGION_SIZE

try:
    from panda3d.core import (
        GeomVertexFormat,
        GeomVertexData,
        GeomVertexWriter,
        GeomTriangles,
        Geom,
        GeomNode,
        NodePath,
    )
except Exception:  # pragma: no cover - Panda3D may be missing during tests
    GeomVertexFormat = GeomVertexData = GeomVertexWriter = None
    GeomTriangles = Geom = GeomNode = NodePath = None


@dataclass
class Region:
    """Container for region tile data."""

    rx: int
    ry: int
    height: np.ndarray
    base: np.ndarray
    overlay: np.ndarray
    flags: np.ndarray
    node: NodePath | None = None

    FILE_VERSION: ClassVar[int] = 1

    # ------------------------------------------------------------------
    # Loading / Saving helpers
    # ------------------------------------------------------------------
    @classmethod
    def load(cls, rx: int, ry: int) -> "Region":
        """Load region ``(rx, ry)`` from disk or create a new one."""
        path = Path("maps") / f"region_{rx}_{ry}.bin"
        size = REGION_SIZE * REGION_SIZE
        if path.exists():
            with gzip.open(path, "rb") as f:
                version = int.from_bytes(f.read(2), "little")
                if version != cls.FILE_VERSION:
                    raise ValueError(f"Unsupported region version {version}")
                height = np.frombuffer(f.read(size * 2), dtype=np.int16).reshape(REGION_SIZE, REGION_SIZE).copy()
                base = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
                overlay = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
                flags = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
        else:
            height = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.int16)
            base = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
            overlay = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
            flags = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
        return cls(rx, ry, height, base, overlay, flags)

    def save(self) -> None:
        """Write this region back to disk."""
        path = Path("maps") / f"region_{self.rx}_{self.ry}.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wb") as f:
            f.write(self.FILE_VERSION.to_bytes(2, "little"))
            f.write(self.height.astype(np.int16).tobytes())
            f.write(self.base.astype(np.uint8).tobytes())
            f.write(self.overlay.astype(np.uint8).tobytes())
            f.write(self.flags.astype(np.uint8).tobytes())

    # ------------------------------------------------------------------
    # Mesh generation
    # ------------------------------------------------------------------
    def make_mesh(self) -> NodePath | None:
        """Create or refresh a mesh for this region."""
        if GeomVertexFormat is None:
            return None
        # Remove previous mesh if present
        if self.node is not None:
            self.node.removeNode()
            self.node = None
        format = GeomVertexFormat.get_v3()
        vdata = GeomVertexData("region", format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        tris = GeomTriangles(Geom.UHStatic)
        index = 0
        for y in range(REGION_SIZE):
            for x in range(REGION_SIZE):
                z = float(self.height[y, x])
                vertex.addData3(x, y, z)
                vertex.addData3(x + 1, y, z)
                vertex.addData3(x + 1, y + 1, z)
                vertex.addData3(x, y + 1, z)
                tris.addVertices(index, index + 1, index + 2)
                tris.addVertices(index, index + 2, index + 3)
                index += 4
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode("region")
        node.addGeom(geom)
        self.node = NodePath(node)
        return self.node
