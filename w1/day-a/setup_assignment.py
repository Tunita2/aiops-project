import nbformat as nbf

nb = nbf.v4.new_notebook()

markdown_1 = """# W1-D1 Assignment: Metric Anomaly Detection
## Phase 1: EDA & Hiểu Data
"""

code_1 = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf

# 1. Load data
df = pd.read_csv('machine_temperature_system_failure.csv', parse_dates=['timestamp'])
df.set_index('timestamp', inplace=True)

# Lấy nhãn ground truth
with open('combined_labels.json', 'r') as f:
    labels = json.load(f)
anomaly_timestamps = labels.get('realKnownCause/machine_temperature_system_failure.csv', [])
anomaly_timestamps = pd.to_datetime(anomaly_timestamps)

# 2. Plot raw time series
plt.figure(figsize=(15, 5))
plt.plot(df.index, df['value'], label='Machine Temperature')
for ts in anomaly_timestamps:
    plt.axvline(x=ts, color='red', alpha=0.5, linestyle='--')
plt.title('Raw Time Series with True Anomalies (Red Dashed)')
plt.legend()
plt.show()

# 3. Tính basic stats
print(f"Mean: {df['value'].mean():.2f}, Std: {df['value'].std():.2f}")
print(f"Skewness: {stats.skew(df['value']):.2f}")
print(f"Min: {df['value'].min():.2f}, Max: {df['value'].max():.2f}")

# 4. Plot histogram & density
plt.figure(figsize=(10, 4))
df['value'].plot(kind='hist', bins=50, density=True, alpha=0.5, color='blue')
df['value'].plot(kind='kde', color='red')
plt.title('Histogram & Density')
plt.show()

# 5. Plot ACF
fig, ax = plt.subplots(figsize=(15, 4))
plot_acf(df['value'], lags=1000, ax=ax)
plt.title('Autocorrelation Function (ACF)')
plt.show()
"""

markdown_2 = """## Phase 2 & 3: Implement 2 Detectors & So Sánh
Detector 1: Rolling Z-Score (3-Sigma)
Detector 2: Isolation Forest
"""

code_2 = """from sklearn.ensemble import IsolationForest
import joblib

# ----- DETECTOR 1: Rolling Z-Score -----
window_size = 60 # 1 tiếng data
threshold_z = 3.0

rolling_mean = df['value'].rolling(window=window_size, min_periods=1).mean()
rolling_std = df['value'].rolling(window=window_size, min_periods=1).std().replace(0, 1e-10)
z_scores = (df['value'] - rolling_mean) / rolling_std
df['zscore_anomaly'] = np.abs(z_scores) > threshold_z

# ----- DETECTOR 2: Isolation Forest -----
# Tạo feature table
features = pd.DataFrame({
    'value': df['value'],
    'rolling_mean': rolling_mean,
    'rolling_std': rolling_std,
    'rate_of_change': df['value'].diff()
}).dropna()

iso_forest = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
iso_forest.fit(features)
features['if_anomaly'] = iso_forest.predict(features) == -1

# Khôi phục lại df ban đầu
df['if_anomaly'] = False
df.loc[features.index, 'if_anomaly'] = features['if_anomaly']

# Save Model
joblib.dump(iso_forest, 'isolation_forest_model.pkl')

# ----- PLOT KẾT QUẢ -----
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

# Plot Z-Score
ax1.plot(df.index, df['value'], label='Value', color='blue')
ax1.scatter(df[df['zscore_anomaly']].index, df[df['zscore_anomaly']]['value'], color='red', label='Z-Score Anomaly')
ax1.set_title('Detector 1: Rolling Z-Score Anomalies')
ax1.legend()

# Plot IF
ax2.plot(df.index, df['value'], label='Value', color='blue')
ax2.scatter(df[df['if_anomaly']].index, df[df['if_anomaly']]['value'], color='orange', label='IF Anomaly')
ax2.set_title('Detector 2: Isolation Forest Anomalies')
ax2.legend()

plt.tight_layout()
plt.show()
"""

code_3 = """# ----- ĐÁNH GIÁ (EVALUATION) -----
def evaluate(predictions, true_anomalies, index):
    # Đơn giản hoá: Kiểm tra xem mỗi prediction có nằm gần true anomaly không (trong khoảng +- 1h)
    true_set = set(true_anomalies.dt.floor('H'))
    pred_set = set(index[predictions].floor('H'))
    
    tp = len(true_set.intersection(pred_set))
    fp = len(pred_set - true_set)
    fn = len(true_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1, fp

print("--- Z-Score Evaluation ---")
p_z, r_z, f1_z, fp_z = evaluate(df['zscore_anomaly'], anomaly_timestamps, df.index)
print(f"Precision: {p_z:.2f}, Recall: {r_z:.2f}, F1: {f1_z:.2f}, False Alarms: {fp_z}")

print("\\n--- Isolation Forest Evaluation ---")
p_if, r_if, f1_if, fp_if = evaluate(df['if_anomaly'], anomaly_timestamps, df.index)
print(f"Precision: {p_if:.2f}, Recall: {r_if:.2f}, F1: {f1_if:.2f}, False Alarms: {fp_if}")
"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(markdown_1),
    nbf.v4.new_code_cell(code_1),
    nbf.v4.new_markdown_cell(markdown_2),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_code_cell(code_3)
]

with open('assignment.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

submit_md = \"\"\"# W1-D1 Submission: Metric Anomaly Detection

## 1. EDA Reflection
- Data type: (Trả lời: Data có phân phối chuẩn hay skew? Có tính mùa vụ không?)
- Phương pháp đã chọn: Z-Score & Isolation Forest.

## 2. Model Tuning Logs
Thử nghiệm với tham số `contamination` của Isolation Forest:
1. Contamination = 0.01 -> Precision: ..., Recall: ..., F1: ...
2. Contamination = 0.02 -> Precision: ..., Recall: ..., F1: ...
3. Contamination = 0.05 -> Precision: ..., Recall: ..., F1: ...

## 3. Comparison
| Metric | Z-Score (3-Sigma) | Isolation Forest |
|---|---|---|
| Precision | ? | ? |
| Recall | ? | ? |
| F1 | ? | ? |
| False Alarms | ? | ? |

## 4. Final Reflection
- Model nào tốt hơn?
- Trade-off giữa 2 phương pháp?
- Production choice: (Tại sao ưu tiên recall trong AIOps?)
\"\"\"

with open('SUBMIT.md', 'w', encoding='utf-8') as f:
    f.write(submit_md)
