# AI Flood Early-Warning Demo

> **Status: 🚧 in progress (started 2026).** This is a research prototype. No results, accuracy figures, or deployments are claimed anywhere in this repository. Items marked `TODO` are planned, not done.

## Research question

Can satellite rainfall (CHIRPS) combined with machine learning (XGBoost, LSTM) outperform a standard SCS-CN runoff baseline for short-term (1–7 day) flood-risk forecasting in a Ugandan catchment?

## Motivation

Floods in Uganda repeatedly affect lives, roads, farmland and urban drainage, while ground gauge networks are sparse. Freely available satellite rainfall, terrain and land-cover products — optionally complemented by low-cost IoT sensors — may help build affordable early-warning tools. The SCS Curve Number method is widely used in data-scarce settings, so it is a natural, transparent baseline: the question is whether ML adds measurable skill over it, and under which conditions.

## Study area

**[choose catchment]** — TODO. Selection criteria: (1) some observed streamflow or water-level record or documented flood events, (2) manageable size (~100–2,000 km²), (3) mixed land cover so curve numbers vary, (4) accessible for optional sensor deployment. See `docs/roadmap.md` (Week 1).

## Data sources

| Data | Product | Use |
|---|---|---|
| Rainfall | CHIRPS daily (~5 km) via Google Earth Engine | Main forcing, lagged/accumulated features |
| Terrain | SRTM or Copernicus DEM (30 m) | Slope, flow accumulation, TWI, catchment delineation |
| Land cover | Sentinel-2 / ESA WorldCover (10 m) | Curve-number assignment, imperviousness |
| Soil moisture (optional) | NASA SMAP | Antecedent wetness feature |
| Ground truth | Observed discharge / water level / flood records — TODO: source | Targets and validation |
| Sensors (optional) | ESP32 + rain gauge / water-level sensor over MQTT | Local validation, not required for the core study |

Details, licences and caveats: [`docs/data.md`](docs/data.md).

## Methods (planned)

1. **Baseline:** SCS-CN runoff from CHIRPS rainfall, curve numbers from land cover × soil group, with antecedent-moisture adjustment.
2. **ML models:** XGBoost on engineered features (lagged and accumulated rainfall, terrain/land-cover descriptors, optional SMAP); LSTM on daily sequences.
3. **Forecast horizons:** 1 to 7 days ahead.
4. **Validation:** chronological split (no shuffling), rolling-origin evaluation; all models compared to the SCS-CN baseline on the same test period.

See [`docs/methods.md`](docs/methods.md).

## Evaluation metrics

- **RMSE** — root mean squared error
- **NSE** — Nash–Sutcliffe efficiency
- **KGE** — Kling–Gupta efficiency
- Optionally event-based scores (hit rate / false alarm rate) for flood-threshold exceedance.

Results: **TODO — none yet.**

## Repository structure

```
flood-ewd-repo/
├── README.md
├── LICENSE
├── requirements.txt
├── docker-compose.yml        # skeleton
├── .gitignore
├── docs/                     # methods.md, data.md, roadmap.md
├── data/                     # raw/interim/processed (git-ignored), see data/README.md
├── notebooks/                # exploration notebooks
├── src/
│   ├── data/                 # Earth Engine pulls, loaders
│   ├── baseline/             # SCS-CN
│   ├── features/             # feature engineering
│   ├── models/               # XGBoost, LSTM
│   ├── evaluation/           # RMSE / NSE / KGE, plots
│   └── api/                  # FastAPI backend
├── dashboard/                # Next.js + Leaflet + Plotly (planned)
├── firmware/                 # ESP32 sketch (optional, planned)
└── tests/
```

## How to run

> Most steps below are **planned**; scripts will be added as they are implemented.

```bash
# 1. Environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Authenticate Google Earth Engine (one-off)
earthengine authenticate

# 3. TODO: pull data for the chosen catchment
# python -m src.data.ee_pull --config configs/catchment.yaml

# 4. TODO: baseline, features, models, evaluation
# python -m src.baseline.scs_cn ...
# python -m src.models.train_xgb ...
# python -m src.models.train_lstm ...
# python -m src.evaluation.run ...

# 5. TODO: API and dashboard
# uvicorn src.api.main:app --reload
# cd dashboard && npm install && npm run dev

# Optional: services skeleton (PostGIS, MQTT, API)
docker compose up -d db mqtt
```

## Roadmap / status — **in progress**

| Item | Status |
|---|---|
| Repo scaffold and docs | In progress |
| Catchment selection | TODO |
| Data pipeline (CHIRPS/DEM/land cover) | TODO |
| SCS-CN baseline | TODO |
| XGBoost / LSTM | TODO |
| Evaluation (RMSE/NSE/KGE) | TODO |
| API + dashboard | TODO |
| Optional ESP32/MQTT | TODO |

Full 6-week plan: [`docs/roadmap.md`](docs/roadmap.md).

## Limitations (known in advance)

- CHIRPS is a ~5 km product and can miss localised convective storms.
- SCS-CN is an event-runoff method; using it for continuous daily forecasting needs care.
- Ground truth in Ugandan catchments is sparse; results depend on the quality of available observations.
- This is a demonstration, **not** an operational warning system and must not be used for safety decisions.

## Author

**Joshua Mugabo** — joshuamugabo67@gmail.com

## License

MIT — see [`LICENSE`](LICENSE).
