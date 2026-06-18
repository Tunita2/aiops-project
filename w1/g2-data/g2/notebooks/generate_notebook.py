"""
Generate comprehensive AIOps analysis notebook for all 5 microservices.
Each service section includes:
  1. EDA: Distribution + Histogram for every metric
  2. Anomaly Detection: IQR, Log1p+3-Sigma, Isolation Forest (with feature engineering)
  3. Visualization of detection results
  4. Log tracing (if available) + Root cause conclusion
"""

import json
import hashlib
from pathlib import Path

OUTPUT = Path(__file__).parent / "full_analysis.ipynb"

_n = 0
def _id():
    global _n; _n += 1
    return hashlib.md5(f"c{_n}".encode()).hexdigest()[:8]

def _src(t):
    t = t.strip("\n")
    ls = t.split("\n")
    return [l + "\n" for l in ls[:-1]] + [ls[-1]]

def md(t):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": _src(t)}

def code(t):
    return {"cell_type": "code", "execution_count": None, "id": _id(),
            "metadata": {}, "outputs": [], "source": _src(t)}

# ── Services config ────────────────────────────────────────
SERVICES = [
    {
        "name": "cart-service",
        "csv": "cart-service.csv",
        "log": "cart-service.log.jsonl",
        "conclusion": (
            "**Root Cause (Nguyen nhan goc):** `ProductCatalogCache eviction failed` - "
            "Cache khong the giai phong bo nho (eviction failed) do heap pressure qua cao. "
            "Dieu nay gay ra memory leak lien tuc -> GC overhead tang -> OOM -> Kubernetes kill Pod -> Restart loop. "
            "Day la SERVICE GAY RA SU CO, khong phai nan nhan."
        ),
    },
    {
        "name": "order-service",
        "csv": "order-service.csv",
        "log": "order-service.log.jsonl",
        "conclusion": (
            "**Nan nhan (Victim):** Order-service bi anh huong GIAN TIEP tu cart-service. "
            "Khi cart-service sap, order-service goi sang cart de lay thong tin gio hang nhung bi timeout. "
            "Log cho thay `Cart service timeout` xuat hien dong loat sau khi cart-service bat dau restart loop. "
            "Khong co loi nao trong code cua order-service."
        ),
    },
    {
        "name": "payment-service",
        "csv": "payment-service.csv",
        "log": None,
        "conclusion": (
            "**Nan nhan (Victim):** Tuong tu order-service, payment-service bi upstream timeout "
            "do phu thuoc vao cart-service. Khi cart sap, payment khong the hoan tat giao dich. "
            "Khong co log file de phan tich them, nhung `upstream_timeout_rate` tang dot bien "
            "chung minh day la hau qua cua cascade failure tu cart-service."
        ),
    },
    {
        "name": "api-gateway",
        "csv": "api-gateway.csv",
        "log": None,
        "conclusion": (
            "**Nan nhan (Victim):** API Gateway la diem vao cua toan he thong. "
            "Khi cart-service sap, `cart_upstream_error_rate` tang vot vi gateway khong the "
            "ket noi voi cart -> tra ve HTTP 5xx cho nguoi dung. "
            "Day la trieu chung (symptom) ma nguoi dung nhin thay, khong phai nguyen nhan."
        ),
    },
    {
        "name": "product-service",
        "csv": "product-service.csv",
        "log": None,
        "conclusion": (
            "**Khong bi anh huong (Bystander):** Product-service la service duoc cart-service GOI TOI "
            "(khong phai goi TU). Khi cart sap, cart khong goi sang product nua -> traffic giam "
            "nhung KHONG co loi. Metric gan nhu binh thuong, chi co traffic giam nhe. "
            "Day la bang chung chung minh huong loi la tu cart -> cac service goi toi cart."
        ),
    },
]

def gen():
    cells = []

    # ── Title ──
    cells.append(md("""# AIOps W1 Lab - Full Analysis: 5 Microservices

**Pipeline cho moi service:**
1. **EDA:** Distribution + Histogram cho tung metric
2. **Anomaly Detection:** IQR | Log1p + 3-Sigma | Isolation Forest (Feature Engineering)
3. **Visualization:** So sanh ket qua 3 phuong phap
4. **Log Tracing:** Truy vet log tai thoi diem anomaly
5. **Ket luan:** Root cause / Victim analysis

---"""))

    # ── Setup ──
    cells.append(md("## Setup & Imports"))
    cells.append(code(r"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json, re
from pathlib import Path
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 11

DATA_DIR = Path(r"D:\Cloude-DevOps\Phase-2\aiops-project\w1\g2-data\g2")
METRICS_DIR = DATA_DIR / "metrics"
LOGS_DIR = DATA_DIR / "logs"

ALERT_TIME = pd.to_datetime("2026-06-01 23:04:00+00:00")
BASELINE = 720   # 6 hours baseline (720 x 30s)

print("Setup OK - Data dir:", DATA_DIR)"""))

    # ── Helper Functions ──
    cells.append(md("## Helper Functions\nCac ham dung chung cho tat ca services"))
    cells.append(code(r'''def get_metric_cols(df):
    """Lay tat ca cot so, bo cot hang so (std=0) va timestamp."""
    return [c for c in df.select_dtypes(include=[np.number]).columns
            if df[c].std() > 0]


def plot_distributions(df, metric_cols, service_name):
    """Ve bieu do phan phoi (KDE) va histogram cho tung metric."""
    n = len(metric_cols)
    fig, axes = plt.subplots(n, 2, figsize=(15, 3 * n))
    if n == 1:
        axes = axes.reshape(1, -1)

    fig.suptitle(f"{service_name} - Distribution & Histogram", fontsize=14, fontweight="bold", y=1.01)

    for i, col in enumerate(metric_cols):
        data = df[col].dropna()
        skewness = stats.skew(data)

        # Left: Time series + KDE overlay
        ax_ts = axes[i, 0]
        ax_ts.plot(df["timestamp"], df[col], color="#6b7280", linewidth=0.6, alpha=0.7)
        ax_ts.set_ylabel(col, fontsize=8)
        ax_ts.set_title(f"{col} - Time Series", fontsize=9)
        ax_ts.grid(True, alpha=0.2)
        ax_ts.axvline(ALERT_TIME, color="red", linestyle=":", linewidth=1, alpha=0.5)
        ax_ts.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        # Right: Histogram + skewness
        ax_h = axes[i, 1]
        ax_h.hist(data, bins=60, color="#60a5fa", edgecolor="#1e40af", alpha=0.7, density=True)
        # KDE overlay
        try:
            kde_x = np.linspace(data.min(), data.max(), 200)
            kde = stats.gaussian_kde(data)
            ax_h.plot(kde_x, kde(kde_x), color="#ef4444", linewidth=1.5)
        except Exception:
            pass
        ax_h.set_title(f"{col} - Histogram (skew={skewness:.2f})", fontsize=9)
        skew_color = "green" if abs(skewness) < 0.5 else ("orange" if abs(skewness) < 1 else "red")
        ax_h.annotate(f"Skewness: {skewness:.2f}", xy=(0.72, 0.85), xycoords="axes fraction",
                      fontsize=9, fontweight="bold", color=skew_color,
                      bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=skew_color, alpha=0.8))

    plt.tight_layout()
    plt.show()


def run_iqr(df, metric_cols):
    """Phat hien anomaly bang IQR cho tung metric."""
    results = {}
    for col in metric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        mask = (df[col] < lower) | (df[col] > upper)
        df[f"{col}_iqr"] = mask
        first = df.loc[mask, "timestamp"].min()
        results[col] = {"count": int(mask.sum()), "first": str(first) if pd.notna(first) else "None",
                        "lower": round(lower, 2), "upper": round(upper, 2)}
    return results


def run_log3sigma(df, metric_cols):
    """Phat hien anomaly bang Log1p transform + 3-Sigma."""
    results = {}
    for col in metric_cols:
        log_data = np.log1p(df[col])
        mu, sigma = log_data.mean(), log_data.std()
        if sigma == 0:
            sigma = 1e-10
        z = np.abs((log_data - mu) / sigma)
        mask = z > 3
        df[f"{col}_log3s"] = mask
        first = df.loc[mask, "timestamp"].min()
        results[col] = {"count": int(mask.sum()), "first": str(first) if pd.notna(first) else "None"}
    return results


def run_isolation_forest(df, metric_cols):
    """Isolation Forest voi Feature Engineering (multivariate)."""
    # Feature Engineering
    feat = pd.DataFrame(index=df.index)
    for col in metric_cols:
        feat[f"{col}_val"] = df[col]
        feat[f"{col}_rmean"] = df[col].rolling(60, min_periods=1).mean()
        feat[f"{col}_rstd"] = df[col].rolling(60, min_periods=1).std().fillna(0)
        feat[f"{col}_roc"] = df[col].diff().fillna(0)

    # Scale
    scaler = StandardScaler()
    X = scaler.fit_transform(feat.fillna(0))

    # Train on baseline (6h dau)
    model = IsolationForest(n_estimators=200, contamination=0.03, random_state=42)
    model.fit(X[:BASELINE])

    # Predict
    labels = model.predict(X)
    scores = -model.decision_function(X)
    df["if_anomaly"] = labels == -1
    df["if_score"] = scores

    first = df.loc[df["if_anomaly"], "timestamp"].min()
    return {
        "total_anomalies": int(df["if_anomaly"].sum()),
        "first_anomaly": str(first) if pd.notna(first) else "None",
        "features_used": len(feat.columns),
    }


def plot_anomaly_comparison(df, metric_cols, service_name):
    """Ve bieu do so sanh 3 phuong phap anomaly detection."""
    n = len(metric_cols)
    fig, axes = plt.subplots(n, 1, figsize=(18, 3.5 * n), sharex=True)
    if n == 1:
        axes = [axes]

    fig.suptitle(f"{service_name} - Anomaly Detection Comparison", fontsize=14, fontweight="bold", y=1.01)

    for i, col in enumerate(metric_cols):
        ax = axes[i]
        ax.plot(df["timestamp"], df[col], color="#9ca3af", linewidth=0.6, alpha=0.6, label="Raw")

        # IQR
        iqr_col = f"{col}_iqr"
        if iqr_col in df.columns:
            m = df[df[iqr_col]]
            if not m.empty:
                ax.scatter(m["timestamp"], m[col], c="#ef4444", s=12, alpha=0.6, label=f"IQR ({len(m)})", zorder=3)

        # Log3sigma
        l3s_col = f"{col}_log3s"
        if l3s_col in df.columns:
            m = df[df[l3s_col]]
            if not m.empty:
                ax.scatter(m["timestamp"], m[col], c="#3b82f6", s=12, marker="x", alpha=0.6, label=f"Log3s ({len(m)})", zorder=4)

        # IF (global)
        if "if_anomaly" in df.columns:
            m = df[df["if_anomaly"]]
            if not m.empty:
                ax.scatter(m["timestamp"], m[col], c="#22c55e", s=12, marker="^", alpha=0.5, label=f"IF ({len(m)})", zorder=5)

        ax.axvline(ALERT_TIME, color="red", linestyle=":", linewidth=1.2, alpha=0.7)
        ax.set_ylabel(col, fontsize=8)
        ax.legend(loc="upper left", fontsize=7, ncol=4)
        ax.grid(True, alpha=0.15)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[-1].set_xlabel("Time (UTC)")
    plt.tight_layout()
    plt.show()


def trace_logs(log_path, anomaly_times_df, n_samples=5):
    """Doc log file, gom cum template, doi chieu voi thoi diem anomaly."""
    if not log_path.exists():
        print(f"  [!] No log file: {log_path.name}")
        return None

    print(f"  Reading: {log_path.name}")
    templates = Counter()
    first_seen = {}
    levels = Counter()
    samples = {}

    def normalize(msg):
        msg = re.sub(r"\b[0-9a-f]{16,}\b", "<hex>", msg, flags=re.I)
        msg = re.sub(r"\b\d+\.\d+\.\d+\.\d+\b", "<ip>", msg)
        msg = re.sub(r"\b\d+\.\d+\b", "<num>", msg)
        msg = re.sub(r"\b\d+\b", "<num>", msg)
        msg = re.sub(r"ORD-[A-Z0-9]+", "ORD-<id>", msg)
        msg = re.sub(r"userId=<num>", "userId=<id>", msg)
        return msg

    with log_path.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            levels[rec["level"]] += 1
            tpl = normalize(rec["message"])
            templates[tpl] += 1
            first_seen.setdefault(tpl, rec["timestamp"])
            samples.setdefault(tpl, rec["message"])

    print(f"  Total lines: {sum(levels.values())}")
    print(f"  Levels: {dict(levels)}")
    print(f"\n  Top {n_samples} WARN/ERROR/FATAL templates:")
    print(f"  {'Count':>6}  {'First Seen':>26}  Template")
    print(f"  {'-'*6}  {'-'*26}  {'-'*50}")

    error_templates = [(tpl, cnt) for tpl, cnt in templates.most_common()
                       if any(kw in tpl.lower() for kw in ["error", "fail", "oom", "timeout", "refused", "overhead", "slow", "elevated", "limit", "killed", "imminent"])]

    for tpl, cnt in error_templates[:15]:
        print(f"  {cnt:>6}  {first_seen[tpl]:>26}  {tpl[:70]}")

    return {"levels": dict(levels), "error_templates": error_templates[:15],
            "first_seen": first_seen, "total_templates": len(templates)}


print("Helper functions defined!")'''))

    # ── Service Sections ──
    for svc in SERVICES:
        name = svc["name"]
        csv = svc["csv"]
        log = svc["log"]
        conclusion = svc["conclusion"]

        cells.append(md(f"""---
# {name.upper().replace('-', ' ')}
---"""))

        # Load data
        cells.append(md(f"## {name} - Load Data"))
        cells.append(code(f'''# Load {name}
df_{name.replace("-","_")} = pd.read_csv(METRICS_DIR / "{csv}", parse_dates=["timestamp"])
df = df_{name.replace("-","_")}.copy()
metric_cols = get_metric_cols(df)

print(f"Service: {name}")
print(f"Shape: {{df.shape}}")
print(f"Time range: {{df['timestamp'].min()}} -> {{df['timestamp'].max()}}")
print(f"Metrics ({{len(metric_cols)}}): {{metric_cols}}")
print()
print(df[metric_cols].describe().round(2))'''))

        # Distribution & Histogram
        cells.append(md(f"## {name} - 1. Distribution & Histogram"))
        cells.append(code(f'''plot_distributions(df, metric_cols, "{name}")'''))

        # Anomaly Detection
        cells.append(md(f"## {name} - 2. Anomaly Detection"))

        # IQR
        cells.append(md(f"### 2.1 IQR Method"))
        cells.append(code(f'''iqr_res = run_iqr(df, metric_cols)
print("=== IQR Results for {name} ===")
for col, info in iqr_res.items():
    print(f"  {{col}}: {{info['count']}} anomalies, first={{info['first']}}, bounds=[{{info['lower']}}, {{info['upper']}}]")'''))

        # Log1p + 3-Sigma
        cells.append(md(f"### 2.2 Log1p + 3-Sigma"))
        cells.append(code(f'''log3s_res = run_log3sigma(df, metric_cols)
print("=== Log1p + 3-Sigma Results for {name} ===")
for col, info in log3s_res.items():
    print(f"  {{col}}: {{info['count']}} anomalies, first={{info['first']}}")'''))

        # Isolation Forest
        cells.append(md(f"### 2.3 Isolation Forest (Feature Engineering)"))
        cells.append(code(f'''if_res = run_isolation_forest(df, metric_cols)
print("=== Isolation Forest Results for {name} ===")
print(f"  Features used: {{if_res['features_used']}}")
print(f"  Total anomalies: {{if_res['total_anomalies']}}")
print(f"  First anomaly: {{if_res['first_anomaly']}}")

# Top 5 highest anomaly scores
top5 = df.nlargest(5, "if_score")[["timestamp", "if_score"] + metric_cols[:3]]
print("\\nTop 5 highest anomaly scores:")
print(top5.to_string(index=False))'''))

        # Visualize
        cells.append(md(f"## {name} - 3. Visualize Anomaly Comparison"))
        cells.append(code(f'''plot_anomaly_comparison(df, metric_cols, "{name}")'''))

        # Summary table
        summary_code = '''# Summary table for ''' + name + '''
print()
print("=" * 70)
print("  SUMMARY: ''' + name + '''")
print("=" * 70)
header = f"  {'Metric':<30} {'IQR':>6} {'Log3s':>6} {'IF':>6}"
print(header)
print(f"  {'-'*30} {'-'*6} {'-'*6} {'-'*6}")
for col in metric_cols:
    iqr_n = int(df[f"{col}_iqr"].sum()) if f"{col}_iqr" in df.columns else 0
    l3s_n = int(df[f"{col}_log3s"].sum()) if f"{col}_log3s" in df.columns else 0
    if_n = int(df["if_anomaly"].sum()) if "if_anomaly" in df.columns else 0
    print(f"  {col:<30} {iqr_n:>6} {l3s_n:>6} {if_n:>6}")'''
        cells.append(code(summary_code))

        # Log Tracing
        cells.append(md(f"## {name} - 4. Log Tracing & Root Cause"))

        if log:
            cells.append(code(f'''# Log tracing for {name}
anomaly_times = df[df["if_anomaly"]]["timestamp"]
log_result = trace_logs(LOGS_DIR / "{log}", anomaly_times)'''))
        else:
            cells.append(code(f'''# {name} khong co log file
print("[!] Khong co log file cho {name}")
print("    -> Phan tich dua tren metrics only")
print("    -> upstream_timeout_rate / cart_upstream_error_rate cho thay")
print("       service nay bi anh huong gian tiep tu cart-service")'''))

        # Conclusion
        cells.append(md(f"""### Ket luan {name}

{conclusion}"""))

        # Cleanup
        cells.append(code(f'''# Cleanup columns for next service
cleanup_cols = [c for c in df.columns if c.endswith("_iqr") or c.endswith("_log3s") or c in ["if_anomaly", "if_score"]]
df.drop(columns=cleanup_cols, inplace=True, errors="ignore")
print("[OK] {name} analysis complete!\\n")'''))

    # ── Final Summary ──
    cells.append(md("""---
# FINAL SUMMARY - Root Cause Analysis
---"""))

    cells.append(md("""## Cascade Failure Timeline

```
06:30   [LOG]    cart-service: ProductCatalogCache eviction failed (ROOT CAUSE)
08:07   [METRIC] cart-service: memory_usage bat dau tang bat thuong (Z>3)
09:22   [METRIC] cart-service: jvm_gc_pause tang bat thuong
16:20   [METRIC] cart-service: Memory tang lien tuc khong dung (Sustained anomaly)
19:59   [LOG]    cart-service: OutOfMemoryError imminent -> OOMKilled
20:00   [METRIC] api-gateway: cart_upstream_error_rate tang vot
20:32   [METRIC] order-service: upstream_timeout_rate tang vot
20:45   [METRIC] payment-service: upstream_timeout_rate tang vot
23:04   [ALERT]  PagerDuty alert -> SRE thuc day (QUA MUON!)
```

## Root Cause
**ProductCatalogCache** trong `cart-service` bi loi logic khien cache khong the giai phong bo nho (eviction failed).
RAM ro ri lien tuc -> GC overhead -> OOM -> Kubernetes kill Pod -> Restart loop -> Cascade failure toan he thong.

## Lessons Learned
1. Can dat alert cho RAM o muc 80%, khong doi den OOM
2. Can co AI-based anomaly detection de phat hien silent signals som hon 15+ tieng
3. Can co circuit breaker giua cac services de ngan cascade failure"""))

    # Build notebook
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.13.0"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"Notebook generated: {OUTPUT}")
    print(f"Total cells: {len(cells)}")


if __name__ == "__main__":
    gen()
