"""Turn a sequence of predicted arcs into map polylines.

Used by the API (and the Folium report maps) so every consumer draws routes identically.
"""
from __future__ import annotations

import numpy as np


def collapse_arc_sequence(per_point_arcs: np.ndarray) -> list[int]:
    """Per-point arc ids -> arc sequence with consecutive repeats removed; -1 (no candidate) skipped."""
    sequence: list[int] = []
    for arc in per_point_arcs.tolist():
        if arc >= 0 and (not sequence or sequence[-1] != arc):
            sequence.append(arc)
    return sequence


def arcs_to_segments(arc_sequence: list[int], arcs: np.ndarray,
                     node_lonlat: np.ndarray) -> list[list[list[float]]]:
    """Group the arc sequence into connected runs and return one [lat, lon] polyline per run.

    A new run starts wherever the end node of one arc is not the start node of the next, so a
    disconnected jump is never drawn as a false straight line. The number of runs minus one is the
    number of disconnected jumps.
    """
    segments: list[list[list[float]]] = []
    current: list[list[float]] = []
    previous_end = None
    for arc in arc_sequence:
        start_node, end_node = int(arcs[arc, 0]), int(arcs[arc, 1])
        if previous_end is None or start_node != previous_end:
            if current:
                segments.append(current)
            current = [_lat_lon(node_lonlat, start_node)]
        current.append(_lat_lon(node_lonlat, end_node))
        previous_end = end_node
    if current:
        segments.append(current)
    return segments


def _lat_lon(node_lonlat: np.ndarray, node: int) -> list[float]:
    lon, lat = node_lonlat[node]
    return [round(float(lat), 6), round(float(lon), 6)]
