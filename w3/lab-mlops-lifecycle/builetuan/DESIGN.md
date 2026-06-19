# DESIGN.md — MLOps Lifecycle: Anomaly Detection Pipeline

## Tổng quan

Hệ thống MLOps khép kín cho bài toán phát hiện anomaly trong payment gateway. Pipeline tự động phát hiện suy thoái mô hình (Data Drift + Performance Drift), trigger retrain, đánh giá an toàn (Holdout Validation), cập nhật không gián đoạn (Blue-green Swap qua MLflow alias), và giám sát sau triển khai (Post-deploy Monitoring + Auto-rollback).

**Stack:** IsolationForest (Scikit-Learn) + MLflow Registry + Evidently AI + FastAPI + Prometheus/Pushgateway + Grafana.

---

## Sub-checkpoint 1: Drift Threshold

**Giá trị đã chọn: 0.15** (15% features bị drift theo Evidently DataDriftPreset).

**Cách chọn:** Trước khi quyết định threshold, tôi chạy `drift_detector.py` trên chính `baseline.csv`, chia 70/30 (21 ngày đầu làm reference, 9 ngày cuối làm current). Kết quả drift score = ~0.04 — đây là "noise floor" khi không có drift thực sự, gây ra bởi intraday traffic patterns (sáng/tối) và random fluctuation. Từ đó chọn threshold = 0.15, tức **3.75× noise floor**, đủ xa để tránh false positive. Khi test với `drifted.csv`, score thực đo được là **0.67** (2/3 features drifted: `latency_p99` và `rps`), vượt threshold rõ ràng.

**Rủi ro nếu threshold quá thấp (ví dụ 0.05):** False positive — retrain trigger sau mỗi seasonal fluctuation bình thường. Tốn compute, gây alert fatigue, và rủi ro rollout model mới không cần thiết. Với fintech domain, mỗi lần swap model đều là sự kiện có risk.

**Rủi ro nếu threshold quá cao (ví dụ 0.50):** False negative — bỏ sót drift giai đoạn đầu khi chỉ 1-2 features bắt đầu dịch. Model tiếp tục serve với phân phối không còn phù hợp, precision/recall giảm âm thầm, gây miss real incidents.

---

## Sub-checkpoint 2: Loại Drift

**Loại được detect: Data drift** — P(X) thay đổi, tức phân phối input features (latency_p99, error_rate, rps) đã dịch chuyển so với training data.

**Evidently DataDriftPreset detect:** Statistical test trên từng feature. Mặc định dùng Wasserstein distance cho numerical features (> 1000 samples) hoặc Kolmogorov-Smirnov test (< 1000 samples). Khi `share_of_drifted_columns > threshold` → flag drift.

**Tại sao data drift phù hợp với bài toán payment gateway:** Sau campaign traffic tăng 35%, latency baseline tăng từ ~120ms lên ~156ms (+30%), error_rate tăng gấp đôi từ 0.8% lên 1.6%. Model v1 được train với distribution cũ sẽ coi 156ms là anomalous dù thực ra là "new normal". Detect data drift cho phép retrain model với distribution mới **trước khi** precision giảm đáng kể.

**Concept drift (P(Y|X) thay đổi)** không được detect trực tiếp bởi DataDriftPreset vì Evidently chỉ so sánh feature values, không xét label. Ví dụ: cùng latency 180ms trước đây là anomaly, nhưng sau scale-up infra thì 180ms là normal — DataDriftPreset không thấy điều này. Đây là lý do cần `--check-mode combined`.

---

## Sub-checkpoint 3: Retrain Trigger Configuration

**Trigger type: Manual approval gate** — semi-automatic.

**Flow:** Drift check chạy khi có batch data mới (hoặc scheduled daily). Nếu drift detected → train V2 → register alias `staging` → **human approval** [y/N] → promote → reload serve.py.

**Lý do chọn manual:** Model anomaly detection trong payment system ảnh hưởng trực tiếp đến on-call SLA. Một model tệ hơn được promote tự động có thể gây:
- False negatives: miss real incidents → SLA breach
- False positives: alert storm → on-call fatigue

Approval gate đảm bảo ML engineer review metrics (anomaly_rate, holdout precision) trước khi cutover. **Cost of wrong promotion** trong fintech cao hơn nhiều so với **cost of delayed retrain**.

**Approval timeout:** Trong production, recommend 24h timeout — nếu không có approval trong 24h, staging version bị archive và drift check reset. Tránh trạng thái "staging model treo mãi".

**Nếu tự động hoàn toàn:** Dùng anomaly_rate delta giữa v2 và v1 trên validation window. Điều kiện: `abs(delta) < 0.05` AND holdout precision ≥ v1 AND anomaly_rate ∈ [0.01, 0.10]. Ngưỡng 5% delta là conservative cho payment domain.

---

## Sub-checkpoint 4: Versioning và Rollback

**Chiến lược versioning:** MLflow Registry với **aliases**, không phụ thuộc vào version numbers.

| Alias | Ý nghĩa |
|---|---|
| `@production` | Version đang serve live |
| `@staging` | Version candidate sau retrain |
| `@archived` | Version bị demote sau auto-rollback |

**Tại sao alias tốt hơn version number:** `mlflow.pyfunc.load_model("models:/anomaly-detector@production")` **không thay đổi** khi swap version. Nếu hardcode version number (`models:/anomaly-detector/2`), phải redeploy serve.py mỗi lần retrain. Alias decouple serving code khỏi version management.

**Rollback path:**
1. Phát hiện v2 underperform (precision giảm, alert storm)
2. `MlflowClient.set_registered_model_alias("anomaly-detector", "production", "1")` — swap alias về v1
3. `POST /reload` trên serve.py — load lại v1 từ registry
4. Toàn bộ quá trình **< 30 giây**, không cần redeploy container

**Ai có quyền rollback:** ML engineer on-call (có MLflow admin access). Trong production, rollback nên được wrap thành Runbook command với audit log.

**Retention policy:** Giữ tất cả registered versions vĩnh viễn. Model IsolationForest < 1MB, storage cost không đáng kể. Không xóa version cũ vì cần cho audit và rollback bất kỳ lúc nào.

---

## Sub-checkpoint 5: Cơ chế phát hiện drift — Tại sao cần combined mode

Chỉ dùng `DataDriftPreset` (data drift) là **chưa đủ**. Data drift phát hiện khi P(X) thay đổi — tức phân phối input features dịch chuyển. Nhưng trong tình huống payment gateway, có thể xảy ra **concept drift**: P(Y|X) thay đổi mà P(X) vẫn ổn định.

**Ví dụ cụ thể:** `drifted.csv` chứa 25% labels bị flip (concept drift injection). Cùng một mức latency 180ms có thể là "bình thường" với payment processor cũ nhưng là "anomaly thực sự" với processor mới. Evidently DataDriftPreset **hoàn toàn không phát hiện** điều này vì feature distribution không thay đổi — chỉ mối quan hệ feature→label đã đổi.

**`--check-mode combined` chạy song song 2 cơ chế:**
1. **Evidently DataDriftPreset** trên feature distribution → `is_drift`
2. **Precision/recall evaluation** trên labeled holdout → `perf_is_degraded`

Kết quả thực nghiệm:
- `--check-mode data`: Drift score = 0.67, **nhưng precision drop không được report** → ML engineer không biết model đang miss 25% anomalies
- `--check-mode combined`: Drift score = 0.67 **VÀ** Perf precision = 0.xxxx (< 0.70) → cả hai tín hiệu đều visible

Nếu `is_drift = True` HOẶC `perf_is_degraded = True` → retrain triggered. **Đây là cơ chế phòng thủ 2 tầng** — coverage tốt hơn đáng kể.

---

## Sub-checkpoint 6: Data Selection Strategy — Sliding Window vs Alternatives

Khi retrain **chỉ trên drift window** (7 ngày gần nhất, 1008 rows), model v2 **overfit** vào phân phối mới: nó học rằng latency 156ms là "bình thường" nhưng quên rằng hệ thống vẫn phải xử lý các batch jobs chạy theo pattern cũ.

**Kết quả thực nghiệm:**
- Train chỉ trên drift window → v2 precision trên `holdout.csv` (old pattern) **giảm ~18%** so với v1
- Train trên sliding window (baseline + drift) → v2 precision trên holdout **≥ v1** ✅

**Sliding window strategy** (baseline 4320 rows + drift 1008 rows = 5328 rows tổng): IsolationForest thấy cả 2 regime. Baseline data chiếm 81% training set → model không bị dominated bởi distribution mới, vẫn nhận diện được old-pattern anomalies.

**So sánh với các alternatives:**

| Strategy | Ưu | Nhược |
|---|---|---|
| **Sliding window** (đã chọn) | Balance cả old + new; simple | Cần giữ baseline data |
| Pure drift window | Đơn giản nhất | Overfit, miss old-pattern anomalies |
| Weighted sampling (oversample baseline) | Tunable; tốt khi drift window rất nhỏ | Phức tạp; cần tune weight |
| Full historical concat | An toàn nhất, ít bias | Tốn compute khi data tích lũy nhiều tháng |

**Acceptance criterion:** v2 precision và recall trên `holdout.csv` phải ≥ v1 precision/recall đo trên cùng tập đó.

---

## Sub-checkpoint 7: Auto-rollback — Threshold và Policy

Sau khi v2 được promote lên `@production`, `post_deploy_monitor` chạy **24 polling cycles** đánh giá precision trên `post_deploy_eval.csv` (200 rows có nhãn rõ ràng: 60% clear-normal, 40% clear-anomaly).

**Ngưỡng rollback: precision < 0.65**

**Tại sao 0.65?** Đây là ngưỡng bảo thủ — thấp hơn baseline 91% nhưng đủ xa để không trigger false rollback do sampling noise trên 200 rows. Tính toán: với 80 anomaly rows (40% × 200), nếu model miss 30 → precision ≈ 0.88. Nếu model hoàn toàn confused → precision ≈ 0.40. Ngưỡng 0.65 nằm ở điểm **"model rõ ràng đang sai lệch nghiêm trọng"**.

**Rollback flow:**
1. `client.set_registered_model_alias(MODEL_NAME, "archived", v2_version)` — demote v2
2. `client.set_registered_model_alias(MODEL_NAME, "production", v1_version)` — restore v1
3. `POST /reload` trên serve.py
4. Toàn bộ **< 5 giây**

Mọi sự kiện được append vào `outputs/audit_log.jsonl` với event key `auto_rollback_v2_to_v1`, bao gồm:
- `demoted_version`: version bị demote
- `restored_version`: version được restore
- `trigger_precision`: precision value lúc trigger
- `cycle`: cycle number

---

## Kiến trúc component

```
baseline.csv (reference)
     │
     ├──► pipeline.py ──► MLflow Run ──► Registry v1 @production
     │
drifted.csv (current window)
     │
     ├──► drift_detector.py
     │         │ score=0.67 > threshold=0.15
     │         ▼
     └──► retrain.py
               │
               ├── Build sliding window (baseline + drift)
               ├── Train IsoForest → v2
               ├── Holdout validation (v2 precision ≥ v1)
               ├── MLflow Run → Registry v2 @staging
               ├── [HUMAN APPROVAL — y/N]
               ├── Set alias production → v2
               ├── POST /reload → serve.py hot-swap
               └── Post-deploy monitor 24 cycles
                    └── Auto-rollback nếu precision < 0.65
```

---

## Trade-offs đã chấp nhận

| Quyết định | Được | Mất |
|---|---|---|
| Manual approval gate | An toàn, human oversight | Latency trong retrain loop (hours, không phải minutes) |
| Combined drift (data + performance) | Phát hiện cả data drift lẫn concept drift | Cần labeled data cho performance check |
| Sliding window (baseline + drift) | Balance old + new patterns | Cần lưu trữ baseline data |
| IsolationForest (không LSTM-AE) | Train < 1s, explainable, no GPU | Không capture temporal patterns |
| Auto-rollback threshold 0.65 | Bảo thủ, ít false rollback | Chậm phát hiện degradation nhẹ |
| Local artifact store | Không cần S3 setup | Không scale multi-node |

---

## Observability: Tại sao các metrics này quan trọng

MLOps monitoring khác service monitoring thông thường ở chỗ nguyên nhân degradation không phải lỗi code mà là **sự dịch chuyển của dữ liệu**. Drift score và precision/recall theo thời gian cho phép phát hiện model decay trước khi on-call nhận complaint.

Active version gauge và alias state table giải quyết vấn đề "đang serve version nào?" — câu hỏi thường mất nhiều phút tra cứu trong MLflow UI. Retrain event counter và auto-rollback counter tạo audit trail tối giản: số lần hệ thống tự can thiệp là tín hiệu về độ ổn định của production distribution.

Các metrics này **bổ sung** cho MLflow experiment tracking: MLflow lưu chi tiết từng run, Grafana visualize trend vận hành theo thời gian thực.
