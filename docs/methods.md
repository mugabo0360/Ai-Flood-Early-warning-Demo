# Methods (planned — in progress)

Nothing here has been run yet unless explicitly stated. Parameters marked TODO will be fixed after catchment selection.

## 1. Problem definition
Forecast flood risk 1–7 days ahead for one Ugandan catchment **[choose catchment]**. Target, to be decided from available ground truth (TODO):
- (a) daily discharge / water level at an outlet gauge (regression), and/or
- (b) binary flood-threshold exceedance (classification, derived from (a) or documented flood events).

## 2. Catchment preparation
- Delineate catchment from DEM (SRTM 30 m or Copernicus GLO-30): fill sinks, flow direction, flow accumulation, outlet snapping.
- Derive slope, elevation statistics, TWI, drainage density.
- Land cover: ESA WorldCover (10 m) and/or Sentinel-2 classification; compute class fractions.

## 3. Baseline: SCS-CN runoff
For daily rainfall P (mm) and potential maximum retention S = 25400/CN − 254 (mm):

    Q = (P − Ia)² / (P − Ia + S)   for P > Ia, else 0,   with Ia = λ·S (λ = 0.2 default; TODO sensitivity test)

- CN assigned per land-cover class × hydrologic soil group (TODO: soil source, e.g. SoilGrids) → area-weighted catchment CN.
- Antecedent moisture: adjust CN (AMC I/II/III) from 5-day antecedent rainfall, optionally SMAP.
- Runoff depth → streamflow proxy via simple routing (e.g. unit hydrograph / linear reservoir). TODO decide.
- Forecast horizon h: use forecast-free baseline configurations (e.g. persistence of CN-derived runoff) and, if available, rainfall forecasts. TODO define clearly to keep comparison fair.

## 4. Features (ML)
- Rainfall: lagged values (t…t−14), rolling sums (3/7/14/30 d), max intensity, days since last rain.
- Static: catchment mean elevation/slope, TWI, land-cover fractions, weighted CN.
- Optional: SMAP soil moisture, seasonality (day of year sin/cos), sensor observations.
- Leakage control: features at forecast origin t use data ≤ t only.

## 5. Models
- **XGBoost:** one model per horizon (direct strategy) or horizon as a feature. Hyperparameters tuned with time-series CV.
- **LSTM:** sequence length TODO (e.g. 30 d), multi-output for 1–7 d. Early stopping on a chronological validation block.
- Both compared with the SCS-CN baseline and a naive persistence/climatology reference.

## 6. Validation protocol
- Chronological split: train / validation / test, test period untouched until final evaluation.
- Rolling-origin (expanding window) cross-validation for tuning.
- Report per horizon (1…7 d) and for high-flow events separately.

## 7. Metrics
- RMSE = sqrt(mean((sim − obs)²))
- NSE = 1 − Σ(sim − obs)² / Σ(obs − mean(obs))²
- KGE = 1 − sqrt((r − 1)² + (α − 1)² + (β − 1)²), r = correlation, α = σ_sim/σ_obs, β = μ_sim/μ_obs
- Optional event scores: POD, FAR, CSI for threshold exceedance.

## 8. Optional sensor component
ESP32 with rain gauge and/or ultrasonic water-level sensor publishes via MQTT to a broker; a subscriber writes to PostGIS. Used for local sanity-checks of satellite rainfall, not for core training unless enough data accumulates. TODO.

## 9. Results
**TODO — none.** Results will be added only after experiments are run and reproducible from this repo.
