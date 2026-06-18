# SUBMIT.md — Kết Quả Kiểm Thử Các Kịch Bản Chaos

> **Ghi chú**: Dán log JSON output vào từng section bên dưới sau khi chạy từng scenario.

---

## Scenario 1 — Action Succeeds (HighLatency trên payment-svc)

**Lệnh inject lỗi:**
```bash
bash data-pack/scripts/inject_fault.sh latency payment-svc 500ms
```

**Kết quả mong đợi:**
- `ALERT_DETECTED`: alertname=HighLatency, service=payment-svc
- `DRY_RUN_PASS`
- `BLAST_RADIUS_OK`
- `ACTION_EXECUTED`: restart payment-svc
- `VERIFY_PASS`: latency trở về bình thường
- `ACTION_SUCCESS`

**Log output:**
```json
{"ts": "2026-06-18T14:14:32.768098+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "HighLatency", "service": "payment-svc", "severity": "warning"}
{"ts": "2026-06-18T14:14:32.770132+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "HighLatency", "service": "payment-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:14:32.770648+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "payment-svc"}
{"ts": "2026-06-18T14:14:32.771675+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "payment-svc", "dry_run": true}
{"ts": "2026-06-18T14:14:32.921622+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "payment-svc", "returncode": 0, "stdout": "[DRY-RUN] would execute: docker restart ronki-payment-svc", "stderr": ""}
{"ts": "2026-06-18T14:14:32.922282+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/restart_service.sh", "service": "payment-svc"}
{"ts": "2026-06-18T14:14:32.922785+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "payment-svc", "dry_run": false}
{"ts": "2026-06-18T14:14:40.121546+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "payment-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-payment-svc...\nronki-payment-svc\n[restart_service] Waiting 5s for ronki-payment-svc to come up...\n[restart_service] ronki-payment-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:14:40.122086+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_EXECUTED", "runbook": "runbooks/restart_service.sh", "service": "payment-svc"}
{"ts": "2026-06-18T14:14:40.122599+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_START", "service": "payment-svc", "timeout_s": 120}
{"ts": "2026-06-18T14:14:40.181583+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 1, "latency_p99_ms": 988.90625, "up": 1.0, "latency_ok": false, "up_ok": true}
{"ts": "2026-06-18T14:14:50.221807+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 2, "latency_p99_ms": 984.8214285714286, "up": 1.0, "latency_ok": false, "up_ok": true}
{"ts": "2026-06-18T14:15:00.239195+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 3, "latency_p99_ms": 978.0434782608695, "up": 1.0, "latency_ok": false, "up_ok": true}
{"ts": "2026-06-18T14:15:10.260745+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 4, "latency_p99_ms": 958.9285714285711, "up": 1.0, "latency_ok": false, "up_ok": true}
{"ts": "2026-06-18T14:15:20.293480+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 5, "latency_p99_ms": 928.3333333333331, "up": 1.0, "latency_ok": false, "up_ok": true}
{"ts": "2026-06-18T14:15:30.323319+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 6, "latency_p99_ms": 248.2181540005263, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:15:40.337733+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 7, "latency_p99_ms": 248.25409836065577, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:15:50.372842+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 8, "latency_p99_ms": 248.25206611570246, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:15:50.374346+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_PASS", "service": "payment-svc", "samples": 8}
{"ts": "2026-06-18T14:15:50.375910+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_SUCCESS", "alertname": "HighLatency", "service": "payment-svc", "runbook": "runbooks/restart_service.sh"}
```

---

## Scenario 2 — Action Fails → Rollback (InstanceDown trên checkout-svc)

**Lệnh inject lỗi:**
```bash
bash data-pack/scripts/inject_fault.sh kill checkout-svc
```

**Kết quả mong đợi:**
- `ALERT_DETECTED`: alertname=InstanceDown, service=checkout-svc
- `ACTION_EXECUTED`: restart checkout-svc → fail
- `VERIFY_FAIL`: service vẫn down
- `ROLLBACK_TRIGGERED`
- `ROLLBACK_EXECUTED`

**Log output:**
```json
{"ts": "2026-06-18T14:16:59.568009+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "InstanceDown", "service": "checkout-svc", "severity": "critical"}
{"ts": "2026-06-18T14:16:59.575320+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "InstanceDown", "service": "checkout-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:16:59.575842+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "checkout-svc"}
{"ts": "2026-06-18T14:16:59.576881+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": true}
{"ts": "2026-06-18T14:16:59.742579+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[DRY-RUN] would execute: docker restart ronki-checkout-svc", "stderr": ""}
{"ts": "2026-06-18T14:16:59.745380+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:16:59.745886+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:17:05.393209+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:17:05.395126+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_EXECUTED", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:17:05.396106+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_START", "service": "checkout-svc", "timeout_s": 30}
{"ts": "2026-06-18T14:17:05.433690+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 1, "latency_p99_ms": null, "up": 0.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:17:15.457970+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 2, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:17:25.518117+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 3, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:17:35.519841+00:00", "logger": "verify", "level": "WARNING", "event_type": "VERIFY_FAIL", "service": "checkout-svc", "samples": 3}
{"ts": "2026-06-18T14:17:35.522451+00:00", "logger": "orchestrator", "level": "WARNING", "event_type": "ROLLBACK_TRIGGERED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:17:35.523443+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:17:43.435346+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:17:43.439012+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ROLLBACK_EXECUTED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}
```

---

## Scenario 3 — Circuit Breaker (3 lần thất bại liên tiếp)

**Cách thực hiện:** Inject lỗi liên tiếp 3 lần, hoặc đặt ngưỡng verify rất thấp (latency < 10ms) để verify luôn fail.

**Kết quả mong đợi:**
- Lần thất bại #1: `ROLLBACK_EXECUTED`
- Lần thất bại #2: `ROLLBACK_EXECUTED`
- Lần thất bại #3: `CIRCUIT_BREAKER_HALT`
- Không có thêm `ACTION_EXECUTED` nào sau đó

**Log output:**
```json
{"ts": "2026-06-18T14:16:59.568009+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "InstanceDown", "service": "checkout-svc", "severity": "critical"}
{"ts": "2026-06-18T14:16:59.575320+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "InstanceDown", "service": "checkout-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:16:59.575842+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "checkout-svc"}
{"ts": "2026-06-18T14:16:59.576881+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": true}
{"ts": "2026-06-18T14:16:59.742579+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[DRY-RUN] would execute: docker restart ronki-checkout-svc", "stderr": ""}
{"ts": "2026-06-18T14:16:59.745380+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:16:59.745886+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:17:05.393209+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:17:05.395126+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_EXECUTED", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:17:05.396106+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_START", "service": "checkout-svc", "timeout_s": 30}
{"ts": "2026-06-18T14:17:05.433690+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 1, "latency_p99_ms": null, "up": 0.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:17:15.457970+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 2, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:17:25.518117+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 3, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:17:35.519841+00:00", "logger": "verify", "level": "WARNING", "event_type": "VERIFY_FAIL", "service": "checkout-svc", "samples": 3}
{"ts": "2026-06-18T14:17:35.522451+00:00", "logger": "orchestrator", "level": "WARNING", "event_type": "ROLLBACK_TRIGGERED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:17:35.523443+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:17:43.435346+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:17:43.439012+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ROLLBACK_EXECUTED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}

{"ts": "2026-06-18T14:19:14.835248+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "InstanceDown", "service": "checkout-svc", "severity": "critical"}
{"ts": "2026-06-18T14:19:14.842608+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "InstanceDown", "service": "checkout-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:19:14.844673+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "checkout-svc"}
{"ts": "2026-06-18T14:19:14.845681+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": true}
{"ts": "2026-06-18T14:19:15.218480+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[DRY-RUN] would execute: docker restart ronki-checkout-svc", "stderr": ""}
{"ts": "2026-06-18T14:19:15.221070+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:19:15.222639+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:19:22.623528+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:19:22.625092+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_EXECUTED", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:19:22.626178+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_START", "service": "checkout-svc", "timeout_s": 30}
{"ts": "2026-06-18T14:19:22.697684+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 1, "latency_p99_ms": null, "up": 0.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:19:32.737037+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 2, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:19:42.806595+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 3, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:19:52.810365+00:00", "logger": "verify", "level": "WARNING", "event_type": "VERIFY_FAIL", "service": "checkout-svc", "samples": 3}
{"ts": "2026-06-18T14:19:52.810365+00:00", "logger": "orchestrator", "level": "WARNING", "event_type": "ROLLBACK_TRIGGERED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:19:52.810365+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:20:00.656657+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:20:00.657338+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ROLLBACK_EXECUTED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}

{"ts": "2026-06-18T14:21:15.179501+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "InstanceDown", "service": "checkout-svc", "severity": "critical"}
{"ts": "2026-06-18T14:21:15.188709+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "InstanceDown", "service": "checkout-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:21:15.189785+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "checkout-svc"}
{"ts": "2026-06-18T14:21:15.190296+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": true}
{"ts": "2026-06-18T14:21:15.584320+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[DRY-RUN] would execute: docker restart ronki-checkout-svc", "stderr": ""}
{"ts": "2026-06-18T14:21:15.587230+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:21:15.588542+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:21:21.649375+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:21:21.651487+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_EXECUTED", "runbook": "runbooks/restart_service.sh", "service": "checkout-svc"}
{"ts": "2026-06-18T14:21:21.653601+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_START", "service": "checkout-svc", "timeout_s": 30}
{"ts": "2026-06-18T14:21:21.711955+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 1, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:21:31.775071+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 2, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:21:41.845380+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "checkout-svc", "sample": 3, "latency_p99_ms": null, "up": 1.0, "latency_ok": false, "up_ok": false}
{"ts": "2026-06-18T14:21:51.848363+00:00", "logger": "verify", "level": "WARNING", "event_type": "VERIFY_FAIL", "service": "checkout-svc", "samples": 3}
{"ts": "2026-06-18T14:21:51.849410+00:00", "logger": "orchestrator", "level": "WARNING", "event_type": "ROLLBACK_TRIGGERED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:21:51.851070+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "dry_run": false}
{"ts": "2026-06-18T14:22:00.192781+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "checkout-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-checkout-svc...\nronki-checkout-svc\n[restart_service] Waiting 5s for ronki-checkout-svc to come up...\n[restart_service] ronki-checkout-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:22:00.193485+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ROLLBACK_EXECUTED", "service": "checkout-svc", "rollback_runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:22:00.195139+00:00", "logger": "safety", "level": "ERROR", "event_type": "CIRCUIT_BREAKER_HALT", "consecutive_failures": 3, "threshold": 3, "message": "Automation halted. Manual intervention required."}
{"ts": "2026-06-18T14:22:00.223033+00:00", "logger": "orchestrator", "level": "ERROR", "event_type": "CIRCUIT_BREAKER_HALT", "message": "Circuit open — polling suspended."}
```

---

## Scenario 4 — Multi-step Transactional Rollback (Nếu triển khai)

**Log output:**
```json
{"ts": "2026-06-18T14:47:07.918070+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "MultiStepDeploy", "service": "api-gateway", "severity": "critical"}
{"ts": "2026-06-18T14:47:07.920688+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "MultiStepDeploy", "service": "api-gateway", "runbook": "runbooks/multi_step_deploy.sh --step-a"}
{"ts": "2026-06-18T14:47:07.921232+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "api-gateway"}
{"ts": "2026-06-18T14:47:07.921766+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/multi_step_deploy.sh --step-a", "service": "api-gateway", "dry_run": true}
{"ts": "2026-06-18T14:47:08.145247+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/multi_step_deploy.sh --step-a", "service": "api-gateway", "returncode": 0, "stdout": "[DRY-RUN] step-A: would drain traffic → docker stop ronki-api-gateway", "stderr": ""}
{"ts": "2026-06-18T14:47:08.145711+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/multi_step_deploy.sh --step-a", "service": "api-gateway"}
{"ts": "2026-06-18T14:47:08.146217+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/multi_step_deploy.sh --step-a", "service": "api-gateway", "dry_run": false}
{"ts": "2026-06-18T14:47:11.164088+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/multi_step_deploy.sh --step-a", "service": "api-gateway", "returncode": 0, "stdout": "[multi_step_deploy] step-A: draining traffic from ronki-api-gateway...\nronki-api-gateway\n[multi_step_deploy] step-A complete.", "stderr": ""}
{"ts": "2026-06-18T14:47:11.165214+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/multi_step_deploy.sh --step-b", "service": "api-gateway", "dry_run": false}
{"ts": "2026-06-18T14:47:15.160282+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/multi_step_deploy.sh --step-b", "service": "api-gateway", "returncode": 0, "stdout": "[multi_step_deploy] step-B: applying new config to ronki-api-gateway...\nronki-api-gateway\n[multi_step_deploy] step-B complete.", "stderr": ""}
{"ts": "2026-06-18T14:47:15.162596+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/multi_step_deploy.sh --step-c", "service": "api-gateway", "dry_run": false}
{"ts": "2026-06-18T14:47:15.444103+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/multi_step_deploy.sh --step-c", "service": "api-gateway", "returncode": 1, "stdout": "[multi_step_deploy] step-C: re-enabling traffic for ronki-api-gateway...\n[multi_step_deploy] Simulating step-C failure (fail_step_c file detected)...", "stderr": ""}
{"ts": "2026-06-18T14:47:15.445621+00:00", "logger": "orchestrator", "level": "ERROR", "event_type": "TRANSACTIONAL_STEP_FAIL", "step": "runbooks/multi_step_deploy.sh --step-c", "service": "api-gateway", "completed_before_failure": ["runbooks/multi_step_deploy.sh --step-a", "runbooks/multi_step_deploy.sh --step-b"]}
{"ts": "2026-06-18T14:47:15.446202+00:00", "logger": "orchestrator", "level": "WARNING", "event_type": "TRANSACTIONAL_ROLLBACK_STEP", "step": "runbooks/multi_step_deploy.sh --rollback-b", "service": "api-gateway"}
{"ts": "2026-06-18T14:47:15.448958+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/multi_step_deploy.sh --rollback-b", "service": "api-gateway", "dry_run": false}
{"ts": "2026-06-18T14:47:20.380627+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/multi_step_deploy.sh --rollback-b", "service": "api-gateway", "returncode": 0, "stdout": "[multi_step_deploy] rollback-B: reverting config on ronki-api-gateway...\nronki-api-gateway\n[multi_step_deploy] rollback-B complete.", "stderr": ""}
{"ts": "2026-06-18T14:47:20.381637+00:00", "logger": "orchestrator", "level": "WARNING", "event_type": "TRANSACTIONAL_ROLLBACK_STEP", "step": "runbooks/multi_step_deploy.sh --rollback-a", "service": "api-gateway"}
{"ts": "2026-06-18T14:47:20.381637+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/multi_step_deploy.sh --rollback-a", "service": "api-gateway", "dry_run": false}
{"ts": "2026-06-18T14:47:22.536791+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/multi_step_deploy.sh --rollback-a", "service": "api-gateway", "returncode": 0, "stdout": "[multi_step_deploy] rollback-A: restoring traffic to ronki-api-gateway...\nronki-api-gateway\n[multi_step_deploy] rollback-A complete.", "stderr": ""}
{"ts": "2026-06-18T14:47:22.538117+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "TRANSACTIONAL_ROLLBACK_COMPLETE", "service": "api-gateway", "rolled_back": ["runbooks/multi_step_deploy.sh --rollback-b", "runbooks/multi_step_deploy.sh --rollback-a"]}
```

---

## Scenario 5 — Concurrent Alert Race

**Log output:**
```json
{"ts": "2026-06-18T14:47:32.713945+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ORCHESTRATOR_START", "config": "config.yaml", "dry_run": false, "poll_interval_s": 15}
{"ts": "2026-06-18T14:47:47.823552+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "HighLatency", "service": "payment-svc", "severity": "warning"}
{"ts": "2026-06-18T14:47:47.826552+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "HighLatency", "service": "inventory-svc", "severity": "warning"}
{"ts": "2026-06-18T14:47:47.830174+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "HighLatency", "service": "payment-svc", "severity": "critical"}
{"ts": "2026-06-18T14:47:47.830721+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "HighLatency", "service": "payment-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:47:47.830721+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "HighLatency", "service": "inventory-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:47:47.831260+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DECIDE_RUNBOOK", "alertname": "HighLatency", "service": "payment-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:47:47.832889+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "payment-svc"}
{"ts": "2026-06-18T14:47:47.833997+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "inventory-svc"}
{"ts": "2026-06-18T14:47:47.834529+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "BLAST_RADIUS_OK", "service": "payment-svc"}
{"ts": "2026-06-18T14:47:47.836683+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "payment-svc", "dry_run": true}
{"ts": "2026-06-18T14:47:47.836683+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "inventory-svc", "dry_run": true}
{"ts": "2026-06-18T14:47:47.837210+00:00", "logger": "orchestrator", "level": "WARNING", "event_type": "SERVICE_LOCK_BUSY", "service": "payment-svc", "message": "Another runbook is executing for this service; skipping duplicate"}
{"ts": "2026-06-18T14:47:48.301908+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "payment-svc", "returncode": 0, "stdout": "[DRY-RUN] would execute: docker restart ronki-payment-svc", "stderr": ""}
{"ts": "2026-06-18T14:47:48.301908+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "inventory-svc", "returncode": 0, "stdout": "[DRY-RUN] would execute: docker restart ronki-inventory-svc", "stderr": ""}
{"ts": "2026-06-18T14:47:48.303723+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/restart_service.sh", "service": "inventory-svc"}
{"ts": "2026-06-18T14:47:48.303723+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "DRY_RUN_PASS", "runbook": "runbooks/restart_service.sh", "service": "payment-svc"}
{"ts": "2026-06-18T14:47:48.304632+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "inventory-svc", "dry_run": false}
{"ts": "2026-06-18T14:47:48.304632+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_EXEC", "script": "runbooks/restart_service.sh", "service": "payment-svc", "dry_run": false}
{"ts": "2026-06-18T14:47:57.553154+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "payment-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-payment-svc...\nronki-payment-svc\n[restart_service] Waiting 5s for ronki-payment-svc to come up...\n[restart_service] ronki-payment-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:47:57.553842+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_EXECUTED", "runbook": "runbooks/restart_service.sh", "service": "payment-svc"}
{"ts": "2026-06-18T14:47:57.554347+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_START", "service": "payment-svc", "timeout_s": 120}
{"ts": "2026-06-18T14:47:57.643722+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 1, "latency_p99_ms": 248.2391304347826, "up": 0.0, "latency_ok": true, "up_ok": false}
{"ts": "2026-06-18T14:47:57.676433+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "RUNBOOK_RESULT", "script": "runbooks/restart_service.sh", "service": "inventory-svc", "returncode": 0, "stdout": "[restart_service] Restarting ronki-inventory-svc...\nronki-inventory-svc\n[restart_service] Waiting 5s for ronki-inventory-svc to come up...\n[restart_service] ronki-inventory-svc is running.", "stderr": ""}
{"ts": "2026-06-18T14:47:57.677442+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_EXECUTED", "runbook": "runbooks/restart_service.sh", "service": "inventory-svc"}
{"ts": "2026-06-18T14:47:57.677973+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_START", "service": "inventory-svc", "timeout_s": 120}
{"ts": "2026-06-18T14:47:57.706963+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "inventory-svc", "sample": 1, "latency_p99_ms": 95.64285714285717, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:48:07.686762+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 2, "latency_p99_ms": 248.15384615384616, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:48:07.756291+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "inventory-svc", "sample": 2, "latency_p99_ms": 95.66666666666664, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:48:17.704305+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 3, "latency_p99_ms": 248.10655737704917, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:48:17.842497+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "inventory-svc", "sample": 3, "latency_p99_ms": 95.20833333333331, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:48:17.843582+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_PASS", "service": "inventory-svc", "samples": 3}
{"ts": "2026-06-18T14:48:17.844130+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_SUCCESS", "alertname": "HighLatency", "service": "inventory-svc", "runbook": "runbooks/restart_service.sh"}
{"ts": "2026-06-18T14:48:27.726036+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_SAMPLE", "service": "payment-svc", "sample": 4, "latency_p99_ms": 248.125, "up": 1.0, "latency_ok": true, "up_ok": true}
{"ts": "2026-06-18T14:48:27.727043+00:00", "logger": "verify", "level": "INFO", "event_type": "VERIFY_PASS", "service": "payment-svc", "samples": 4}
{"ts": "2026-06-18T14:48:27.727644+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ACTION_SUCCESS", "alertname": "HighLatency", "service": "payment-svc", "runbook": "runbooks/restart_service.sh"}
```

---

## Scenario 6 — LLM Hallucination Defense

**Log output:**
```json
{"ts": "2026-06-18T14:48:33.932951+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ORCHESTRATOR_START", "config": "config.yaml", "dry_run": false, "poll_interval_s": 15}
{"ts": "2026-06-18T14:48:48.982145+00:00", "logger": "orchestrator", "level": "INFO", "event_type": "ALERT_DETECTED", "alertname": "TestHallucination", "service": "payment-svc", "severity": "critical"}
{"ts": "2026-06-18T14:48:48.982145+00:00", "logger": "orchestrator", "level": "ERROR", "event_type": "DECISION_VALIDATION_FAILED", "bad_runbook": "runbooks/nonexistent_runbook.sh", "alertname": "TestHallucination", "raw_decision": "runbooks/nonexistent_runbook.sh", "action": "escalate_no_auto_action"}
```
