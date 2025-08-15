from __future__ import annotations

import gzip
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Tuple

import numpy as np
from runepy.paths import MAPS_DIR

from constants import REGION_SIZE

try:
    from panda3d.core import (
        Geom,
        GeomNode,
        GeomTriangles,
        GeomVertexData,
        GeomVertexFormat,
        GeomVertexWriter,
        NodePath,
    )
except Exception:  # pragma: no cover - Panda3D may be missing during tests
    Geom = GeomNode = GeomTriangles = None
    GeomVertexData = GeomVertexFormat = GeomVertexWriter = None
    NodePath = None

logger = logging.getLogger(__name__)
LOAD_TIMES: Dict[Tuple[int, int], List[float]] = defaultdict(list)


def world_to_region(x: int, y: int) -> Tuple[int, int]:
    """Return ``(rx, ry)`` region coordinates for world position ``(x, y)``."""
    return x // REGION_SIZE, y // REGION_SIZE


def local_tile(x: int, y: int) -> Tuple[int, int]:
    """Return local tile indices within a region for world position ``(x, y)``."""
    return x % REGION_SIZE, y % REGION_SIZE


@dataclass
class Region:
    """Container for region tile data."""

    rx: int
    ry: int
    height: np.ndarray
    base: np.ndarray
    overlay: np.ndarray
    flags: np.ndarray
    textures: np.ndarray
    node: "NodePath" | None = None

    FILE_VERSION: ClassVar[int] = 2

    @classmethod
    def load(cls, rx: int, ry: int) -> "Region":
        """Load region ``(rx, ry)`` from disk or create a new one."""
        start = time.perf_counter()
        path = MAPS_DIR / f"region_{rx}_{ry}.bin"
        size = REGION_SIZE * REGION_SIZE
        texels = 16 * 16
        if path.exists():
            with gzip.open(path, "rb") as f:
                version = int.from_bytes(f.read(2), "little")
                if version not in {1, cls.FILE_VERSION}:
                    raise ValueError(f"Unsupported region version {version}")
                height = np.frombuffer(f.read(size * 2), dtype=np.int16).reshape(REGION_SIZE, REGION_SIZE).copy()
                base = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
                overlay = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
                flags = np.frombuffer(f.read(size), dtype=np.uint8).reshape(REGION_SIZE, REGION_SIZE).copy()
                if version >= 2:
                    textures = np.frombuffer(
                        f.read(size * texels), dtype=np.uint8
                    ).reshape(REGION_SIZE, REGION_SIZE, 16, 16).copy()
                else:
                    textures = np.zeros((REGION_SIZE, REGION_SIZE, 16, 16), dtype=np.uint8)
        else:
            height = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.int16)
            base = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
            overlay = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
            flags = np.zeros((REGION_SIZE, REGION_SIZE), dtype=np.uint8)
            textures = np.zeros((REGION_SIZE, REGION_SIZE, 16, 16), dtype=np.uint8)
        region = cls(rx, ry, height, base, overlay, flags, textures)
        duration = time.perf_counter() - start
        LOAD_TIMES[(rx, ry)].append(duration)
        logger.debug(
            "Loaded region (%s, %s) in %.6f s (access #%d)",
            rx,
            ry,
            duration,
            len(LOAD_TIMES[(rx, ry)]),
        )
        return region

    def save(self) -> None:
        """Write this region back to disk."""
        path = MAPS_DIR / f"region_{self.rx}_{self.ry}.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wb") as f:
            f.write(self.FILE_VERSION.to_bytes(2, "little"))
            f.write(self.height.astype(np.int16).tobytes())
            f.write(self.base.astype(np.uint8).tobytes())
            f.write(self.overlay.astype(np.uint8).tobytes())
            f.write(self.flags.astype(np.uint8).tobytes())
            f.write(self.textures.astype(np.uint8).tobytes())

    def make_mesh(self):
        """Create or refresh a mesh for this region."""
        if GeomVertexFormat is None:
            return None
        if self.node is not None:
            self.node.removeNode()
            self.node = None
        format = GeomVertexFormat.get_v3cp()
        vdata = GeomVertexData("region", format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")
        color = GeomVertexWriter(vdata, "color")
        tris = GeomTriangles(Geom.UHStatic)
        index = 0
        for y in range(REGION_SIZE):
            for x in range(REGION_SIZE):
                z = float(self.height[y, x])
                val = int(self.overlay[y, x]) or int(self.base[y, x])
                if val:
                    shade = val / 255.0
                    col = (shade, shade, shade, 1.0)
                else:
                    col = (0.2, 0.2, 0.2, 1.0)
                vertex.addData3(x, y, z)
                color.addData4f(*col)
                vertex.addData3(x + 1, y, z)
                color.addData4f(*col)
                vertex.addData3(x + 1, y + 1, z)
                color.addData4f(*col)
                vertex.addData3(x, y + 1, z)
                color.addData4f(*col)
                tris.addVertices(index, index + 1, index + 2)
                tris.addVertices(index, index + 2, index + 3)
                index += 4
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode("region")
        node.addGeom(geom)
        self.node = NodePath(node)
        return self.node
