"""
Visualize All Services — Auto-scan metrics + Isolation Forest Anomaly Detection
================================================================================
Tự động quét toàn bộ thư mục metrics, mỗi service tạo 1 biểu đồ gồm
tất cả metrics của service đó, với anomaly points được đánh dấu bằng IF.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ── Đường dẫn ──────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent
METRICS_DIR = DATA_DIR / "metrics"
OUTPUT_DIR = DATA_DIR / "notebooks"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Thời điểm alert chính thức (PagerDuty) theo đề bài
ALERT_TIME = pd.to_datetime("2026-06-01 23:04:00+00:00")

# Baseline: dùng 6 giờ đầu (720 điểm × 30s) để train IF
BASELINE_POINTS = 720


def detect_anomalies_if(df: pd.DataFrame, metric_cols: list[str]) -> pd.DataFrame:
    """
    Áp dụng Isolation Forest lên TẤT CẢ metrics của 1 service cùng lúc (Multivariate).
    Trả về DataFrame gốc với thêm cột 'if_anomaly' (bool) và 'if_score' (float).
    """
    X = df[metric_cols].copy()

    # Chuẩn hóa dữ liệu (StandardScaler) để các metric có scale khác nhau
    # (bytes vs percent vs ms) được đưa về cùng thang đo
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train IF trên baseline (6h đầu — lúc hệ thống còn khỏe)
    model = IsolationForest(
        n_estimators=200,
        contamination=0.03,    # Ước lượng 3% data là anomaly
        random_state=42,
    )
    model.fit(X_scaled[:BASELINE_POINTS])

    # Predict trên toàn bộ 24h
    df = df.copy()
    df["if_anomaly"] = model.predict(X_scaled) == -1
    df["if_score"] = -model.decision_function(X_scaled)  # Càng cao càng bất thường
    return df


def plot_service(service_name: str, df: pd.DataFrame, metric_cols: list[str]) -> None:
    """
    Vẽ 1 figure cho 1 service, gồm N subplots (1 subplot per metric).
    Mỗi subplot hiển thị:
      - Đường metric gốc (xám)
      - Các điểm IF anomaly (đỏ)
      - Đường kẻ dọc đánh dấu thời điểm alert 23:04 (đỏ nét đứt)
    """
    n_metrics = len(metric_cols)
    fig, axes = plt.subplots(n_metrics, 1, figsize=(18, 3.5 * n_metrics), sharex=True)

    # Nếu chỉ có 1 metric, axes không phải list → wrap lại
    if n_metrics == 1:
        axes = [axes]

    fig.suptitle(
        f"Service: {service_name}  —  Isolation Forest Anomaly Detection",
        fontsize=16, fontweight="bold", y=1.01,
    )

    anomaly_mask = df["if_anomaly"]

    for i, col in enumerate(metric_cols):
        ax = axes[i]

        # Vẽ đường metric gốc
        ax.plot(df["timestamp"], df[col], color="#6b7280", alpha=0.6, linewidth=0.8, label="Raw data")

        # Vẽ các điểm anomaly (IF)
        anom = df[anomaly_mask]
        if not anom.empty:
            ax.scatter(
                anom["timestamp"], anom[col],
                color="#ef4444", s=12, zorder=5,
                label=f"IF Anomaly ({len(anom)} points)",
                alpha=0.7,
            )

        # Đánh dấu thời điểm alert chính thức 23:04
        ax.axvline(x=ALERT_TIME, color="#ef4444", linestyle=":", linewidth=1.5, label="Alert 23:04")

        # Tô vùng baseline (6h đầu)
        baseline_end = df["timestamp"].iloc[BASELINE_POINTS - 1]
        ax.axvspan(df["timestamp"].iloc[0], baseline_end, color="#22c55e", alpha=0.06, label="Baseline (train)")

        # Tìm thời điểm anomaly đầu tiên SAU baseline
        anom_after_baseline = anom[anom["timestamp"] > baseline_end]
        if not anom_after_baseline.empty:
            first_anomaly_time = anom_after_baseline["timestamp"].iloc[0]
            ax.axvline(x=first_anomaly_time, color="#f59e0b", linestyle="--", linewidth=1.2, label=f"First anomaly: {first_anomaly_time.strftime('%H:%M')}")

        # Định dạng
        ax.set_ylabel(col, fontsize=9, rotation=0, ha="right", labelpad=10)
        ax.yaxis.set_label_coords(-0.01, 0.5)
        ax.legend(loc="upper left", fontsize=7, ncol=2)
        ax.grid(True, alpha=0.2)
        ax.tick_params(axis="y", labelsize=8)

    # Định dạng trục thời gian
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=2))
    axes[-1].set_xlabel("Time (UTC)", fontsize=10)
    plt.xticks(rotation=45)

    plt.tight_layout()
    out_path = OUTPUT_DIR / f"viz_{service_name.replace('-', '_')}.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] Saved: {out_path.name}")


def main() -> None:
    print("=" * 60)
    print("  AUTO-SCAN ALL SERVICES — IF Anomaly Detection")
    print("=" * 60)

    # Quét toàn bộ file CSV trong thư mục metrics
    csv_files = sorted(METRICS_DIR.glob("*.csv"))
    print(f"\nFound {len(csv_files)} service files in {METRICS_DIR}\n")

    summary_rows = []

    for csv_path in csv_files:
        service_name = csv_path.stem  # e.g. "cart-service"
        print(f"-- Processing: {service_name} --")

        # Đọc CSV
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])

        # Tự động lấy TẤT CẢ cột số (bỏ timestamp + cột không phải số)
        metric_cols = [
            c for c in df.select_dtypes(include=[np.number]).columns
            if c != "timestamp"
        ]
        print(f"   Metrics found: {metric_cols}")

        # Bỏ cột hằng số (ví dụ memory_limit_bytes luôn = 2GB, không có gì để detect)
        metric_cols = [c for c in metric_cols if df[c].std() > 0]
        print(f"   Metrics used (non-constant): {metric_cols}")

        # Áp dụng Isolation Forest
        df = detect_anomalies_if(df, metric_cols)

        # Tìm thời điểm anomaly đầu tiên cho summary
        anomalies = df[df["if_anomaly"]]
        first_anomaly = anomalies["timestamp"].min() if not anomalies.empty else None

        summary_rows.append({
            "Service": service_name,
            "Metrics Count": len(metric_cols),
            "Total Points": len(df),
            "Anomaly Points": len(anomalies),
            "Anomaly %": f"{len(anomalies) / len(df) * 100:.1f}%",
            "First Anomaly": str(first_anomaly) if first_anomaly else "None",
        })

        # Vẽ biểu đồ
        plot_service(service_name, df, metric_cols)

    # In bảng tóm tắt
    summary_df = pd.DataFrame(summary_rows)
    print("\n" + "=" * 60)
    print("  SUMMARY — First Anomaly Detection per Service")
    print("=" * 60)
    print(summary_df.to_string(index=False))
    print()


if __name__ == "__main__":
    main()
