# Kế hoạch thực hiện bài Lab W1 (Detect & Triage)

Để giải quyết bài Lab này một cách trọn vẹn và đúng yêu cầu, mình đề xuất chúng ta sẽ đi qua 4 bước (tương ứng với 4 Phase). Mình sẽ viết các đoạn code Python chuẩn (bạn có thể copy vào file `.py` hoặc Jupyter Notebook `.ipynb` tùy ý). 

Toàn bộ code và báo cáo sẽ được lưu trong thư mục làm việc của nhóm (ở đây mình dùng `g2`).

## 1. Phase 1: Khám phá dữ liệu (Exploratory Data Analysis - EDA)
**Mục tiêu:** Nhìn bức tranh tổng thể và tìm ra "thời điểm bắt đầu rò rỉ" (WHEN).
- Đọc file `metrics/cart-service.csv`.
- Vẽ biểu đồ theo thời gian (Timeline) của `memory_usage_bytes` so với `memory_limit_bytes`.
- Trích xuất biểu đồ thể hiện số lần khởi động lại (`container_restart_count`) và tỉ lệ lỗi (`http_5xx_rate`).
- **Output:** Script `01-eda.py` (hoặc notebook) vẽ các biểu đồ phân tích xu hướng.

## 2. Phase 2: Phát hiện dị thường (Anomaly Detection)
**Mục tiêu:** Áp dụng thuật toán để AI tự động phát hiện ra điểm bất thường trên Metric thay vì nhìn bằng mắt thường (WHERE).
- Áp dụng **Phương pháp 1 (Statistical):** Rolling Z-score (3-Sigma) để dò tìm những điểm dữ liệu vượt quá ngưỡng thống kê bình thường.
- Áp dụng **Phương pháp 2 (Machine Learning):** Isolation Forest để huấn luyện mô hình cô lập các điểm dữ liệu bất thường dựa trên nhiều chiều (ví dụ: memory usage + 5xx rate).
- So sánh hiệu quả của 2 phương pháp (phương pháp nào phát hiện sớm hơn).
- **Output:** Script `02-anomaly-detection.py`.

## 3. Phase 3: Gom cụm Log (Log Clustering)
**Mục tiêu:** Đào sâu vào Log để xem chuyện gì thực sự xảy ra (WHAT).
- Cài đặt thư viện `drain3`.
- Chạy Drain3 trên file `logs/cart-service.log.jsonl` để rút trích các Log Templates (ví dụ biến các lỗi OOMKilled thành chung 1 cụm).
- Đếm số lượng log ERROR/FATAL theo từng mốc thời gian 5 phút.
- **Output:** Script `03-log-clustering.py` và xuất ra bảng danh sách các lỗi xuất hiện nhiều nhất.

## 4. Phase 4: Tổng hợp Báo cáo (Postmortem & Submit)
**Mục tiêu:** Tổng hợp thành tài liệu báo cáo để nộp cho Giảng viên.
- Viết file `FINDINGS.md`: Postmortem giải thích chi tiết WHEN (lúc nào bắt đầu leak), WHERE (service nào tạch), WHAT (tại sao).
- Viết file `SUBMIT.md`: Group reflection và phân công đóng góp.

## User Review Required
> [!IMPORTANT]
> Đây là quy trình 4 bước chuẩn chỉ nhất để "phá án". 
> Bạn có đồng ý với kế hoạch này không? Nếu OK, mình sẽ tiến hành viết và chạy code cho **Bước 1 (EDA)** ngay bây giờ nhé!
