# PathSnap API contract – FINAL v1.0

Agreed interface between the API (Laptop 1, owner Atharva) and the UI (Laptop 2, owner Tanish).
Machine-readable version: `api/schemas.py` (pydantic). Real example response: `ui/mock/predict_example.json`
(flagged `"mock": true`, generated from student_test trip 00000052 with a development stand-in classifier).
Changing anything below needs both owners to agree, a bump of `CONTRACT_VERSION`, and an update of this file.

## Decisions (so nobody has to ask)
| Topic | Decision |
|---|---|
| Server | FastAPI + uvicorn, port **8000**, bind `0.0.0.0`: `uvicorn api.main:app --host 0.0.0.0 --port 8000` |
| CORS | allow all origins (closed hotspot network, no credentials) |
| Trip ids | 8-digit strings exactly as folder names, e.g. `"00000015"` |
| Coordinates | **`[lat, lon]`** everywhere in responses (Leaflet order). Raw files are lon,lat; the API converts |
| Data location | env var `EVALUATOR_DATA` (default `../evaluator_data/evaluator_test`); trips = its sub-folders |
| Ground truth | `.route` files are read **server side only**, to compute metrics. Never in any response |
| Caching | static assets (model, graph code) may be loaded once at startup; **predictions are not cached** – every request runs the full pipeline and is logged |
| Performance target | largest trip (6,854 points) answers in under 30 s; the UI times out at 60 s |
| Logging | every request prints one line: `PREDICT trip=00000015 status=200 top1=0.9xx seconds=3.2` (plus uvicorn's access log). The evaluator is shown this terminal |
| Empty candidates | points with no candidate arc get arc id `-1`; they are skipped when drawing |
| JSON | UTF-8, floats rounded (metrics 4 dp, coordinates 6 dp) |

## Endpoints

### `GET /health`
```json
{"status": "ok", "contract_version": "1.0", "model": "lightgbm", "version": "a1b2c3d"}
```

### `GET /trips`
Exactly the reserved trips, no labels, no route info:
```json
[{"trip_id": "00000015", "n_points": 6854}, {"trip_id": "00000017", "n_points": 1346}]
```

### `POST /predict/{trip_id}`  (no body)
Runs the whole pipeline: load trip -> project -> candidates -> features -> classifier -> HMM -> score against the
server-side reference route. Response shape = `PredictResponse` in `api/schemas.py`:

| Field | Meaning |
|---|---|
| `gps` | `[lat, lon, t_seconds]` for every point, in order |
| `classifier_route`, `hmm_route` | `arc_ids` (consecutive repeats removed) and `segments`: list of connected polylines, each a list of `[lat, lon]` |
| `per_point.hmm_arc`, `.classifier_arc` | predicted arc id per GPS point (`-1` = none) |
| `metrics` | HMM `top1_accuracy`, `route_continuity`, `route_arc_f1`, plus `n_points`, `n_scored_points`, `candidate_miss_rate` |
| `metrics.classifier_only` | the same three metrics without the HMM (for the before/after view) |
| `timing` | `seconds` total, optional per-stage seconds |
| `model` | `name`, `version` of the classifier + code |
| `warnings` | human-readable notices; the UI must display them |
| `contract_version`, `mock` | `"1.0"`, and `true` only in the example files |

**Segments:** a new segment starts wherever consecutive predicted arcs are not head-to-tail connected, so a jump is
never drawn as a false straight line. The HMM route still has a few breaks (the vehicle can skip a whole short arc
between two 1-second samples; the reference routes show the same, about 1%). The UI may join consecutive segments of
the **HMM** route with a thin dashed line, but must leave the classifier-only route fragmented, because the
fragmentation is exactly what the HMM fixes.

**Warnings the API must raise:** if more than 20% of the trip's points are over 50 m from the reference route, add
`"reference route covers only part of the GPS track; accuracy for this trip is unreliable"` (this happens in the
training data, e.g. trip 00000054). Never hide such a trip and never alter the pipeline for it.

### Errors
`4xx/5xx` with `{"detail": "<readable message>", "code": "UNKNOWN_TRIP" | "PIPELINE_ERROR" | "BAD_REQUEST"}`.
Unknown trip -> 404. Any exception in the pipeline -> 500 with a message and a traceback in the API log, not in the response.

## Division of work on this contract
* **Atharva**: implement `api/main.py` returning exactly these models (`from api.schemas import ...`); use
  `pathsnap.route_geometry` (`collapse_arc_sequence`, `arcs_to_segments`) to build routes so the UI and the report
  maps draw identically; compute metrics with `pathsnap.hmm_eval.evaluate_routes` (on the HMM branch/main once merged).
* **Tanish**: build the UI against `ui/mock/predict_example.json` first, then switch to the real API; do not depend on
  any field not listed here.
* Both: run all ten trips end to end over the hotspot before the demo; save screenshots of the UI and of the API terminal.

## Hotspot setup (two laptops)
1. One person turns on Personal Hotspot (phone) and **both Macs join it**. Do not use venue Wi-Fi (client isolation).
2. Laptop 1: `ipconfig getifaddr en0` -> e.g. `172.20.10.2`. Start the API with `--host 0.0.0.0 --port 8000`.
3. Allow incoming connections for Python when macOS asks (System Settings -> Network -> Firewall if it was missed).
4. Laptop 2: open the UI, set API URL to `http://172.20.10.2:8000`, press **Test connection** (`/health`).
5. The hotspot also gives internet for the Leaflet CDN and map tiles; keep `ui/vendor/` copies as a fallback.
6. The IP can change if either machine reconnects: re-check before the demo.
