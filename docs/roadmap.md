# Roadmap — 6-week plan (status: **in progress**, nothing below is completed unless ticked)

| Week | Goals | Deliverables | Done |
|---|---|---|---|
| 1 | Choose catchment; check observed-flow availability; scaffold repo/environment; set up Earth Engine | Catchment decision note; working env; `data/README` filled | [ ] |
| 2 | Pull CHIRPS, DEM, land cover; delineate catchment; build aligned daily dataset | `src/data/*`; processed daily table; data QC notebook | [ ] |
| 3 | Implement SCS-CN baseline; define metrics (RMSE/NSE/KGE) and split protocol | `src/baseline/scs_cn.py`; `src/evaluation/metrics.py`; unit tests | [ ] |
| 4 | Feature engineering; XGBoost; start LSTM | `src/features/*`; `src/models/xgb.py`, `lstm.py` | [ ] |
| 5 | Full evaluation vs baseline per horizon 1–7 d; plots; FastAPI backend; start dashboard | Evaluation report (honest, incl. failures); `src/api/*` | [ ] |
| 6 | Dashboard (Leaflet + Plotly); optional ESP32/MQTT; Docker; docs polish; 60-second demo | `dashboard/`; `docker-compose.yml`; demo script | [ ] |

## Risks
- No usable ground-truth discharge → fall back to a proxy target (e.g. flood records, water-level sensor) and state this clearly.
- Time budget → ESP32/MQTT and SMAP are optional; cut first.

## Definition of done (for the demo)
- Reproducible pipeline from raw pull to metrics table.
- Baseline and ML compared on an identical held-out period.
- Clear limitations section. Negative results reported as such.
