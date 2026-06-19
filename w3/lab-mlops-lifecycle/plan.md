# Kế Hoạch Triển Khai Bài Lab: MLOps Lifecycle & Automated Retraining Loop

Tài liệu này phác thảo lộ trình 4 giai đoạn để xây dựng một hệ thống MLOps khép kín: Tự động phát hiện suy thoái mô hình (Drift/Performance) $\rightarrow$ Tái huấn luyện (Retrain V2) $\rightarrow$ Đánh giá an toàn (Sanity Check) $\rightarrow$ Cập nhật không gián đoạn (Hot-swap Deploy) $\rightarrow$ Giám sát sau triển khai (Post-deploy Monitoring & Auto-rollback).

---

## 📋 GIAI ĐOẠN 1: KHỞI ĐỘNG HẠ TẦNG & HUẤN LUYỆN MÔ HÌNH GỐC (V1)
*Mục tiêu: Thiết lập môi trường MLOps và đăng ký phiên bản Production đầu tiên.*

- [ ] **Task 1.1: Khởi động Stack công cụ**
  - Chạy `bash scripts/start_stack.sh` để kích hoạt MLflow, PostgreSQL, Prometheus, Pushgateway và Grafana.
  - Sử dụng lệnh `curl` kiểm tra trạng thái sức khỏe (health-check) của tất cả các port dịch vụ (`5000`, `9090`, `9091`, `3000`).
- [ ] **Task 1.2: Chuẩn bị dữ liệu và Huấn luyện Baseline (V1)**
  - Chạy `uv run python data/generate_data.py` để sinh các file dữ liệu giả lập (`baseline.csv`, `drifted.csv`, `holdout.csv`, `post_deploy_eval.csv`).
  - Hoàn thiện `pipeline.py`: Đọc `baseline.csv`, huấn luyện mô hình `IsolationForest` (Scikit-Learn).
  - Tích hợp MLflow Tracking: Log các tham số (hyperparameters), chỉ số đánh giá (metrics), và artifact của mô hình.
  - Đăng ký mô hình vào MLflow Model Registry và gắn thẻ (tag) `@production` cho phiên bản V1 này.

---

## ⚙️ GIAI ĐOẠN 2: XÂY DỰNG MODEL SERVER & BỘ PHÁT HIỆN LỆCH DỮ LIỆU (Drift Detector)
*Mục tiêu: Dựng API phục vụ dự đoán và hệ thống cảnh báo sớm khi mô hình "bị dốt đi".*

- [ ] **Task 2.1: Phát triển Model Server thông minh (`serve.py`)**
  - Sử dụng `FastAPI` để dựng API phục vụ tại port `8000` với endpoint `/predict`.
  - **Cơ chế Hot-reload:** Viết endpoint `/health/active-version`. Server phải có logic định kỳ hoặc kích hoạt chủ động truy vấn sang MLflow API để kéo phiên bản mang tag `@production` về bộ nhớ (`Live Loading`) mà không cần restart container.
  - Tích hợp `prometheus_client` để xuất các metric vận hành của server (số lượt predict, tỉ lệ anomaly phát hiện).
- [ ] **Task 2.2: Xây dựng Bộ phát hiện suy thoái (`drift_detector.py`)**
  - Sử dụng thư viện `Evidently AI` để so sánh tập dữ liệu đang chạy (`current`) với tập chuẩn (`reference`).
  - Hỗ trợ 3 chế độ kiểm tra thông qua cờ `--check-mode`:
    - `data`: Check lệch phân phối đầu vào (Data Drift sử dụng `DataDriftPreset`).
    - `performance`: Check sụt giảm độ chính xác dựa trên nhãn thực tế đổ về muộn.
    - `combined`: Kết hợp cả hai điều kiện trên.
  - Nếu phát hiện vượt ngưỡng an toàn $\rightarrow$ Xuất trạng thái `DRIFT_DETECTED` và đẩy chỉ số sang Prometheus Pushgateway.

---

## 🛡️ GIAI ĐOẠN 3: PHÁT TRIỂN BỘ ĐIỀU PHỐI VÒNG ĐỜI TOÀN DIỆN (`retrain.py`)
*Mục tiêu: Triển khai "bộ não" tự động hóa khép kín khống chế toàn bộ vòng đời ML.*

- [ ] **Task 3.1: Trigger Pipeline Tái huấn luyện tự động**
  - Lắng nghe tín hiệu từ `drift_detector.py`. Khi có lỗi `DRIFT_DETECTED`, tự động kích hoạt `pipeline.py` chạy trên tập dữ liệu mới (`drifted.csv`) để cho ra mô hình V2.
- [ ] **Task 3.2: Tầng bảo vệ Sanity Check (Chống phá hoại mô hình mới)**
  - Đem mô hình V2 vừa huấn luyện xong đi test với tập dữ liệu `holdout.csv` (tập dữ liệu chứa các mẫu hành vi cũ nhưng chuẩn xác).
  - **Kiểm định:** Nếu V2 giải quyết được dữ liệu mới (`drifted`) nhưng làm sụt giảm nghiêm trọng độ chính xác trên dữ liệu cũ (`holdout`) $\rightarrow$ Từ chối phê duyệt (`REJECT_V2`), giữ nguyên V1 ở Production để bảo vệ hệ thống.
- [ ] **Task 3.3: Thăng cấp mô hình (Promote to Production)**
  - Nếu V2 vượt qua tầng Sanity Check $\rightarrow$ Tự động đổi tag `@production` từ V1 sang cho V2 trên MLflow Registry.
  - Gọi tín hiệu để Model Server (`serve.py`) thực hiện Hot-swap load model mới ngay lập tức.

---

## 🧪 GIAI ĐOẠN 4: GIÁM SÁT SAU TRIỂN KHAI & TỰ ĐỘNG ROLLBACK (Post-Deploy)
*Mục tiêu: Kiểm soát rủi ro tuyệt đối sau khi đưa mô hình mới lên môi trường thật.*

- [ ] **Task 4.1: Chạy mô phỏng 24 Chu kỳ đánh giá (Evaluation Loops)**
  - Đọc dữ liệu từ `post_deploy_eval.csv` để giả lập dữ liệu thực tế đổ về theo từng chu kỳ (mỗi chu kỳ đại diện cho 1 khoảng thời gian thực tế).
  - Với mỗi chu kỳ: Đẩy dữ liệu qua `/predict` của mô hình V2 mới, sau đó đối chiếu kết quả dự đoán với Ground Truth để tính chỉ số Accuracy/F1-score thực tế.
  - Đẩy các chỉ số hiệu năng này theo thời gian thực (Real-time Metric) lên Prometheus Pushgateway.
- [ ] **Task 4.2: Cơ chế Tự động Hạ cấp (Auto-Rollback)**
  - Trong vòng 24 chu kỳ theo dõi, nếu chỉ số của mô hình V2 bị sụt giảm liên tiếp xuống dưới ngưỡng an toàn cấu hình $\rightarrow$ Xác định V2 bị lỗi ẩn (Hidden Regression).
  - Bộ điều phối tự động ra lệnh **Rollback**: Gỡ tag `@production` ở mô hình V2, trả lại tag `@production` cho mô hình V1 cũ.
- [ ] **Task 4.3: Đánh giá và Nghiệm thu trực quan**
  - Truy cập Grafana tại `http://localhost:3000`, mở Dashboard "AIOps MLOps Lifecycle".
  - Theo dõi đường đi đồ thị: Trạng thái Drift vọt lên $\rightarrow$ Quá trình Train V2 bắt đầu $\rightarrow$ Metric của Active Version đổi từ V1 sang V2 $\rightarrow$ Đường hiệu năng phục hồi (hoặc đồ thị Rollback kích hoạt nếu giả lập kịch bản V2 lỗi).