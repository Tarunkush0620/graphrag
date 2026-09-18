import json
import urllib.request

questions = [
    "Who won the gold medal in Men's Singles Tennis at Athens 2004?",
    "Which athlete won the men's 50 km race walk at the Summer Olympics immediately before 2016?",
    "Which venue hosted both an event won by an athlete from China and an event won by an athlete from France?",
    "Which gold medalist had more competitors in their event than Chen Ding?"
]

for q in questions:
    print("\n" + "=" * 60, flush=True)
    print("QUESTION:", q, flush=True)
    for mode in ["rag", "graphrag", "agentic"]:
        data = json.dumps({"question": q, "mode": mode, "max_steps": 6}).encode("utf-8")
        req = urllib.request.Request("http://localhost:8000/api/query", data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                res = json.loads(r.read().decode("utf-8"))
                ans = res.get("answer", "")
                tok = res.get("tokens")
                lat = res.get("latency_ms")
                steps = res.get("retrieval_steps")
                hops = res.get("graph_hops", 0)
                print(f"[{mode.upper()}]", flush=True)
                print(f"  Answer: {ans}", flush=True)
                print(f"  Tokens: {tok} | Latency: {lat}ms | Steps: {steps} | Hops: {hops}", flush=True)
                if mode == "agentic":
                    print(f"  Stopping Reason: {res.get('stopping_reason')}", flush=True)
                    print(f"  Facts Required: {res.get('facts_required')}", flush=True)
                    print(f"  Facts Found: {res.get('facts_found')}", flush=True)
                    print(f"  Graph Paths Discovered: {len(res.get('graph_paths', []))}", flush=True)
                    print(f"  Decision Log Steps: {len(res.get('decision_log', []))}", flush=True)
                    print(f"  Tool Log Entries: {len(res.get('tool_log', []))}", flush=True)
        except Exception as e:
            print(f"[{mode.upper()}] Error: {e}", flush=True)
