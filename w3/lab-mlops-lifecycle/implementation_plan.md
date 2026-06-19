# MLOps Lifecycle Lab — Implementation Plan

## Mục tiêu

Xây dựng hệ thống MLOps khép kín: Train V1 → Drift Detection → Retrain V2 → Approval Gate → Promote → Post-deploy Monitor → Auto-Rollback. Tất cả chạy local với Docker Compose + Python.

---

## Cấu trúc thư mục bài nộp

```
builetuan/
├── pipeline.py           # Train IsolationForest + MLflow register
├── serve.py              # FastAPI /predict + /health/active-version + /reload
├── drift_detector.py     # Evidently DataDriftPreset + Performance drift
├── retrain.py            # Orchestrator: drift → train v2 → staging → approve → promote → post-deploy
├── metrics_util.py       # Pushgateway helpers cho Grafana dashboard
├── DESIGN.md             # Thiết kế + defense 7 sub-checkpoints
├── SUBMIT.md             # Reflection 5 câu hỏi
└── README.md             # Hướng dẫn chạy pipeline
```

---

## Giai đoạn 1: Setup hạ tầng & Train V1

### [NEW] `builetuan/pipeline.py`
- Train `IsolationForest` trên `data/baseline.csv` (4320 rows)
- Log params: `contamination=0.03`, `n_estimators=100`, `random_state=42`
- Log metrics: `train_anomaly_rate`, `feature_count`
- Log model via `mlflow.sklearn.log_model()` + scaler artifact
- Register model name `anomaly-detector`, set alias `@production`

### Setup commands
```bash
# Start Docker stack (MLflow, PostgreSQL, Prometheus, Pushgateway, Grafana)
bash data-pack/scripts/start_stack.sh

# Install dependencies
uv pip install 'mlflow==2.13.2' 'evidently==0.4.40' scikit-learn pandas numpy fastapi uvicorn prometheus_client requests

# Train V1
export MLFLOW_TRACKING_URI=http://localhost:5000
uv run python builetuan/pipeline.py --data data-pack/data/baseline.csv
```

---

## Giai đoạn 2: Model Server & Drift Detector

### [NEW] `builetuan/serve.py`
- FastAPI app, port 8000
- Startup: load model từ `models:/anomaly-detector@production`
- `POST /predict` — nhận `{features: [[...], ...]}`, trả `{predictions, scores, version}`
- `GET /health/active-version` — version đang serve
- `POST /reload` — reload model sau swap alias
- `GET /metrics` — Prometheus metrics (request count, latency histogram)

### [NEW] `builetuan/drift_detector.py`
- Wrapper cho Evidently `DataDriftPreset`
- 3 check modes: `data`, `performance`, `combined`
- `data`: so sánh feature distribution (Wasserstein/JS divergence)
- `performance`: precision/recall trên labeled holdout → concept drift
- `combined`: cả hai — flag nếu MỘT TRONG HAI detect drift
- Save HTML report → `outputs/drift_reports/`
- Log drift score → MLflow
- Push metrics → Pushgateway

### [NEW] `builetuan/metrics_util.py`
- Helper functions: `push_drift_score()`, `push_model_eval()`, `push_event()`, `push_active_version()`
- Best-effort push — không crash nếu Pushgateway offline

---

## Giai đoạn 3: Retrain Orchestrator

### [NEW] `builetuan/retrain.py`
- **Step 1**: Load reference + current data
- **Step 2**: Run `drift_detector.detect_drift()` → nếu no drift → exit
- **Step 3**: Train V2 trên sliding window (baseline + drift window concat)
- **Step 4**: Holdout validation — v2 precision/recall trên `holdout.csv` phải ≥ v1
- **Step 5**: Register V2 → alias `@staging`
- **Step 6**: Approval gate — `[y/N]` prompt (hoặc `--auto-approve`)
- **Step 7**: Promote staging → production, reload serve.py
- **Step 8**: Post-deploy monitor 24 cycles trên `post_deploy_eval.csv`
- **Auto-rollback**: nếu precision < 0.65 → demote V2 → `@archived`, restore V1 → `@production`
- Audit log → `outputs/audit_log.jsonl`

---

## Giai đoạn 4: Documentation

### [NEW] `builetuan/DESIGN.md`
7 sub-checkpoints:
1. **Drift threshold** — 0.15, noise floor 0.04, tại sao
2. **Drift type** — Data drift vs Concept drift, Evidently detect gì
3. **Retrain trigger** — Manual approval, tại sao
4. **Versioning + Rollback** — MLflow aliases, rollback path
5. **Combined mode** — Tại sao cần combined, ví dụ cụ thể
6. **Sliding window** — So sánh với alternatives
7. **Auto-rollback** — Threshold 0.65, policy

### [NEW] `builetuan/SUBMIT.md`
5 câu hỏi reflection với số liệu thực từ run

### [NEW] `builetuan/README.md`
Hướng dẫn chạy pipeline từ đầu đến cuối

---

## Verification Plan

### Acceptance Criteria 1-3 (Basic)
```bash
# Train V1
uv run python builetuan/pipeline.py --data data-pack/data/baseline.csv

# Serve
uv run python builetuan/serve.py &
curl http://localhost:8000/health/active-version

# Drift detection
uv run python builetuan/drift_detector.py --reference data-pack/data/baseline.csv --current data-pack/data/drifted.csv
```

### Acceptance Criterion 4 (Stress 1 — Combined mode)
```bash
uv run python builetuan/drift_detector.py \
  --reference data-pack/data/baseline.csv \
  --current data-pack/data/drifted.csv \
  --check-mode combined \
  --labeled-current data-pack/data/drifted.csv \
  --model-uri models:/anomaly-detector@production
```

### Acceptance Criterion 5 (Stress 2 — Holdout validation)
```bash
uv run python builetuan/retrain.py \
  --reference data-pack/data/baseline.csv \
  --current data-pack/data/drifted.csv \
  --holdout data-pack/data/holdout.csv \
  --auto-approve
```

### Acceptance Criterion 6 (Stress 3 — Auto-rollback)
```bash
uv run python builetuan/retrain.py \
  --reference data-pack/data/baseline.csv \
  --current data-pack/data/drifted.csv \
  --holdout data-pack/data/holdout.csv \
  --post-deploy-eval data-pack/data/post_deploy_eval.csv \
  --auto-approve
```

---

## Open Questions

> [!NOTE]
> Không có câu hỏi mở. Lab này có sample solution rõ ràng, tôi sẽ triển khai theo đúng spec trong HANDOUT.md với code và nội dung riêng của mình.
