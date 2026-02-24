#!/usr/bin/env python3
"""Quick test for POST /research. Run with the server up: uv run python scripts/test_research.py"""

import json
import urllib.request
import urllib.error

BASE = "http://localhost:8000"


def main():
    # 1. Health check
    try:
        with urllib.request.urlopen(f"{BASE}/") as r:
            print("GET /:", json.loads(r.read().decode()))
    except urllib.error.URLError as e:
        print("Server not running? Start with: uv run python main.py")
        raise SystemExit(1) from e

    # 2. POST /research (minimal payload)
    body = json.dumps({
        "company": "Acme Corp",
        "company_url": None,
        "industry": "SaaS",
        "hq_location": None,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/research",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print("\nPOST /research (this may take a minute)...")
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            out = json.loads(r.read().decode())
            print("Status:", out.get("status"))
            print("Job ID:", out.get("job_id"))
            persona = out.get("persona_content")
            if persona:
                print("Persona keys:", list(persona.keys())
                      if isinstance(persona, dict) else type(persona))
                print("Persona (sample):", json.dumps(
                    persona, indent=2)[:800], "...")
            else:
                print("Persona content:", persona)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print("HTTP error:", e.code, body)
        raise SystemExit(1) from e
    except urllib.error.URLError as e:
        print("Request failed:", e)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
