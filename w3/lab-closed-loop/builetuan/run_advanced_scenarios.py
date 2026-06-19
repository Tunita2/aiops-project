import os
import time
import sys
import subprocess
import requests
import json
from pathlib import Path
from datetime import datetime, timezone

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
    time.sleep(2)

def read_last_events(n=30):
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

def wait_for_event(event_type, service=None, timeout=120, start_ts=None):
    start = time.time()
    if start_ts is None:
        start_ts = datetime.now(timezone.utc).isoformat()
    while time.time() - start < timeout:
        events = read_last_events(30)
        for ev in events:
            if ev.get("ts", "") >= start_ts:
                if ev.get("event_type") == event_type:
                    if service is None or ev.get("service") == service:
                        return ev
        time.sleep(1)
    raise TimeoutError(f"Timed out waiting for event {event_type} on {service}")

def post_alert(alertname, service, severity="critical"):
    payload = [
        {
            "labels": {
                "alertname": alertname,
                "service": service,
                "severity": severity
            },
            "annotations": {
                "summary": f"{alertname} triggered for testing on {service}"
            },
            "generatorURL": "http://localhost:9090"
        }
    ]
    resp = requests.post("http://localhost:9093/api/v2/alerts", json=payload, timeout=5)
    print(f"Posted alert {alertname} for {service}. Alertmanager response: {resp.status_code}")

def resolve_alert(alertname, service, severity="critical"):
    now_str = datetime.now(timezone.utc).isoformat()
    payload = [
        {
            "labels": {
                "alertname": alertname,
                "service": service,
                "severity": severity
            },
            "startsAt": now_str,
            "endsAt": now_str,
            "generatorURL": "http://localhost:9090"
        }
    ]
    try:
        resp = requests.post("http://localhost:9093/api/v2/alerts", json=payload, timeout=5)
        print(f"Resolved alert {alertname} for {service}. Alertmanager response: {resp.status_code}")
    except Exception as e:
        print(f"Failed to resolve alert: {e}")

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

def run_scenario_4():
    print("\n=========================================================")
    print("RUNNING SCENARIO 4: Multi-Step Transactional Rollback")
    print("=========================================================")
    
    # Ensure containers are running
    start_container("ronki-api-gateway")
    
    clean_log()
    
    # Create the fail_step_c file in current workspace to trigger step-c failure
    fail_file = BASE_DIR / "fail_step_c"
    fail_file.touch()
    print("Created fail_step_c marker file.")

    # Start orchestrator
    print("Starting orchestrator...")
    orchestrator = subprocess.Popen(
        [sys.executable, "closed_loop.py", "--config", "config.yaml"],
        cwd=str(BASE_DIR)
    )
    time.sleep(5)

    scenario_start = datetime.now(timezone.utc).isoformat()
    try:
        # Inject MultiStepDeploy alert for api-gateway
        post_alert("MultiStepDeploy", "api-gateway")
        
        print("Waiting for transactional rollback completion...")
        wait_for_event("TRANSACTIONAL_ROLLBACK_COMPLETE", service="api-gateway", timeout=120, start_ts=scenario_start)
        print("Scenario 4 completed successfully!")
        
        # Resolve the alert immediately
        resolve_alert("MultiStepDeploy", "api-gateway")
    finally:
        print("Stopping orchestrator...")
        orchestrator.terminate()
        orchestrator.wait()
        
        if fail_file.exists():
            fail_file.unlink()
            print("Removed fail_step_c marker file.")
        
        # Settle down
        time.sleep(3)

def run_scenario_5():
    print("\n=========================================================")
    print("RUNNING SCENARIO 5: Concurrent Alert Race")
    print("=========================================================")
    
    # Ensure services are up
    start_container("ronki-payment-svc")
    start_container("ronki-inventory-svc")
    
    clean_log()

    # Start orchestrator
    print("Starting orchestrator...")
    orchestrator = subprocess.Popen(
        [sys.executable, "closed_loop.py", "--config", "config.yaml"],
        cwd=str(BASE_DIR)
    )
    time.sleep(5)

    scenario_start = datetime.now(timezone.utc).isoformat()
    try:
        # Start traffic generators for both services
        import threading
        stop_traffic = threading.Event()
        t1 = generate_traffic(stop_traffic, "http://localhost:8082/")
        t2 = generate_traffic(stop_traffic, "http://localhost:8083/")
        print("Traffic generators started for payment-svc and inventory-svc.")

        # Post concurrent alerts simultaneously
        print("Posting concurrent alerts for payment-svc and inventory-svc...")
        post_alert("HighLatency", "payment-svc", severity="warning")
        post_alert("HighLatency", "inventory-svc", severity="warning")

        # Wait a few seconds to let them start processing, then post a duplicate alert on payment-svc
        # to trigger SERVICE_LOCK_BUSY
        time.sleep(5)
        print("Posting duplicate alert on payment-svc to trigger SERVICE_LOCK_BUSY...")
        post_alert("HighLatency", "payment-svc", severity="critical")

        print("Waiting for lock busy and action success events...")
        wait_for_event("SERVICE_LOCK_BUSY", service="payment-svc", timeout=60, start_ts=scenario_start)
        print("SERVICE_LOCK_BUSY detected!")
        wait_for_event("ACTION_SUCCESS", service="payment-svc", timeout=120, start_ts=scenario_start)
        print("ACTION_SUCCESS on payment-svc detected!")
        wait_for_event("ACTION_SUCCESS", service="inventory-svc", timeout=120, start_ts=scenario_start)
        print("ACTION_SUCCESS on inventory-svc detected!")
        print("Concurrent actions completed successfully!")
        
        stop_traffic.set()
        t1.join()
        t2.join()
        
        # Resolve the alerts
        resolve_alert("HighLatency", "payment-svc", severity="warning")
        resolve_alert("HighLatency", "payment-svc", severity="critical")
        resolve_alert("HighLatency", "inventory-svc", severity="warning")
    finally:
        print("Stopping orchestrator...")
        orchestrator.terminate()
        orchestrator.wait()
        time.sleep(3)

def run_scenario_6():
    print("\n=========================================================")
    print("RUNNING SCENARIO 6: LLM Hallucination Defense")
    print("=========================================================")
    clean_log()

    # Start orchestrator
    print("Starting orchestrator...")
    orchestrator = subprocess.Popen(
        [sys.executable, "closed_loop.py", "--config", "config.yaml"],
        cwd=str(BASE_DIR)
    )
    time.sleep(5)

    scenario_start = datetime.now(timezone.utc).isoformat()
    try:
        # Inject TestHallucination alert
        post_alert("TestHallucination", "payment-svc")
        
        print("Waiting for DECISION_VALIDATION_FAILED...")
        wait_for_event("DECISION_VALIDATION_FAILED", timeout=60, start_ts=scenario_start)
        print("Scenario 6 completed successfully!")
        
        # Resolve it
        resolve_alert("TestHallucination", "payment-svc")
    finally:
        print("Stopping orchestrator...")
        orchestrator.terminate()
        orchestrator.wait()
        time.sleep(3)

def main():
    run_scenario_4()
    run_scenario_5()
    run_scenario_6()
    print("\nAll advanced scenarios completed successfully!")

if __name__ == "__main__":
    main()
