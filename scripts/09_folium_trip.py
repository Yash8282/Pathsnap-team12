"""Interactive Folium map of one trip: GPS points, nearby road network, reference route, candidate arcs.

Usage: python scripts/09_folium_trip.py <partition> <trip_id>     e.g. student_test 00000052
Writes results/maps/<partition>_<trip_id>.html. Uses candidate arcs from data/features_<partition>.parquet
(run scripts/03_build_dataset.py first). Reference route is shown for development partitions only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import folium
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pathsnap.data import load_trip  # noqa: E402
from pathsnap.route_geometry import arcs_to_segments  # noqa: E402


def main(partition: str, trip_id: str) -> None:
    trip = load_trip(trip_id, partition)
    pairs = pd.read_parquet(ROOT / "data" / f"features_{partition}.parquet", filters=[("trip_id", "==", trip_id)])
    candidate_arcs = np.unique(pairs.arc_id.to_numpy())
    lat_lon = trip.track_lonlat[:, ::-1]
    fmap = folium.Map(location=lat_lon.mean(axis=0).tolist(), zoom_start=16, tiles="OpenStreetMap")
    fmap.fit_bounds([lat_lon.min(axis=0).tolist(), lat_lon.max(axis=0).tolist()])

    network = folium.FeatureGroup(name=f"Road network near track ({len(candidate_arcs)} arcs within 100 m)", show=True)
    for start, end in trip.arcs[candidate_arcs]:
        folium.PolyLine([trip.node_lonlat[start][::-1].tolist(), trip.node_lonlat[end][::-1].tolist()],
                        color="#7f8c8d", weight=2, opacity=0.7).add_to(network)
    network.add_to(fmap)

    reference = folium.FeatureGroup(name="Reference route (derived from .route)", show=True)
    for segment in arcs_to_segments(trip.route.tolist(), trip.arcs, trip.node_lonlat):
        folium.PolyLine(segment, color="#27ae60", weight=6, opacity=0.8).add_to(reference)
    reference.add_to(fmap)

    gps = folium.FeatureGroup(name="Raw GPS observations", show=True)
    folium.PolyLine(lat_lon.tolist(), color="#2980b9", weight=1, opacity=0.5).add_to(gps)
    for index in range(0, len(lat_lon), max(1, len(lat_lon) // 400)):
        folium.CircleMarker(lat_lon[index].tolist(), radius=3, color="#1f4e79", fill=True, fill_opacity=0.9,
                            tooltip=f"point {index}, t={trip.timestamps[index]:.0f}s").add_to(gps)
    gps.add_to(fmap)

    legend = ("<div style='position:fixed;bottom:25px;left:25px;z-index:9999;background:white;padding:8px 10px;"
              "border:1px solid #999;font-size:12px'><b>Trip %s (%s)</b><br>"
              "<span style='color:#1f4e79'>&#9679;</span> raw GPS points<br>"
              "<span style='color:#27ae60'>&#9644;</span> reference route<br>"
              "<span style='color:#7f8c8d'>&#9644;</span> road network (candidate arcs)</div>" % (trip_id, partition))
    fmap.get_root().html.add_child(folium.Element(legend))
    folium.LayerControl(collapsed=False).add_to(fmap)
    out = ROOT / "results" / "maps" / f"{partition}_{trip_id}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    fmap.save(str(out))
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB), {len(trip.timestamps)} GPS points, {len(trip.route)} route arcs")


if __name__ == "__main__":
    main(*sys.argv[1:3])
