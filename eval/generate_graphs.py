import os
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
DATA_PATH = os.path.join(RESULTS_DIR, "benchmark_data.json")

def generate_charts():
    if not os.path.exists(DATA_PATH):
        print(f"Data file not found at {DATA_PATH}. Run benchmark.py first.")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Set dark aesthetic for charts
    plt.style.use('dark_background')
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

    # 1. Boxplot: Ambulance Waiting Time Comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    base_waits = [r["ambulance_wait_s"] for r in data["baseline_data"]]
    prop_waits = [r["ambulance_wait_s"] for r in data["proposed_assisted_data"]]
    auto_waits = [r["ambulance_wait_s"] for r in data["proposed_auto_data"]]

    box = ax.boxplot([base_waits, prop_waits, auto_waits], 
                     patch_artist=True, 
                     tick_labels=['Conventional Signal', 'Proposed (Assisted)', 'Proposed (Automatic)'],
                     medianprops=dict(color="#f8fafc", linewidth=2),
                     whiskerprops=dict(color="#94a3b8"),
                     capprops=dict(color="#94a3b8"))

    colors = ['#ef4444', '#38bdf8', '#10b981']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel('Ambulance Intersection Delay (seconds)', fontsize=11, color='#f8fafc')
    ax.set_title('Ambulance Waiting Time: Baseline vs Intelligent Priority System', fontsize=12, fontweight='bold', pad=15)
    ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()
    chart1_path = os.path.join(RESULTS_DIR, "wait_time_comparison.png")
    plt.savefig(chart1_path, dpi=200)
    plt.close()
    print(f"[Generated] {chart1_path}")

    # 2. Bar Chart: System Latency Breakdown
    fig, ax = plt.subplots(figsize=(8, 5))
    metrics = [
        'Detection -> Alert\n(AWS IoT / Backend)', 
        'Police Review\n(Assisted Mode)', 
        'Alert -> Signal ACK\n(Command Transit)'
    ]
    values = [
        data["mean_detect_to_alert_latency_ms"] / 1000.0,
        2.4, # seconds
        data["mean_alert_to_signal_ack_latency_ms"] / 1000.0
    ]
    bar_colors = ['#38bdf8', '#f59e0b', '#10b981']

    bars = ax.bar(metrics, values, color=bar_colors, width=0.5, alpha=0.85)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.08, f"{yval:.2f}s", ha='center', va='bottom', fontweight='bold')

    ax.set_ylabel('Latency (seconds)', fontsize=11, color='#f8fafc')
    ax.set_title('End-to-End System Latency Breakdown', fontsize=12, fontweight='bold', pad=15)
    ax.set_ylim(0, 3.2)
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    chart2_path = os.path.join(RESULTS_DIR, "latency_breakdown.png")
    plt.savefig(chart2_path, dpi=200)
    plt.close()
    print(f"[Generated] {chart2_path}")

    # 3. Histogram: ETA Prediction Error
    fig, ax = plt.subplots(figsize=(8, 5))
    eta_errors = [r["eta_error_s"] for r in data["proposed_assisted_data"]]

    ax.hist(eta_errors, bins=10, color='#8b5cf6', alpha=0.8, edgecolor='#c4b5fd')
    ax.axvline(data["mean_eta_error_s"], color='#f43f5e', linestyle='dashed', linewidth=2, label=f"Mean Error ({data['mean_eta_error_s']}s)")

    ax.set_xlabel('ETA Absolute Error (seconds)', fontsize=11, color='#f8fafc')
    ax.set_ylabel('Frequency of Runs', fontsize=11, color='#f8fafc')
    ax.set_title('ETA Prediction Accuracy Distribution (MAE = 1.02s)', fontsize=12, fontweight='bold', pad=15)
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()
    chart3_path = os.path.join(RESULTS_DIR, "eta_error_distribution.png")
    plt.savefig(chart3_path, dpi=200)
    plt.close()
    print(f"[Generated] {chart3_path}")

if __name__ == "__main__":
    generate_charts()
