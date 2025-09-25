import subprocess, sys

steps = [
    [sys.executable, "scripts/run_preprocess.py"],
    [sys.executable, "scripts/run_topic_modeling.py"],
    [sys.executable, "scripts/run_summarization_test.py"],
    [sys.executable, "scripts/run_sentiment_test.py"],
]

def main():
    for i, cmd in enumerate(steps, 1):
        print(f"\n=== Running step {i}/{len(steps)}: {' '.join(cmd)} ===")
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            print(f"Step {i} failed with code {proc.returncode}")
            sys.exit(proc.returncode)
    print("\nAll steps completed successfully.")

if __name__ == "__main__":
    main()
