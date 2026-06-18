# SUBMIT: AIOps Lab W1 - Group 2

## Group Reflection

Bài Lab tuần này đã mang lại cho nhóm một bài học cực kỳ sâu sắc về giá trị của AIOps và tư duy giám sát hệ thống phân tán.
Lúc đầu, khi nhìn vào cảnh báo lúc 23:04, chúng tôi rất dễ bị bối rối bởi "cơn bão cảnh báo" (Alert Storm) đến từ cả 4 services cùng một lúc. Tuy nhiên, bằng cách áp dụng tuần tự các phương pháp EDA, phân tích đa độ đo (multi-metric correlation) và Machine Learning (Isolation Forest, Z-score), chúng tôi đã thành công trong việc lọc nhiễu, tìm ra service gốc rễ (`cart-service`).
Đặc biệt, việc kết hợp (Fusion) dòng thời gian của Metrics với các Log Templates được trích xuất từ thuật toán Drain3 đã tạo ra bằng chứng không thể chối cãi. Chúng tôi hiểu ra rằng, sự cố hiếm khi đột ngột xảy ra mà thường có một "Silent Period" kéo dài nhiều giờ trước đó (như vụ rò rỉ RAM âm ỉ). Nếu có một hệ thống AIOps tự động phát hiện được tín hiệu chìm này, on-call engineer đã có thể ngăn chặn thảm họa từ trước khi nó ảnh hưởng tới khách hàng.

## Contribution

> **[TO BE DISCUSSED]** Phần này sẽ được cập nhật sau khi nhóm họp và thống nhất về contribution của từng thành viên.

**Suggested structure (for group discussion):**

### Phase 1 - EDA (Exploratory Data Analysis)

- **Assigned to:** [Tên thành viên]
- **Tasks:** Load metrics từ 4 services, vẽ multi-service timeline, correlation heatmap
- **Deliverable:** `01-eda.py`, 2 PNG charts

### Phase 2 - Anomaly Detection

- **Assigned to:** [Tên thành viên]
- **Tasks:** Implement Z-score + Isolation Forest, tạo First Detection Time table
- **Deliverable:** `02-anomaly-detection.py`, anomaly comparison chart

### Phase 3 - Log Analysis & Fusion

- **Assigned to:** [Tên thành viên]
- **Tasks:** Run Drain3 clustering, cross-reference logs với metrics timeline
- **Deliverable:** `03-log-clustering.py`, `03-log-metrics-fusion.py`, 2 TXT reports

### Phase 4 - Documentation & Report

- **Assigned to:** [Tên thành viên]
- **Tasks:** Viết FINDINGS.md (postmortem) và SUBMIT.md (reflection)
- **Deliverable:** 2 MD files với evidence references

### Overall Coordination

- **Assigned to:** [Tên thành viên]
- **Tasks:** Project planning, workflow design, code review, quality assurance

---

**Note:** Mỗi thành viên cần ghi rõ phần việc cụ thể đã làm (ví dụ: "Implement Z-score algorithm, debug memory spike issue, write Section WHEN in FINDINGS.md")
