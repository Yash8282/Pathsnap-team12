# Evaluator UI spec (Laptop 2) – owner: Tanish

The evaluator opens this page on Laptop 2, picks one of the ten trips, and sees the predicted route and the
accuracy computed by the API on Laptop 1. It must look clean, load fast, and never break in front of an evaluator.

## Hard rules (from the hackathon guidelines)
1. The UI only talks to the API. It never loads trip files, models or labels itself.
2. **Reference (ground-truth) routes are never sent to or shown in the UI.** Accuracy numbers come from the API.
3. Works for **all ten** trips, not one demo trip. No hardcoded outputs, no mocked data in the final version.
4. The API address is a setting, not hardcoded. Source code must match what is demonstrated.

## Stack (keep it simple, nothing to install on Laptop 2)
Single static page: `ui/index.html`, `ui/style.css`, `ui/app.js`, `ui/config.js`.
Map: **Leaflet** from a CDN (Folium is a Leaflet wrapper, so maps look consistent with the report). Plain JS `fetch`.
Run on Laptop 2:
```bash
cd ui && python3 -m http.server 8080       # open http://localhost:8080
```
Alternative if Tanish prefers Python: Streamlit + `streamlit-folium`. Decide once, and say so in the PR.

## Layout (desktop, laptop screen; must also not break at narrow widths)
```
+------------------------------------------------------------------------------+
| PathSnap · Team 12                       API: http://192.168.1.20:8000  ● online [Settings] |
+----------------------+-------------------------------------------------------+
| Trips (10)           |                                                       |
|  [ 00000015  6,854 ] |                     MAP (fills the area)              |
|  [ 00000017  1,346 ] |   layer toggles: GPS points / Classifier route /      |
|  [ 00000023    458 ] |                  HMM route / Road network (optional)  |
|  ...                 |                                                       |
|                      +-------------------------------------------------------+
| [ Run prediction ]   |  Results: Top-1  Continuity  Arc F1  | Classifier vs HMM |
|                      |  Points  Time taken  Model name     | request log       |
+----------------------+-------------------------------------------------------+
```

## Behaviour
* On load: call `GET /trips`, show the ten trips as selectable cards (id, number of GPS points). Show a clear
  empty/error state if the API is unreachable (see errors below).
* Select a trip -> **Run prediction** -> `POST /predict/{trip_id}`. While waiting: spinner, disabled button, live
  elapsed-seconds counter (big trips can take several seconds). Cancel via `AbortController` if the user picks
  another trip.
* On success: fit the map to the GPS bounds; draw layers (colours below); fill the results panel; append a line to the
  on-page request log (`time · trip · status · seconds`).
* Layers and colours (consistent with report maps; add a **legend** and a layer control):
  * GPS observations: small grey/blue dots (use canvas rendering, `L.map(..., {preferCanvas: true})`; for trips
    above about 3,000 points draw every n-th point so the page stays responsive, and say so in the legend)
  * Classifier-only route: thin orange line, shows disconnected jumps
  * **Classifier + HMM route: thick green line** (the final answer, on top)
  * Optional faint road-network context if the API provides it
* Hover/click a point: show index, time, and the predicted arc id.
* Results cards: top-1 accuracy, route continuity, route arc F1, number of points, and a small
  "classifier only -> + HMM" before/after comparison with the delta (green if improved, red if not; never hide a
  drop). Format as percentages with one decimal.
* Settings dialog: API base URL, saved in `localStorage`, plus a "Test connection" button that calls `GET /health`.

## API contract
The contract is **final and lives in `docs/API_CONTRACT.md`** (machine-readable: `api/schemas.py`; real example: `ui/mock/predict_example.json`).
Key points for the UI: coordinates are `[lat, lon]`; routes arrive as `segments` (list of polylines) - draw each
segment separately; the HMM route may be joined with a thin dashed line between segments, the classifier-only
route must stay fragmented; display every string in `warnings[]`.

## Error and edge states (each needs a visible, readable message)
API unreachable / CORS blocked -> banner "Cannot reach API at <url>" + Retry; timeout after 60 s; unknown trip;
empty `polyline`; a trip with no candidates for some points (API may return `-1`; ignore those in drawing);
double-click on Run (ignore while a request is in flight).

## Design checklist ("good UI")
* One clear primary action; big readable text (projected on a screen); high-contrast colours; same palette as the
  report figures. Light theme is enough; dark is a bonus.
* No layout jump while loading; metrics have units/labels; numbers align.
* Keyboard accessible buttons, visible focus, `aria-live` region for loading/error text.
* No console errors; no third-party calls except the Leaflet CDN and map tiles (OpenStreetMap, with attribution).
  Cache the Leaflet files locally under `ui/vendor/` as a fallback if the venue Wi-Fi is bad.

## Working before the API exists
Start against the static `ui/mock/predict_example.json` and `ui/mock/trips_example.json` (already in the repo; `fetch` them), clearly named
`mock`, and **remove the mock switch from the demo build**. Switch to Atharva's real API as soon as `/trips` and
`/predict` exist.

## Running across two laptops (do this test early, not on demo day)
1. Both laptops on the **phone hotspot** (decided). Venue Wi-Fi often isolates clients. Full steps: `docs/API_CONTRACT.md`.
2. On Laptop 1 (Mac): `ipconfig getifaddr en0` gives the IP. API must bind `0.0.0.0` and enable CORS for the UI origin.
3. macOS firewall may prompt to allow incoming connections for Python: allow it.
4. On Laptop 2 open the UI, set the API URL to `http://<laptop1-ip>:8000`, press Test connection.
5. Run all ten trips end to end, and keep the API terminal visible: the evaluator wants to see the request logs.

## Definition of done
- [ ] All ten trips selectable and run successfully through the real API
- [ ] Map shows GPS, classifier-only route and HMM route with legend and layer control
- [ ] Metrics and before/after comparison displayed; warnings displayed
- [ ] Error states tested by stopping the API mid-session
- [ ] API URL configurable; works across two machines
- [ ] Screenshots of the UI and of the API terminal logs saved for the report (section 7)
- [ ] README section "Run the UI" written; no secrets in the repo

## Git workflow
Branch `feat/ui`, small commits under your own identity (`feat(ui): add trip list and map layers`,
`feat(ui): add results panel`, `fix(ui): handle API timeout`), PR into `main`.
