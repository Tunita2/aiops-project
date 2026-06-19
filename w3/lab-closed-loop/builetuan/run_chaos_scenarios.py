import os
import time
import sys
import subprocess
import requests
import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
AUDIT_LOG = BASE_DIR / "audit_log.jsonl"
CONFIG_YAML = BASE_DIR / "config.yaml"
BASELINE_JSON = BASE_DIR.parent / "data-pack" / "data" / "baseline.json"

def clean_log():
    if AUDIT_LOG.exists():
        AUDIT_LOG.unlink()
    print("Deleted old audit_log.jsonl")

def start_container(name):
    print(f"Starting {name}...")
    subprocess.run(["docker", "start", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)

def stop_container(name):
    print(f"Stopping {name}...")
    subprocess.run(["docker", "stop", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def update_baseline(up_required, timeout):
    with open(BASELINE_JSON, "r") as f:
        data = json.load(f)
    data["verify_thresholds"]["up_required"] = up_required
    data["verify_thresholds"]["verify_timeout_seconds"] = timeout
    with open(BASELINE_JSON, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Updated baseline.json (up_required={up_required}, timeout={timeout})")

def read_last_events(n=10):
    if not AUDIT_LOG.exists():
        return []
    with open(AUDIT_LOG, "r") as f:
        lines = f.readlines()
    events = []
    for line in lines[-n:]:
        try:
            events.append(json.loads(line.strip()))
        except:
            pass
    return events

def wait_for_event(event_type, service=None, timeout=180):
    start = time.time()
    from datetime import datetime, timezone
    start_ts = datetime.now(timezone.utc).isoformat()
    while time.time() - start < timeout:
        events = read_last_events(20)
        for ev in events:
            if ev.get("ts", "") >= start_ts:
                if ev.get("event_type") == event_type:
                    if service is None or ev.get("service") == service:
                        return ev
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for event {event_type} on {service}")

def generate_traffic(stop_event, url, interval=0.2):
    import threading
    def target():
        while not stop_event.is_set():
            try:
                requests.get(url, timeout=1)
            except:
                pass
            time.sleep(interval)
    t = threading.Thread(target=target, daemon=True)
    t.start()
    return t

def main():
    # Make sure containers are running and healthy
    start_container("ronki-payment-svc")
    start_container("ronki-checkout-svc")
    
    clean_log()
    
    # Make sure baseline.json is healthy for Scenario 1
    update_baseline(up_required=1, timeout=120)
    
    print("\n=== STARTING ORCHESTRATOR ===")
    orchestrator = subprocess.Popen(
        [sys.executable, "closed_loop.py", "--config", "config.yaml"],
        cwd=str(BASE_DIR)
    )
    time.sleep(5)
    
    try:
        # ---------------------------------------------------------
        # SCENARIO 1: Latency on payment-svc
        # ---------------------------------------------------------
        print("\n--- Running Scenario 1: HighLatency on payment-svc ---")
        # Inject latency via API
        resp = requests.get("http://localhost:8082/inject-fault?latency=500")
        print("Latency injected API response:", resp.json())
        
        # Start traffic generator
        import threading
        stop_traffic = threading.Event()
        traffic_thread = generate_traffic(stop_traffic, "http://localhost:8082/")
        print("Traffic generator started.")
        
        print("Waiting for alert detection and successful mitigation...")
        wait_for_event("ACTION_SUCCESS", service="payment-svc")
        print("Scenario 1 passed!")
        
        stop_traffic.set()
        traffic_thread.join()
        
        # Give it a moment to settle
        time.sleep(5)
        
        # ---------------------------------------------------------
        # SCENARIO 2 & 3: Circuit Breaker on checkout-svc
        # ---------------------------------------------------------
        print("\n--- Running Scenario 2 & 3: Circuit Breaker ---")
        # Restart orchestrator to use updated baseline
        print("Stopping orchestrator to apply baseline update...")
        orchestrator.terminate()
        orchestrator.wait()
        
        # Force verify failure
        update_baseline(up_required=2, timeout=30)
        
        print("Starting orchestrator again...")
        orchestrator = subprocess.Popen(
            [sys.executable, "closed_loop.py", "--config", "config.yaml"],
            cwd=str(BASE_DIR)
        )
        time.sleep(5)
        
        # We need 3 consecutive failures
        for i in range(1, 4):
            print(f"\n--- Failure Cycle #{i} ---")
            stop_container("ronki-checkout-svc")
            
            if i < 3:
                print("Waiting for ROLLBACK_EXECUTED...")
                wait_for_event("ROLLBACK_EXECUTED", service="checkout-svc", timeout=180)
                print(f"Failure Cycle #{i} completed.")
                # Wait for container to be fully up and scraper to fetch it
                time.sleep(15)
            else:
                print("Waiting for CIRCUIT_BREAKER_HALT...")
                wait_for_event("CIRCUIT_BREAKER_HALT", timeout=180)
                print("Scenario 3 passed! Circuit breaker tripped.")

    finally:
        print("\nStopping orchestrator...")
        orchestrator.terminate()
        orchestrator.wait()
        
        # Restore baseline.json to healthy state
        update_baseline(up_required=1, timeout=120)
        print("Restored baseline.json to healthy baseline configuration.")
        
        # Start checkout-svc back up to leave stack healthy
        start_container("ronki-checkout-svc")
        print("Checkout service started back up.")

if __name__ == "__main__":
    main()
