# Kế Hoạch Triển Khai Bài Lab: Closed-Loop Auto-Remediation Orchestrator

Tài liệu này phác thảo lộ trình 4 giai đoạn để xây dựng bộ điều phối tự động hóa khép kín (Orchestrator) từ số 0 đạt chuẩn Production-ready (AIOps/SRE Senior).

---

## 📋 GIAI ĐOẠN 1: KHÁM PHÁ & THIẾT KẾ CẤU HÌNH (Định hình tư duy)
*Mục tiêu: Tách biệt hoàn toàn dữ liệu cấu hình ra khỏi logic code Python.*

- [x] **Task 1.1: Phân tích cấu trúc Alert**
  - Mổ xẻ JSON mẫu từ Alertmanager đổ về.
  - Xác định cách bóc tách hai trường cốt lõi: `alertname` và `service` từ Label.
- [x] **Task 1.2: Thiết kế file cấu hình hệ thống (`config.yaml`)**
  - Khai báo cổng kết nối và URL của Prometheus, Alertmanager.
  - Định nghĩa `runbook_map`: Ánh xạ động từ Tên Alert $\rightarrow$ Đường dẫn file Script sửa lỗi.
  - Định nghĩa `rollback_map`: Ánh xạ lệnh khôi phục trạng thái cũ khi sửa thất bại.
  - Thiết lập tham số cấu hình cho các tầng phòng vệ (ngưỡng Circuit Breaker, giới hạn Blast Radius).

---

## ⚙️ GIAI ĐOẠN 2: XÂY DỰNG CORE PIPELINE (Nhận và Chạy)
*Mục tiêu: Thông suốt luồng đi dữ liệu cơ bản từ Alertmanager đến việc thực thi Script.*

- [x] **Task 2.1: Viết Webhook Receiver / Poller (Bộ nhận tín hiệu)**
  - Polling Alertmanager API (`/api/v2/alerts`) định kỳ mỗi 15s để lấy active alerts.
  - Kiểm tra tính hợp lệ của JSON alert payload.
- [x] **Task 2.2: Xây dựng hàm Quyết định (`decide`) & Thực thi (`act`)**
  - **Decide:** Đọc dữ liệu Alert $\rightarrow$ Tra cứu `config.yaml` để tìm Runbook tương ứng.
  - **Decision Validation:** Kiểm tra xem file script có nằm trong danh sách đăng ký an toàn (`runbook_registry`) hay không. Nếu không, từ chối chạy ngay lập tức để chống hiện tượng LLM bị bịa tên lệnh (Hallucination).
  - **Act:** Sử dụng thư viện `subprocess` của Python để thực thi file Bash Script một cách an toàn.

---

## 🛡️ GIAI ĐOẠN 3: TRIỂN KHAI CÁC TẦNG BẢO VỆ AN TOÀN (Closed-Loop)
*Mục tiêu: Đưa trí thông minh và khả năng "tự vệ" vào code để bảo vệ hạ tầng.*

- [x] **Task 3.1: Tích hợp Blast Radius Guard (Giới hạn vùng ảnh hưởng)**
  - Thiết lập bộ đếm thời gian (Sliding Window).
  - Kiểm tra: Nếu số hành động tự động sửa lỗi vượt quá $N$ lần/phút hoặc số lần restart của 1 service vượt quá $M$ lần/giờ $\rightarrow$ Chặn hành động và Log cảnh báo nguy hiểm.
- [x] **Task 3.2: Khóa đồng thời theo Dịch vụ (Per-service Mutex)**
  - Sử dụng `threading.Lock()` để tạo map quản lý lock theo tên service.
  - Đảm bảo: Nếu `payment-svc` đang được xử lý cứu lỗi, mọi Alert trùng lặp tiếp theo của riêng `payment-svc` sẽ bị bỏ qua (hoặc xếp hàng), tránh việc chạy đè lệnh gây Crash Loop. Các dịch vụ khác vẫn chạy song song bình thường.
- [x] **Task 3.3: Tầng Xác thực (Verify) & Tự động Rollback**
  - Viết hàm gọi API sang Prometheus sau khi chạy Runbook.
  - Tiến hành Polling liên tục (ví dụ: 5 giây một lần trong vòng 60 giây).
  - **Kịch bản A (Thành công):** Nếu Metric (Latency, Error Rate) hạ về ngưỡng quy định trong `baseline.json` $\rightarrow$ Đánh dấu `ACTION_SUCCESS`.
  - **Kịch bản B (Thất bại):** Nếu hết thời gian Timeout mà Metric vẫn xấu $\rightarrow$ Kịch hoạt lệnh Rollback tương ứng từ cấu hình và đánh dấu thất bại.
- [x] **Task 3.4: Bộ ngắt mạch an toàn (Circuit Breaker - Cầu chì)**
  - Giám sát số lần thất bại liên tiếp của toàn hệ thống điều phối.
  - Nếu số lần thất bại/rollback liên tiếp vượt quá ngưỡng cấu hình $\rightarrow$ Chuyển trạng thái sang `OPEN`.
  - Ngừng hoàn toàn việc Polling/nhận Alert, đóng băng tự động hóa để chờ con người vào xử lý thủ công (`CIRCUIT_BREAKER_HALT`).

---

## 🧪 GIAI ĐOẠN 4: NGHIỆM THU VÀ KIỂM THỬ KHỦNG BỐ (Chaos Testing)
*Mục tiêu: Đảm bảo bộ điều phối "sống sót" trước mọi kịch bản lỗi thực tế.*

- [x] **Task 4.1: Kiểm thử chế độ Dry-Run**
  - Chạy Orchestrator với cờ `--dry-run`.
  - Kiểm tra xem hệ thống có nhận Alert, có khớp đúng cấu hình và ghi nhận Log chính xác mà không thực sự can thiệp vào hạ tầng hay không.
- [x] **Task 4.2: Đấu nối trực tiếp và Test phá hoại**
  - Khởi động toàn bộ cụm hạ tầng bằng `start_stack.sh`.
  - Chạy bộ điều phối vừa viết ở chế độ Production.
  - Sử dụng `inject_fault.sh` để giả lập lần lượt 6 kịch bản lỗi của bài lab (lỗi chậm, lỗi sập service, lỗi liên hoàn để kích hoạt cầu chì, lỗi LLM giả lập đưa sai tên script).
- [x] **Task 4.3: Đánh giá kết quả trên Dashboard**
  - Mở Grafana để quan sát trạng thái chuyển dịch của các chỉ số do chính bộ điều phối đẩy lên (`circuit_breaker_gauge`, `verify_status_gauge`).
  - Đảm bảo hệ thống tự phục hồi về đúng trạng thái `baseline.json` ổn định.