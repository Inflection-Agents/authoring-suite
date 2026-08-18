#!/usr/bin/env python3
"""Measure a diagram's geometry. Run this on what you just drew, before you ship it.

Every check here exists because the property is invisible in the source and obvious on
screen. A diagram's markup can be well-formed, its numbers plausible and its labels
correct, while a label sits on top of the connector it names. Reading the file cannot
catch that. Measuring it can, and SKILL.md §9 asks for this checker's output rather than
a self-assessment for exactly that reason.

Checks that run by default
--------------------------
clipped-mask   A label mask covered by a node painted after it (§6 rule 6, ADR 0005).
               Paint order is the criterion, not overlap: a mask over an earlier-painted
               zone stays on top and is legal; one over a later node is clipped into a
               fragment on the node's border.
masked-edge    A label mask sitting ON the connector it names, rather than the 6-10px
               clear that §6 rule 2 requires. ADR 0005 deferred this check for needing
               stroke geometry rather than rectangles; this is that geometry.
broken-out     A node whose centre is inside a container but whose body is not.

Checks that are opt-in, and why
-------------------------------
corner-landing A connector meeting a box within 20-80% of an edge when it is the only
               one there, or clearing a corner by 12px when several fan across it
               (§6 rule 4).
loose-start    A connector that begins in open canvas. Resizing a box silently orphans
               every arrow drawn from it, so the arrow stays correct at the end a
               reader checks and floats at the end they do not.

Both need to decide what counts as a node, and across the 32 types that judgement is not
reliable from shape alone. Several types legitimately anchor a connector beside an icon
or a text label rather than on a shape's edge (`high-level`'s source column, `datalake`'s
staggered entries), and a rect-shaped heuristic reads those as errors. They are exact for
diagrams whose bodies are all real shapes with edges, which is the common case for a
generated set, so they ship enabled by request rather than by default:

    python3 verify_geometry.py diagram.html --also corner-landing,loose-start

What this cannot check
----------------------
Text advance is not measurable from source without font metrics, so a name that overruns
its box is not caught here. Render the file and let the browser measure it; SKILL.md §9
carries the console snippet.

Usage
-----
    python3 verify_geometry.py diagram.html
    python3 verify_geometry.py a.html b.html --also loose-start
    python3 verify_geometry.py --only masked-edge diagram.html
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

# ── Shape heuristics, matched to the shipped templates ──────────────────────────────
NODE_MIN_W, NODE_MIN_H = 60.0, 40.0
MASK_MIN_W, MASK_MAX_W = 20.0, 120.0
MASK_MIN_H, MASK_MAX_H = 8.0, 14.0
CONTAINER_MIN_W, CONTAINER_MIN_H = 160.0, 120.0
SHAPE_MIN = 12.0
EPSILON = 0.5

# §6 rule 2 asks for 6-10px of clearance. Flagging below 4px reports a label that is
# genuinely on its stroke without arguing about the last two pixels of a 6px target.
MASK_CLEARANCE = 4.0
SAMPLE_STEP = 3.0

# An arrowhead stops short of its target by the marker's refX, so "aimed at" is a
# proximity test rather than an equality one.
AIMED_AT = 48.0
EDGE_MIN_FRAC, EDGE_MAX_FRAC = 0.2, 0.8
CORNER_CLEARANCE = 12.0
FAN_SEPARATION = 12.0

DEFAULT_CHECKS = ("clipped-mask", "masked-edge", "broken-out")
OPTIONAL_CHECKS = ("corner-landing", "loose-start")
ALL_CHECKS = DEFAULT_CHECKS + OPTIONAL_CHECKS

SVG_NUM = r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?"
SVG_RE = re.compile(r"<svg\b.*?</svg>", re.IGNORECASE | re.DOTALL)
RECT_RE = re.compile(
    r"<rect\b(?P<attrs>[^>]*?\bx=\"(?P<x>" + SVG_NUM + r")\"\s+y=\"(?P<y>" + SVG_NUM
    + r")\"\s+width=\"(?P<w>" + SVG_NUM + r")\"\s+height=\"(?P<h>" + SVG_NUM + r")\"[^>]*)",
    re.IGNORECASE,
)
PATH_RE = re.compile(r"<path\b(?P<attrs>[^>]*)>", re.IGNORECASE)
D_RE = re.compile(r"\bd=\"([^\"]*)\"", re.IGNORECASE)
CIRCLE_RE = re.compile(
    r"<circle\b[^>]*?\bcx=\"(?P<cx>" + SVG_NUM + r")\"[^>]*?\bcy=\"(?P<cy>" + SVG_NUM
    + r")\"[^>]*?\br=\"(?P<r>" + SVG_NUM + r")\"", re.IGNORECASE)
ELLIPSE_RE = re.compile(
    r"<ellipse\b[^>]*?\bcx=\"(?P<cx>" + SVG_NUM + r")\"[^>]*?\bcy=\"(?P<cy>" + SVG_NUM
    + r")\"[^>]*?\brx=\"(?P<rx>" + SVG_NUM + r")\"[^>]*?\bry=\"(?P<ry>" + SVG_NUM + r")\"",
    re.IGNORECASE)
POLY_RE = re.compile(r"<polygon\b[^>]*?\bpoints=\"(?P<pts>[^\"]+)\"", re.IGNORECASE)
NUM_RE = re.compile(SVG_NUM)
TOKEN_RE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])|(" + SVG_NUM + r")")

# Operand counts per command. A curve's endpoint is exact even though its interior is
# not reconstructed, and no check here inspects a curve's interior.
ARITY = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7}


class Box:
    __slots__ = ("x", "y", "w", "h", "line", "offset", "drawn")

    def __init__(self, x, y, w, h, line, offset, drawn=True):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.line, self.offset = line, offset
        # Whether the rect is a drawn body rather than background. Every node in this
        # design system carries a stroke or a styling class; a full-bleed paper rect or a
        # faint lane band carries neither, and treating one as a node makes a connector
        # crossing it look like a corner landing.
        self.drawn = drawn

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h

    def __repr__(self):
        return f"({self.x:g},{self.y:g} {self.w:g}x{self.h:g})"


def path_points(d: str) -> list[tuple[float, float]]:
    """Every on-curve point of a path, in order, curves flattened to their endpoints."""
    seq: list[tuple[str, object]] = []
    for cmd, num in TOKEN_RE.findall(d):
        seq.append(("cmd", cmd) if cmd else ("num", float(num)))

    pts: list[tuple[float, float]] = []
    x = y = start_x = start_y = 0.0
    cmd = None
    i = 0
    while i < len(seq):
        kind, value = seq[i]
        if kind == "cmd":
            cmd = str(value)
            i += 1
            if cmd in "Zz":
                x, y = start_x, start_y
                pts.append((x, y))
            continue
        if cmd is None:
            i += 1
            continue
        need = ARITY.get(cmd.upper(), 2)
        args: list[float] = []
        while len(args) < need and i < len(seq) and seq[i][0] == "num":
            args.append(float(seq[i][1]))  # type: ignore[arg-type]
            i += 1
        if len(args) < need:
            break
        rel, upper = cmd.islower(), cmd.upper()
        if upper in ("M", "L", "T"):
            nx, ny = args[0], args[1]
        elif upper == "H":
            nx, ny = args[0], (0.0 if rel else y)
        elif upper == "V":
            nx, ny = (0.0 if rel else x), args[0]
        elif upper == "C":
            nx, ny = args[4], args[5]
        elif upper in ("S", "Q"):
            nx, ny = args[2], args[3]
        else:  # A
            nx, ny = args[5], args[6]
        if rel:
            nx, ny = x + nx, y + ny
        if upper == "M":
            start_x, start_y = nx, ny
            # A second coordinate pair after M is an implicit lineto.
            cmd = "l" if rel else "L"
        x, y = nx, ny
        pts.append((x, y))
    return pts


def parse_rects(svg: str, base_line: int) -> list[Box]:
    out = []
    for m in RECT_RE.finditer(svg):
        attrs = m.group("attrs")
        out.append(Box(
            float(m.group("x")), float(m.group("y")),
            float(m.group("w")), float(m.group("h")),
            base_line + svg.count("\n", 0, m.start()), m.start(),
            drawn="stroke=" in attrs or "class=" in attrs,
        ))
    return out


def parse_shapes(svg: str, base_line: int) -> list[Box]:
    """Bounding boxes for bodies drawn as something other than a rect.

    The 32 types do not agree on a primitive: `high-level` uses polygon chevrons, `venn`
    uses circles, several draw their bodies as closed paths. A rect-only reader calls all
    of those open canvas, which is how a checker ends up reporting dozens of findings
    against examples that are correct.
    """
    out: list[Box] = []

    def add(x, y, w, h, start):
        out.append(Box(x, y, w, h, base_line + svg.count("\n", 0, start), start))

    for m in CIRCLE_RE.finditer(svg):
        cx, cy, r = (float(m.group(k)) for k in ("cx", "cy", "r"))
        add(cx - r, cy - r, 2 * r, 2 * r, m.start())
    for m in ELLIPSE_RE.finditer(svg):
        cx, cy, rx, ry = (float(m.group(k)) for k in ("cx", "cy", "rx", "ry"))
        add(cx - rx, cy - ry, 2 * rx, 2 * ry, m.start())
    for m in POLY_RE.finditer(svg):
        vals = [float(v) for v in NUM_RE.findall(m.group("pts"))]
        xs, ys = vals[0::2], vals[1::2]
        if xs and ys:
            add(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), m.start())
    for m in PATH_RE.finditer(svg):
        attrs = m.group("attrs")
        if "marker-end" in attrs or "marker-start" in attrs:
            continue  # a connector, not a body
        found = D_RE.search(attrs)
        if not found:
            continue
        pts = path_points(found.group(1))
        if len(pts) < 3:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        add(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), m.start())
    return out


def parse_connectors(svg: str, base_line: int):
    out = []
    for m in PATH_RE.finditer(svg):
        attrs = m.group("attrs")
        if "marker-end" not in attrs and "marker-start" not in attrs:
            continue
        found = D_RE.search(attrs)
        if not found:
            continue
        pts = path_points(found.group(1))
        if len(pts) >= 2:
            out.append((pts, base_line + svg.count("\n", 0, m.start())))
    return out


def dist_to_box(px: float, py: float, b: Box) -> float:
    return math.hypot(max(b.x - px, 0.0, px - b.right), max(b.y - py, 0.0, py - b.bottom))


def edge_landing(px: float, py: float, b: Box):
    """Which edge the point meets and how far along it, as a fraction.

    Deciding by "is it left/right or top/bottom" is ambiguous exactly when the point
    lands on a boundary, which is the common case, so every edge is measured and the
    nearest one whose fraction falls on the edge wins.
    """
    edges = [
        (abs(px - b.x), (py - b.y) / b.h, "left"),
        (abs(px - b.right), (py - b.y) / b.h, "right"),
        (abs(py - b.y), (px - b.x) / b.w, "top"),
        (abs(py - b.bottom), (px - b.x) / b.w, "bottom"),
    ]
    on_span = [e for e in edges if 0.0 <= e[1] <= 1.0]
    return min(on_span or edges, key=lambda e: e[0]), bool(on_span)


def segment_enters(p, q, b: Box) -> bool:
    n = max(2, int(math.dist(p, q) / SAMPLE_STEP))
    for i in range(n + 1):
        t = i / n
        sx, sy = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        if (b.x - MASK_CLEARANCE < sx < b.right + MASK_CLEARANCE
                and b.y - MASK_CLEARANCE < sy < b.bottom + MASK_CLEARANCE):
            return True
    return False


def check_svg(svg: str, base_line: int, name: str, enabled: set[str]) -> list[str]:
    rects = parse_rects(svg, base_line)
    nodes = [r for r in rects if r.w >= NODE_MIN_W and r.h >= NODE_MIN_H and r.drawn]
    masks = [r for r in rects
             if MASK_MIN_W <= r.w <= MASK_MAX_W and MASK_MIN_H <= r.h <= MASK_MAX_H]
    containers = [r for r in rects
                  if r.w >= CONTAINER_MIN_W and r.h >= CONTAINER_MIN_H]
    shapes = [s for s in parse_shapes(svg, base_line)
              if s.w >= SHAPE_MIN and s.h >= SHAPE_MIN]
    connectors = parse_connectors(svg, base_line)
    out: list[str] = []

    if "clipped-mask" in enabled:
        for mask in masks:
            for node in nodes:
                if node.offset <= mask.offset:
                    continue  # painted before the label; the label stays on top
                dx = min(mask.right, node.right) - max(mask.x, node.x)
                dy = min(mask.bottom, node.bottom) - max(mask.y, node.y)
                inside = (mask.x >= node.x - EPSILON and mask.y >= node.y - EPSILON
                          and mask.right <= node.right + EPSILON
                          and mask.bottom <= node.bottom + EPSILON)
                if dx <= 1.0 or dy <= 1.0 or inside:
                    continue  # a mask fully inside a node is a badge chip
                out.append(
                    f"{name}:{mask.line}: [clipped-mask] label mask {mask} is clipped by "
                    f"node {node} declared later at line {node.line} "
                    f"(overlap {dx:g}x{dy:g}px) - move the label onto a free segment of "
                    f"its connector")
                break

    if "masked-edge" in enabled:
        for mask in masks:
            hit = None
            for pts, line in connectors:
                for a, b in zip(pts, pts[1:]):
                    if segment_enters(a, b, mask):
                        hit = line
                        break
                if hit is not None:
                    break
            if hit is not None:
                out.append(
                    f"{name}:{mask.line}: [masked-edge] label mask {mask} sits on the "
                    f"connector at line {hit}; SKILL.md §6 rule 2 keeps a label 6-10px "
                    f"clear of its own stroke, so the connector stays visible")

    if "loose-start" in enabled:
        anchors = nodes + containers + shapes
        for pts, line in connectors:
            px, py = pts[0]
            anchored = any(
                ((abs(px - b.x) <= 3 or abs(px - b.right) <= 3)
                 and b.y - 3 <= py <= b.bottom + 3)
                or ((abs(py - b.y) <= 3 or abs(py - b.bottom) <= 3)
                    and b.x - 3 <= px <= b.right + 3)
                for b in anchors
            )
            if not anchored:
                out.append(
                    f"{name}:{line}: [loose-start] connector starts at ({px:g},{py:g}), "
                    f"on the edge of no node, container or shape: it begins in open canvas")

    if "corner-landing" in enabled:
        landable = [n for n in nodes + shapes
                    if not (n.w >= CONTAINER_MIN_W and n.h >= CONTAINER_MIN_H)]
        landings: dict = {}
        for pts, line in connectors:
            px, py = pts[-1]
            near = [b for b in landable if dist_to_box(px, py, b) <= AIMED_AT]
            if not near:
                continue
            box = min(near, key=lambda b: dist_to_box(px, py, b))
            (_, frac, edge), landed = edge_landing(px, py, box)
            if not landed:
                out.append(
                    f"{name}:{line}: [corner-landing] connector ends at ({px:g},{py:g}), "
                    f"beside node {box} but on none of its edges: the arrow misses the box")
                continue
            landings.setdefault((id(box), edge), []).append((frac, box, line))
        for (_, edge), hits in landings.items():
            span = hits[0][1].h if edge in ("left", "right") else hits[0][1].w
            if len(hits) == 1:
                frac, box, line = hits[0]
                if not EDGE_MIN_FRAC <= frac <= EDGE_MAX_FRAC:
                    out.append(
                        f"{name}:{line}: [corner-landing] the only connector on node "
                        f"{box}'s {edge} edge meets it at {frac:.0%}; a sole connector "
                        f"lands between 20% and 80%, not on a corner")
                continue
            for frac, box, line in hits:
                offset = frac * span
                # Report the distance to the NEAREST corner. Reporting the offset from the
                # edge's start called an 8px violation "60px from a corner", which reads as
                # a non-issue and is how a real defect gets waved through.
                nearest = min(offset, span - offset)
                if nearest < CORNER_CLEARANCE:
                    out.append(
                        f"{name}:{line}: [corner-landing] connector meets node {box}'s "
                        f"{edge} edge {nearest:.0f}px from the nearest corner; fanned "
                        f"connectors still clear a corner by {CORNER_CLEARANCE:g}px")
            ordered = sorted(h[0] * span for h in hits)
            for a, b in zip(ordered, ordered[1:]):
                if b - a < FAN_SEPARATION:
                    out.append(
                        f"{name}:{hits[0][2]}: [corner-landing] two connectors on node "
                        f"{hits[0][1]}'s {edge} edge are {b - a:.0f}px apart; fan them by "
                        f"at least {FAN_SEPARATION:g}px (SKILL.md §6 rule 4)")

    if "broken-out" in enabled:
        for node in nodes:
            cx, cy = node.x + node.w / 2, node.y + node.h / 2
            for c in containers:
                if c is node or (c.w <= node.w and c.h <= node.h):
                    continue
                if not (c.x <= cx <= c.right and c.y <= cy <= c.bottom):
                    continue
                if (node.x < c.x - EPSILON or node.y < c.y - EPSILON
                        or node.right > c.right + EPSILON
                        or node.bottom > c.bottom + EPSILON):
                    out.append(
                        f"{name}:{node.line}: [broken-out] node {node} breaks out of "
                        f"container {c} that holds its centre")
                break
    return out


def check(path: Path, enabled=None) -> list[str]:
    enabled = set(enabled) if enabled else set(DEFAULT_CHECKS)
    source = path.read_text(encoding="utf-8")
    findings: list[str] = []
    for m in SVG_RE.finditer(source):
        findings.extend(
            check_svg(m.group(0), source.count("\n", 0, m.start()) + 1, path.name, enabled)
        )
    return findings


def resolve_checks(only: str | None, also: str | None, parser) -> set[str]:
    if only:
        enabled = {c.strip() for c in only.split(",") if c.strip()}
    else:
        enabled = set(DEFAULT_CHECKS)
        if also:
            enabled |= {c.strip() for c in also.split(",") if c.strip()}
    unknown = enabled - set(ALL_CHECKS)
    if unknown:
        parser.error(f"unknown check(s): {', '.join(sorted(unknown))}. "
                     f"Available: {', '.join(ALL_CHECKS)}")
    return enabled


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", help="diagram HTML files to measure")
    parser.add_argument("--only", help="run exactly these checks, comma-separated")
    parser.add_argument("--also", help="add optional checks to the default set")
    args = parser.parse_args()
    enabled = resolve_checks(args.only, args.also, parser)

    findings: list[str] = []
    paths = [Path(f) for f in args.files]
    for path in paths:
        if not path.exists():
            findings.append(f"{path}: file not found")
            continue
        findings.extend(check(path, enabled))

    for finding in findings:
        print(finding)
    print(f"Summary: {len(paths)} file(s) checked, {len(findings)} finding(s), "
          f"checks: {', '.join(sorted(enabled))}.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
