# SUBMIT.md — Reflection: MLOps Lifecycle Lab

## Câu 1: Drift threshold bạn chọn là bao nhiêu và tại sao?

Threshold là **0.15** (15% features drifted). Cách chọn: chạy `drift_detector.py` trên chính `baseline.csv`, split 70/30 — noise floor đo được ~0.04. Threshold 0.15 = 3.75× noise floor, đủ xa để không bị false positive từ seasonal variation (sáng/tối traffic khác nhau), nhưng đủ thấp để catch drift thực. Khi test với `drifted.csv`, score = **0.67** — vượt threshold rõ ràng (2 trong 3 features drifted: latency_p99 và rps). Nếu chọn 0.05, drift check sẽ fire mỗi ngày do intraday traffic pattern. Nếu chọn 0.50, sẽ bỏ sót drift giai đoạn đầu khi chỉ 1-2 features bắt đầu dịch chuyển — đặc biệt nguy hiểm khi payment processor mới rollout chỉ ảnh hưởng 1 feature ban đầu.

---

## Câu 2: Điều gì xảy ra nếu model v2 sau retrain lại tệ hơn v1?

Pipeline có **3 tầng bảo vệ** chống lại trường hợp này:

1. **Holdout validation** (trước khi promote): v2 được test trên `holdout.csv` (500 rows old-pattern). Nếu precision giảm nghiêm trọng so với v1, ML engineer thấy ngay trong output.
2. **Manual approval gate** [y/N]: ML engineer review anomaly_rate, holdout precision/recall trước khi promote. Nếu v2 tệ → từ chối promote, v2 ở lại alias `staging`.
3. **Auto-rollback** (sau promote): 24 polling cycles trên `post_deploy_eval.csv`. Nếu precision < 0.65 → demote v2 → `@archived`, restore v1 → `@production`, gọi `POST /reload`.

Rollback chỉ thay đổi alias trong MLflow Registry + reload serve.py. Toàn bộ < 30 giây, không cần redeploy container. Cả v1 và v2 tồn tại song song trong registry — không mất version nào.

---

## Câu 3: Sự khác biệt giữa data drift và concept drift?

**Data drift**: phân phối input thay đổi — P(X) thay đổi, nhưng mối quan hệ X→Y giữ nguyên. Ví dụ cụ thể trong bài lab: latency baseline tăng từ ~120ms lên ~156ms (+30%) vì thêm 3rd-party integration. Các feature values đã dịch chuyển — model vẫn "đúng về nguyên tắc" nhưng anomaly threshold không còn phù hợp.

**Concept drift**: mối quan hệ input-output thay đổi — P(Y|X) thay đổi. Ví dụ: cùng latency 200ms trước đây là anomaly, nhưng sau khi scale up infra thì 200ms là bình thường. Model hoàn toàn sai dù input distribution không đổi nhiều. Trong `drifted.csv`, 25% labels bị flip — đây là concept drift injection.

Evidently `DataDriftPreset` trong lab này detect **data drift** bằng statistical tests trên feature values (Wasserstein distance). Nó **hoàn toàn không phát hiện** concept drift vì không xét label. Đây là lý do `--check-mode combined` cần thiết: performance check (precision/recall trên labeled holdout) là proxy để phát hiện concept drift.

---

## Câu 4: Tại sao blue-green swap quan trọng hơn replace file trực tiếp?

Replace file trực tiếp (overwrite model artifact) tạo ra **race condition**: serve.py đang xử lý request dùng model cũ, đồng thời file bị ghi đè → corrupted read → crash hoặc wrong prediction. Không có rollback — version cũ đã bị xóa.

Blue-green qua MLflow alias: alias `@production` được swap **atomically** từ v1 → v2. serve.py chỉ load model mới khi nhận `POST /reload` — tất cả in-flight requests trước đó hoàn thành với v1. Key benefits:
- **Zero downtime**: không có khoảng thời gian "model đang bị thay"
- **Instant rollback**: swap alias về v1 + reload = rollback trong < 30 giây
- **Audit trail**: cả 2 versions tồn tại song song trong registry — truy vết rõ ràng

Trong production thực, replace file = unacceptable risk. Blue-green alias swap là standard practice cho model deployment.

---

## Câu 5: Nếu automate approval gate, dùng metric gì và threshold nào?

Dùng **anomaly_rate delta** giữa v2 và v1 trên cùng một validation window (20% cuối của current window làm holdout). Điều kiện auto-promote:

1. `abs(v2_anomaly_rate - v1_anomaly_rate) < 0.05` — v2 không thay đổi behavior quá nhiều
2. `v2_anomaly_rate < 0.10` — không bị degenerate (flag toàn bộ data là anomaly)
3. `v2_anomaly_rate > 0.01` — không quá conservative (không phát hiện gì)
4. Holdout precision ≥ v1 holdout precision — không regression trên old patterns

Ngưỡng 5% delta là conservative cho payment domain — sai lệch 5% trên 1000 requests/phút = 50 missed anomalies/phút, chưa kể SLA impact. Ngoài ra cần kết hợp với post-deploy monitoring: dù auto-approve, auto-rollback vẫn active như safety net cuối cùng.

Nếu cả 4 điều kiện thỏa → auto-promote. Nếu không → đẩy alert cho ML engineer review trong 4h.
