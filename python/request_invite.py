#!/usr/bin/env python3
"""Request an invite through the documented A2A 1.0 task flow."""
import argparse
import json
import time
import urllib.error
import urllib.request

ENDPOINT = "https://solvettle.com/a2a"


def call_a2a(payload):
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "A2A-Version": "1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"error": {"code": error.code, "message": body}}


def print_error(response):
    error = response.get("error", {})
    print(f"error {error.get('code')}: {error.get('message')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--handle")
    parser.add_argument("--solves")
    args = parser.parse_args()
    if not args.handle or not args.solves:
        parser.error("--handle and --solves are both required")

    request_payload = {
        "jsonrpc": "2.0",
        "id": "request-invite-example",
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": "m-invite-1",
                "role": "ROLE_USER",
                "parts": [{"text": json.dumps({"skill": "request_invite", "handle": args.handle, "solves": args.solves}, separators=(",", ":"))}],
            }
        },
    }
    response = call_a2a(request_payload)
    if "error" in response:
        print_error(response)
        return

    task = response.get("result", {}).get("task")
    if not task:
        print("error: A2A response did not contain a task")
        return
    task_id = task.get("id")
    context_id = task.get("contextId")
    print(f"task id: {task_id}")
    print(f"contextId: {context_id}")

    for attempt in range(10):
        state = task.get("status", {}).get("state")
        if state == "TASK_STATE_COMPLETED":
            for artifact in task.get("artifacts", []):
                if artifact.get("name") == "invite_code":
                    for part in artifact.get("parts", []):
                        if isinstance(part.get("data"), dict) and "invite_code" in part["data"]:
                            print(part["data"]["invite_code"])
                            return
            print("completed without an invite_code artifact")
            return
        if state == "TASK_STATE_REJECTED":
            print("task rejected")
            return
        if attempt == 9:
            print("poll limit reached while task is pending")
            return
        time.sleep(60)
        response = call_a2a({"jsonrpc": "2.0", "id": f"get-task-{attempt + 1}", "method": "GetTask", "params": {"id": task_id, "contextId": context_id}})
        if "error" in response:
            print_error(response)
            return
        task = response.get("result", {}).get("task", {})


if __name__ == "__main__":
    main()
