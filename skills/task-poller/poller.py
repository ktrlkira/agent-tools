#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error
import os


def _load_env():
    for path in [os.path.expanduser("~/.hermes/.env")]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        os.environ.setdefault(k.strip(), v.strip())


_load_env()

API_BASE = os.environ.get("AGENT_API_BASE", "http://localhost:8000")
API_SECRET = os.environ.get("AGENT_API_SECRET", "")
HEADERS = {"Authorization": f"Bearer {API_SECRET}"} if API_SECRET else {}
COST_PER_INPUT_TOKEN = int(os.environ.get("COST_PER_INPUT_TOKEN", "0"))
COST_PER_OUTPUT_TOKEN = int(os.environ.get("COST_PER_OUTPUT_TOKEN", "0"))


def do_request(method, url, data=None, timeout=10):
    req = urllib.request.Request(str(url))
    req.get_method = lambda: method
    if data:
        req.data = json.dumps(data).encode()
    req.add_header("Content-Type", "application/json")
    if HEADERS:
        req.add_header("Authorization", HEADERS["Authorization"])
    return urllib.request.urlopen(req, timeout=timeout).read().decode()


def fetch_pending_task():
    try:
        result = do_request("GET", f"{API_BASE}/tasks?status=pending", timeout=10)
        data = json.loads(result)
        return data[0] if isinstance(data, list) and data else None
    except Exception as e:
        print(f"[poller] fetch failed: {e}", file=sys.stderr)
        return None


def claim_task(task_id):
    try:
        result = do_request("PATCH", f"{API_BASE}/tasks/{task_id}",
                            {"status": "in_progress"}, timeout=10)
        data = json.loads(result) if result else {}
        return data.get("status") == "in_progress"
    except Exception as e:
        print(f"[poller] claim failed: {e}", file=sys.stderr)
        return False


def report_result(task_id, status, result="", error=""):
    payload = {"status": status}
    if result:
        payload["result"] = result
    if error:
        payload["error"] = error
    try:
        do_request("PATCH", f"{API_BASE}/tasks/{task_id}", payload, timeout=10)
    except Exception as e:
        print(f"[poller] report failed: {e}", file=sys.stderr)


def report_tokens(task_id, tokens_in, tokens_out, model=None):
    cost_usd = tokens_in * COST_PER_INPUT_TOKEN + tokens_out * COST_PER_OUTPUT_TOKEN
    body = {"tokens_in": tokens_in, "tokens_out": tokens_out, "cost_usd": cost_usd}
    if model:
        body["model"] = model
    try:
        do_request("PATCH", f"{API_BASE}/tasks/{task_id}", body, timeout=10)
    except Exception as e:
        print(f"[poller] token report failed: {e}", file=sys.stderr)


def send_heartbeat(task_id=None):
    try:
        do_request("POST", f"{API_BASE}/heartbeat", {
            "device": os.environ.get("DEVICE_NAME", "unknown"),
            "status": "healthy",
            "current_task_id": task_id,
            "model_usage": {},
        }, timeout=5)
    except Exception as e:
        print(f"[poller] heartbeat failed: {e}", file=sys.stderr)


def send_heartbeat_to_cerulean(task_id=None):
    cerulean_url = os.environ.get("CERULEAN_URL", "")
    if not cerulean_url:
        return
    try:
        result = do_request("GET", f"{API_BASE}/tasks", timeout=5)
        tasks = json.loads(result) if result else []
        pending = sum(1 for t in tasks if t.get("status") == "pending")
        in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
        do_request("POST", f"{cerulean_url}/heartbeat", {
            "device": os.environ.get("DEVICE_NAME", "unknown"),
            "status": "healthy",
            "current_task_id": task_id,
            "pending_count": pending,
            "in_progress_count": in_progress,
            "model_usage": {},
        }, timeout=5)
    except Exception:
        pass


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "fetch"

    if command == "fetch":
        task = fetch_pending_task()
        print(json.dumps(task if task else {"no_tasks": True}))

    elif command == "claim":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "missing task_id"}))
            sys.exit(1)
        print(json.dumps({"claimed": claim_task(sys.argv[2])}))

    elif command == "report":
        if len(sys.argv) < 5:
            print(json.dumps({"error": "missing args"}))
            sys.exit(1)
        report_result(sys.argv[2], sys.argv[3], sys.argv[4],
                      sys.argv[5] if len(sys.argv) > 5 else "")
        print(json.dumps({"reported": True}))

    elif command == "tokens":
        if len(sys.argv) < 5:
            print(json.dumps({"error": "missing args"}))
            sys.exit(1)
        task_id = sys.argv[2]
        tokens_in, tokens_out = int(sys.argv[3]), int(sys.argv[4])
        model = sys.argv[5] if len(sys.argv) > 5 else None
        report_tokens(task_id, tokens_in, tokens_out, model)
        print(json.dumps({"tokens_reported": True, "model": model}))

    elif command == "heartbeat":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        # Bump updated_at on the task row so the watchdog clock resets
        if task_id:
            try:
                req = urllib.request.Request(f"{API_BASE}/tasks/{task_id}")
                req.get_method = lambda: "PATCH"
                req.data = b"{}"
                req.add_header("Content-Type", "application/json")
                if HEADERS:
                    req.add_header("Authorization", HEADERS["Authorization"])
                urllib.request.urlopen(req, timeout=5)
            except Exception as e:
                print(f"[poller] task heartbeat failed: {e}", file=sys.stderr)
        send_heartbeat(task_id)
        send_heartbeat_to_cerulean(task_id)
        print(json.dumps({"heartbeat": True}))


if __name__ == "__main__":
    main()
