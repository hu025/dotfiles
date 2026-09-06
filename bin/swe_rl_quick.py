#!/usr/bin/env python3
"""Quick wrapper around swe_rl_executor: file + task description → SWE-RL loop."""
import argparse, subprocess, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description="Quick SWE-RL run on a single file")
    ap.add_argument("file", help="Target file to refine (relative to cwd or absolute)")
    ap.add_argument("task", help="Task description for the SWE-RL loop")
    ap.add_argument("--max-iterations", type=int, default=5)
    ap.add_argument("--test-file", help="Optional test file path")
    args = ap.parse_args()

    target = Path(args.file).resolve()
    if not target.exists():
        sys.exit(f"file not found: {target}")

    cmd = ["python", str(Path.home() / ".hermes/scripts/swe_rl_executor.py"),
           "--file", str(target), "--task", args.task,
           "--max-iterations", str(args.max_iterations)]
    if args.test_file:
        cmd.extend(["--test-file", str(Path(args.test_file).resolve())])

    print(f"[swe_rl_quick] running: {' '.join(cmd)}", flush=True)
    sys.exit(subprocess.call(cmd))

if __name__ == "__main__":
    main()