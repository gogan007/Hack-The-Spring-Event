#!/usr/bin/env python
"""
Continuous Real-Time Demo
Simulates detector running continuously with proper time synchronization
"""
import json
import time
import os
from datetime import timedelta

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load POS transactions
import pandas as pd
pos_data = pd.read_csv("pos_logs.csv")
pos_transactions = pos_data.to_dict('records')
pos_times = set(pos_data["timestamp"].astype(str))

print("=" * 70)
print("🛡️  SecurePOS AI - Real-Time Continuous Demo")
print("=" * 70)
print(f"✓ Loaded {len(pos_transactions)} POS transactions")
print(f"  Times: {sorted(pos_times)}")
print()
print("Dashboard at: http://localhost:8501")
print("Press Ctrl+C to stop")
print("-" * 70)
print()

try:
    # Continuous loop - simulate video playback repeatedly
    loop_count = 0
    while True:
        loop_count += 1
        print(f"\n📹 Loop {loop_count} - Starting video playback...")
        
        # Simulate video frames (0-8 seconds for demo1.mp4)
        for i in range(9):  # 0 to 8 seconds
            seconds = i
            timestamp = str(timedelta(seconds=int(seconds)))
            
            # Check if this time has a POS transaction
            current_pos = [t for t in pos_transactions if str(t['timestamp']) == timestamp]
            
            # Simulate detections
            people_count = 1 if i % 10 < 8 else 0
            objects = ["cell phone"] if i % 15 < 3 else []
            
            # Check for theft
            theft = False
            if objects and timestamp not in pos_times:
                theft = True
                status_msg = "⚠️  THEFT DETECTED"
            elif current_pos:
                status_msg = f"✓ AUTHORIZED {current_pos[0]['event']}"
            else:
                status_msg = "Safe"
            
            # Update real-time data
            data = {
                "status": "running",
                "current_time": timestamp,
                "people_count": people_count,
                "objects_detected": objects,
                "theft_detected": theft,
                "current_pos_transaction": current_pos,
                "all_pos_transactions": pos_transactions,
                "timestamp": time.time()
            }
            
            with open("realtime_data.json", "w") as f:
                json.dump(data, f)
            
            # Print progress
            print(f"  Time: {timestamp:8s} | {status_msg:25s} | People: {people_count} | Objects: {len(objects)}", end='\r')
            
            time.sleep(0.1)  # Simulate video playback at ~10x speed for demo
        
        print("\n✓ Video playback completed, looping again...\n")
        time.sleep(1)  # Pause between loops

except KeyboardInterrupt:
    print("\n\n✓ Demo stopped")
    with open("realtime_data.json", "w") as f:
        json.dump({"status": "stopped"}, f)
    print("System stopped gracefully")

