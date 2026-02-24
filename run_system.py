#!/usr/bin/env python
"""
SecurePOS AI System Launcher
Runs detector.py in background and streamlit app in foreground
"""
import subprocess
import os
import time
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🛡️  SecurePOS AI - Theft Detection System")
print("=" * 60)
print()

# Start detector in background
print("Starting detector...")
detector_process = subprocess.Popen(
    [sys.executable, "detector.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
print(f"✓ Detector started (PID: {detector_process.pid})")

# Wait for detector to initialize
time.sleep(2)

print()
print("Starting Streamlit dashboard...")
print("-" * 60)
print("Dashboard will open at: http://localhost:8501")
print("Press Ctrl+C to stop both services")
print("-" * 60)
print()

# Run streamlit in foreground
try:
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        check=False
    )
except KeyboardInterrupt:
    print("\n\nShutting down...")
    detector_process.terminate()
    detector_process.wait()
    print("✓ System stopped")
