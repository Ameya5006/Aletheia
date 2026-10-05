"""Deterministic healthcare acquisition and foundation inspection commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .foundation import (
    SPLIT_LOCK,
    acquire,
    build_split_lock,
    cohort,
    extract,
    feature_views,
    load_contracts,
    load_raw,
    partition,
    verify_split_lock,
    write_split_lock,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="UCI 296 healthcare data foundation")
    parser.add_argument("command", choices=("acquire", "lock", "verify"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/healthcare"))
    args = parser.parse_args()
    contracts = load_contracts()
    archive = args.raw_dir / "diabetes_130_us_hospitals_1999_2008.zip"
    if args.command == "acquire":
        acquire(contracts, archive)
    raw, _ = extract(contracts, archive, args.raw_dir)
    if args.command == "acquire":
        print(json.dumps({"archive": str(archive), "raw": str(raw)}, sort_keys=True))
        return
    frame = cohort(contracts, load_raw(contracts, raw))
    if args.command == "lock":
        write_split_lock(build_split_lock(contracts, frame), SPLIT_LOCK)
    else:
        verify_split_lock(contracts, frame, SPLIT_LOCK)
    train, test = partition(contracts, frame, SPLIT_LOCK)
    predictors, _ = feature_views(contracts, train)
    print(
        json.dumps(
            {
                "train": len(train),
                "test": len(test),
                "predictor_columns": list(predictors),
                "lock": str(SPLIT_LOCK),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
