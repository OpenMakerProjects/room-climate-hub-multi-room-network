#!/usr/bin/env python3
"""Room Climate Hub Multi-Room Network: runnable simulation-first controller."""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass

PROJECT_ID = 8
MODE = "telemetry"
DEFAULT_THRESHOLD = 0.53


@dataclass(frozen=True)
class Snapshot:
    timestamp: float
    values: list[float]
    score: float
    valid: bool


class Controller:
    def __init__(self, threshold: float = DEFAULT_THRESHOLD, confirmations: int = 2) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold
        self.confirmations_required = max(1, confirmations)
        self.confirmations = 0
        self.output_active = False

    def evaluate(self, values: list[float], timestamp: float | None = None) -> Snapshot:
        valid = bool(values) and all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values)
        score = sum(values) / len(values) if valid else 0.0
        condition = valid and score >= self.threshold
        self.confirmations = min(self.confirmations + 1, self.confirmations_required) if condition else 0
        self.output_active = valid and self.confirmations >= self.confirmations_required
        return Snapshot(timestamp or time.time(), values, score, valid)


def simulated_values(step: int) -> list[float]:
    phase = step / 5.0 + PROJECT_ID / 17.0
    return [round((math.sin(phase + offset) + 1.0) / 2.0, 4) for offset in (0.0, 1.4, 2.8)]


def run(iterations: int, interval: float, threshold: float) -> None:
    controller = Controller(threshold=threshold)
    for step in range(iterations):
        snapshot = controller.evaluate(simulated_values(step))
        record = asdict(snapshot) | {
            "project_id": PROJECT_ID,
            "mode": MODE,
            "state": "active" if controller.output_active else ("normal" if snapshot.valid else "fault"),
            "output": controller.output_active,
        }
        print(json.dumps(record, sort_keys=True))
        if interval > 0:
            time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    options = parser.parse_args()
    run(max(1, options.iterations), max(0.0, options.interval), options.threshold)
