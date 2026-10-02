# Data sources

Status: planned; nothing downloaded yet. Always check current licences/terms before redistribution. Raw data is **not** committed (see `.gitignore`).

| Dataset | Earth Engine ID (verify before use) | Resolution | Notes |
|---|---|---|---|
| CHIRPS Daily | `UCSB-CHG/CHIRPS/DAILY` | ~0.05° (~5 km), daily, 1981–present | Gauge-blended satellite rainfall. Weak on very local convective storms. |
| SRTM DEM | `USGS/SRTMGL1_003` | 30 m | Alternative: Copernicus GLO-30 (`COPERNICUS/DEM/GLO30`). |
| ESA WorldCover | `ESA/WorldCover/v200` | 10 m | Land cover classes for CN assignment. |
| Sentinel-2 SR | `COPERNICUS/S2_SR_HARMONIZED` | 10–20 m | Optional: NDVI/NDWI, custom classification, flood extent checks. |
| SMAP (optional) | `NASA/SMAP/SPL4SMGP/008` (verify version) | ~9–11 km | Antecedent soil moisture. |
| Soils (optional) | SoilGrids / HWSD | 250 m–1 km | Hydrologic soil group for CN. TODO. |
| Observed flow / level | TODO — e.g. national water authority gauges, GRDC, local records | — | Key dependency. Availability in the chosen catchment is unknown. |
| Flood event records | TODO — news, disaster agencies, satellite flood maps | — | For event-based validation. |
| ESP32 sensors (optional) | Own measurements | minutes–hourly | Rain tipping bucket, ultrasonic level; via MQTT. |

## Access
- Google Earth Engine account (non-commercial/research registration) and project ID → `earthengine authenticate`.
- Store credentials outside the repo; use `.env` (git-ignored).

## Directory conventions
```
data/raw/        # untouched downloads/exports
data/interim/    # cleaned, clipped, reprojected
data/processed/  # model-ready tables/tensors
```

## Known issues / risks
- Gauge data gaps and rating-curve uncertainty.
- CHIRPS vs. local rain-gauge bias; consider bias correction if local gauges exist.
- Land-cover date mismatch with study period.
- Forecast horizons of 1–7 days require either rainfall forecasts (e.g. GFS/ECMWF, TODO) or a model that predicts from past data only — this must be stated explicitly in every result.
