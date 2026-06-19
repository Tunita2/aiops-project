# MLOps Lifecycle — Pipeline Instructions

## Prerequisites

- Docker + Docker Compose
- Python 3.11+ với `uv` package manager

## Quick Start

```bash
# 1. Khởi động Docker stack (MLflow, PostgreSQL, Prometheus, Pushgateway, Grafana)
cd data-pack
bash scripts/start_stack.sh

# 2. Verify services
curl -s http://localhost:5000/health             # MLflow
curl -s http://localhost:9090/-/healthy          # Prometheus
curl -s http://localhost:9091/-/healthy          # Pushgateway
curl -s http://localhost:3000/api/health         # Grafana

# 3. Install Python dependencies
uv pip install 'mlflow==2.13.2' 'evidently==0.4.40' scikit-learn pandas numpy fastapi uvicorn prometheus_client requests

# 4. Set tracking URI
export MLFLOW_TRACKING_URI=http://localhost:5000

# 5. Train V1 + register @production
uv run python tunita2/pipeline.py --data data-pack/data/baseline.csv

# 6. Start model server (separate terminal)
uv run python tunita2/serve.py

# 7. Verify serving
curl -s http://localhost:8000/health/active-version

# 8. Run full retrain pipeline (drift → train v2 → holdout → approve → promote → monitor)
uv run python tunita2/retrain.py \
    --reference data-pack/data/baseline.csv \
    --current data-pack/data/drifted.csv \
    --holdout data-pack/data/holdout.csv \
    --post-deploy-eval data-pack/data/post_deploy_eval.csv \
    --auto-approve

# 9. Grafana dashboard: http://localhost:3000 → "AIOps MLOps Lifecycle"

# 10. Stop stack
cd data-pack
bash scripts/stop_stack.sh
```

## File Structure

| File | Purpose |
|---|---|
| `pipeline.py` | Train IsolationForest, log vào MLflow, register model `@production` |
| `serve.py` | FastAPI server: `/predict`, `/health/active-version`, `/reload`, `/metrics` |
| `drift_detector.py` | Evidently DataDriftPreset + performance drift (3 check modes) |
| `retrain.py` | Orchestrator: drift → retrain → staging → approve → promote → monitor → rollback |
| `metrics_util.py` | Push metrics lên Prometheus Pushgateway cho Grafana |
| `DESIGN.md` | Design defense (7 sub-checkpoints) |
| `SUBMIT.md` | Reflection (5 câu hỏi) |
