# AIOps W1 Lab - Detect & Triage Analysis

## 📁 Project Structure

```
g2/
├── metrics/              # Raw metrics data (CSV)
├── logs/                 # Raw log data (JSONL)
├── notebooks/            # Analysis scripts and outputs
│   ├── 01-eda.py
│   ├── 02-anomaly-detection.py
│   ├── 03-log-clustering.py
│   ├── 03-log-metrics-fusion.py
│   └── *.png, *.txt     # Generated outputs
├── FINDINGS.md           # Postmortem report
├── SUBMIT.md             # Group reflection
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install pandas matplotlib seaborn scikit-learn drain3
```

### Run Analysis (in order)

1. **Phase 1: Exploratory Data Analysis**

```bash
cd g2/notebooks
python 01-eda.py
```

Outputs: `01-multi_service_timeline.png`, `01-correlation_heatmap.png`

2. **Phase 2: Anomaly Detection**

```bash
python 02-anomaly-detection.py
```

Outputs: `02-multi_metric_anomaly.png` + anomaly detection table

3. **Phase 3: Log Clustering**

```bash
python 03-log-clustering.py
```

Output: `03-log_clusters.txt`

4. **Phase 4: Log-Metrics Fusion**

```bash
python 03-log-metrics-fusion.py
```

Output: `03-log_metrics_fusion.txt`

## 📊 Key Findings

- **When:** First anomaly detected at `01:55:30`, alert triggered at `23:04:00`
- **Where:** `cart-service` memory leak → cascading to order/payment services
- **What:** ProductCatalogCache eviction failure → GC overhead → OOM → restart loop

See `FINDINGS.md` for detailed postmortem analysis.

## 🎯 Deliverables Checklist

- [x] Code reproducible from raw data
- [x] Multi-service & multi-metric analysis
- [x] 2 anomaly detection methods (Z-score + Isolation Forest)
- [x] Log analysis with Drain3 clustering
- [x] FINDINGS.md with WHEN/WHERE/WHAT answers
- [x] SUBMIT.md with group reflection
- [x] Evidence: 4 charts + 2 analysis reports

## 📖 Methodology

### Anomaly Detection Approaches

1. **Z-Score (Statistical)**
   - Rolling window: 60 datapoints (30 minutes)
   - Threshold: 3-sigma
   - Fast, interpretable, good for univariate analysis

2. **Isolation Forest (ML)**
   - Contamination: 0.05 (5% expected anomalies)
   - Features: 4 metrics (memory, GC, 5xx, CPU)
   - Better at capturing multivariate patterns

### Log Analysis

- **Tool:** Drain3 (log template mining)
- **Coverage:** cart-service (24K lines) + order-service (8K lines)
- **Key patterns:** OOMKilled, GC overhead, cache eviction failures

## 📝 References

- [Drain3 Documentation](https://github.com/logpai/Drain3)
- [Isolation Forest Paper](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf)
- [AIOps Best Practices](https://sre.google/workbook/practical-alerting/)
