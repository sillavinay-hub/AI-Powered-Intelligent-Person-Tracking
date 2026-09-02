#!/usr/bin/env python3
"""
Research Experiment Script: evaluate_fusion.py
Quantitatively evaluates Face Only vs ReID Only vs Multimodal Fusion across the 25-camera resort.
"""
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ai.fusion.experiment_runner import experiment_runner

def main():
    parser = argparse.ArgumentParser(description="ResortVision AI - Multimodal Fusion Benchmark")
    parser.add_argument("--samples", type=int, default=150, help="Number of evaluation sequences")
    parser.add_argument("--output", type=str, default="experiments/benchmark_results.json", help="Output file path")
    args = parser.parse_args()

    print("=" * 80)
    print("RESORTVISION AI - RESEARCH EXPERIMENT BENCHMARK EVALUATION")
    print("=" * 80)
    print(f"Running evaluation with {args.samples} multi-camera test instances...")

    results = experiment_runner.run_benchmark(num_samples=args.samples)

    # Print markdown table format
    print("\n### Quantitative Performance Comparison\n")
    headers = ["Configuration", "Accuracy (%)", "Precision (%)", "Recall (%)", "Rank-1 (%)", "mAP (%)", "IDF1 (%)", "MOTA (%)", "ID Switches", "Latency (ms)"]
    print(f"| {' | '.join(headers)} |")
    print(f"|{'---|' * len(headers)}")

    for exp in results["experiments"]:
        row = [
            exp["name"],
            f"{exp['accuracy']:.1f}",
            f"{exp['precision']:.1f}",
            f"{exp['recall']:.1f}",
            f"{exp['reid_rank1']:.1f}",
            f"{exp['reid_map']:.1f}",
            f"{exp['idf1']:.1f}",
            f"{exp['mota']:.1f}",
            str(exp["id_switches"]),
            f"{exp['latency_ms']:.1f}"
        ]
        print(f"| {' | '.join(row)} |")

    print("\n" + results["research_conclusion"] + "\n")

    # Save to json
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved successfully to: {out_path}")

if __name__ == "__main__":
    main()
