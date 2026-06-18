# DESIGN.md — Kiến Trúc Bộ Điều Phối Tự Phục Hồi Kín

## 1. Lựa chọn Decision Engine: Rule-based hay LLM-based?

**Lựa chọn: Rule-based** (ánh xạ tĩnh qua `config.yaml`).

### Lý do:

- **Tính xác định (Determinism):** Trong môi trường Production, mỗi hành động tự động can thiệp hạ tầng phải có kết quả dự đoán được 100%. Rule-based đảm bảo rằng cùng một input (alertname) luôn cho cùng một output (runbook script). LLM-based có rủi ro trả về kết quả không nhất quán giữa các lần gọi API (stochastic output).

- **Độ trễ và độ tin cậy:** Rule-based thực thi gần như tức thì (tra cứu dictionary), không phụ thuộc vào mạng hoặc API bên ngoài. LLM-based cần gọi API qua internet (Anthropic Claude), thêm 1–5 giây latency mỗi lần quyết định, và sẽ thất bại hoàn toàn nếu mạng bị gián đoạn — điều không chấp nhận được khi hệ thống đang trong trạng thái sự cố.

- **Chi phí vận hành bằng 0:** Không cần API key, không cần trả phí theo token. Hệ thống hoạt động hoàn toàn offline trên localhost.

### Trade-offs:

| Tiêu chí | Rule-based | LLM-based |
|---|---|---|
| Độ trễ quyết định | < 1ms | 1–5s (API call) |
| Xử lý alert mới chưa có rule | ❌ Không xử lý được | ✅ Có thể suy luận |
| Tính xác định | ✅ 100% deterministic | ❌ Stochastic |
| Phụ thuộc mạng | ❌ Không | ✅ Có |
| Chi phí | $0 | $0.003–0.015/request |

---

## 2. Cấu hình Blast-Radius

```yaml
blast_radius:
  max_actions_per_minute: 3
  max_restarts_per_service_per_hour: 5
```

### Giải trình các con số:

- **`max_actions_per_minute: 3`**: Hệ thống Ronki có 5 service. Nếu xảy ra bão cảnh báo (Alert Storm), giới hạn 3 hành động/phút đảm bảo tối đa 60% service bị tác động trong một phút bất kỳ, tránh việc restart toàn bộ stack đồng thời gây sập database hoặc load balancer.

- **`max_restarts_per_service_per_hour: 5`**: Một service bị restart 5 lần trong 1 giờ mà vẫn lỗi có nghĩa là vấn đề nằm ở code hoặc cơ sở hạ tầng (data corruption, disk full, network partition), không phải do container bị treo. Lần restart thứ 6 trở đi là vô ích và chỉ gây thêm downtime do thời gian khởi động container (~5-10 giây/lần).

### Cơ chế kỹ thuật:
Sử dụng **Sliding Window** dựa trên `deque` (hàng đợi hai đầu) với timestamp. Mỗi lần `check()`, các timestamp cũ hơn horizon (60s cho global, 3600s cho per-service) sẽ bị loại bỏ tự động.

---

## 3. Verify step: Metric, Threshold, Timeout

### Metric kiểm tra:
1. **`latency_p99`**: Phân vị 99 của độ trễ (histogram_quantile trên `http_request_duration_seconds_bucket`)
2. **`up`**: Trạng thái hoạt động của container (`up{job="<service>"}`)

### Threshold (ngưỡng):
```json
{
  "latency_p99_max_ms": 500,
  "up_required": 1
}
```
- **Latency p99 < 500ms**: Giá trị baseline bình thường của các service nằm trong khoảng 72–230ms. Ngưỡng 500ms cho phép biên dao động sau restart (~2x baseline) mà vẫn đảm bảo trải nghiệm người dùng chấp nhận được.
- **Up = 1**: Container phải ở trạng thái Running và phản hồi health check.

### Timeout & Polling:
```json
{
  "verify_timeout_seconds": 60,
  "verify_poll_interval_seconds": 10,
  "verify_min_samples": 3
}
```
- **Timeout 60s**: Đủ thời gian cho container khởi động (~5s) + warm-up JIT/cache (~10–15s) + 3 lần sample liên tiếp (30s).
- **Poll mỗi 10s**: Đủ thời gian để Prometheus scrape mới (scrape interval = 15s) trong khi không quá chậm.
- **3 mẫu liên tiếp**: Yêu cầu 3 lần đo liên tiếp đều healthy, loại bỏ trường hợp metric tạm thời tốt do cache hit hoặc low traffic.

---

## 4. Circuit Breaker: Reset thủ công hay tự động?

**Lựa chọn: Manual Reset** (operator phải restart process).

### Lý do:

- **An toàn là trên hết**: Khi circuit breaker mở (3 lần thất bại liên tiếp), đó là tín hiệu rõ ràng rằng vấn đề vượt quá khả năng tự phục hồi của hệ thống. Nếu auto-reset, robot sẽ lặp lại chu kỳ: thử 3 lần → mở cầu dao → đợi cooldown → thử thêm 3 lần → mở cầu dao... tạo thành vòng lặp phá hoại không kết thúc.

- **Cơ hội cho Post-Mortem**: Manual reset buộc kỹ sư phải đăng nhập, đọc log, hiểu nguyên nhân gốc (root cause) trước khi bật lại tự động hóa. Điều này ngăn chặn việc "sweep under the rug" — bỏ qua sự cố chưa được giải quyết triệt để.

- **Đơn giản hóa code**: Không cần timer phức tạp cho half-open state hay cooldown period. Process restart = state reset = tất cả counter về 0.

### Nhược điểm chấp nhận được:
- Cần kỹ sư trực (on-call) để restart process khi cầu dao mở vào ban đêm.
- Khắc phục: Tích hợp thêm PagerDuty/Slack notification khi `CIRCUIT_BREAKER_HALT` xảy ra (ngoài scope bài lab).
