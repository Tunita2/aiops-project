# Kế hoạch thực hiện bài Lab W1 (Nâng cấp)

Dựa trên những góp ý vô cùng sắc bén và chính xác của bạn, mình đã cấu trúc lại toàn bộ kế hoạch. Để đạt điểm tối đa, bài Lab không thể chỉ nhìn phiến diện vào `cart-service` mà phải có góc nhìn toàn cảnh (Multi-service & Multi-metric).

Kế hoạch NÂNG CẤP sẽ được triển khai như sau:

## 1. Phase 1: EDA (Upgraded) - Phân tích Đa dịch vụ
**Mục tiêu:** Tìm ra service nào có signal sớm nhất và phân tích hiệu ứng dây chuyền (Cascade effect).
- Đọc và plot tất cả 4 file metrics (`cart-service`, `order-service`, `payment-service`, `api-gateway`).
- Vẽ multi-service timeline comparison để đối chiếu các luồng dữ liệu theo thời gian.
- Phân tích Correlation (tương quan) giữa các services (ví dụ: HTTP 5xx của Cart tăng thì Upstream timeout của Order tăng thế nào).
- **Output:** Script `01-eda.py` (cập nhật).

## 2. Phase 2: Anomaly Detection (Upgraded) - Phân tích Đa độ đo
**Mục tiêu:** Tìm "silent signal" (tín hiệu chìm) sớm nhất từ nhiều khía cạnh của `cart-service`.
- Apply Z-score và Isolation Forest trên các metrics:
  - `memory_usage_bytes`
  - `jvm_gc_pause_ms_avg`
  - `http_5xx_rate`
  - `cpu_usage_percent`
- Tạo bảng timeline (anomaly timeline table) tổng hợp các cảnh báo.
- Tìm ra EARLIEST anomaly (silent signal) chính xác đến từng phút.
- **Output:** Script `02-anomaly-detection.py` (cập nhật).

## 3. Phase 3: Log + Metrics Fusion
**Mục tiêu:** Trích xuất Error/Fatal log và map (đối chiếu) với Metric timeline để khẳng định Root Cause.
- Chạy Drain3 trên cả 2 file log (`cart-service.log.jsonl` và `order-service.log.jsonl`).
- Trích xuất các timestamps xuất hiện ERROR/FATAL đầu tiên.
- Cross-reference (đối chiếu chéo) với timeline của Metric Anomalies ở Phase 2.
- **Output:** Script `03-log-metrics-fusion.py`.

## 4. Phase 4: Report (Cấu trúc chuẩn mực)
**Mục tiêu:** Viết Postmortem chuyên nghiệp.
- **`FINDINGS.md`** sẽ được cấu trúc lại chặt chẽ:
  - Executive Summary (Tóm tắt sự cố)
  - WHEN - Timeline Analysis (Mốc thời gian chi tiết)
  - WHERE - Root Cause Service & Metric (Nơi bắt nguồn)
  - WHAT - Root Cause Hypothesis (Cơ chế sinh lỗi)
  - Evidence (Bằng chứng: Biểu đồ, Log snippets, KQ Anomaly detection)
- **`SUBMIT.md`**: Group reflection.

## User Review Required
> [!IMPORTANT]
> Mình hoàn toàn đồng ý với nhận xét của bạn! Những bổ sung này là **bắt buộc phải có** để phân tích nguyên nhân gốc rễ (Root Cause Analysis) một cách thuyết phục nhất trong môi trường Microservices thực tế. 
> 
> Bạn xem qua bản kế hoạch nâng cấp này nhé. Nếu bạn "Chốt", mình sẽ tiến hành đập đi xây lại 3 file code để đáp ứng chuẩn mực mới này ngay lập tức!
