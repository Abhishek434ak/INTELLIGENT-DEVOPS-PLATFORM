import re, random, time
from statistics import mean

def analyze_logs(raw):
    lines=[x.strip() for x in raw.splitlines() if x.strip()]
    events=[]
    error_re=re.compile(r"\b(error|fatal|exception|critical|failed|timeout|traceback)\b",re.I)
    warn_re=re.compile(r"\b(warn|warning|retry|deprecated|slow)\b",re.I)
    for line in lines:
        level="ERROR" if error_re.search(line) else ("WARNING" if warn_re.search(line) else "INFO")
        anomaly="YES" if level=="ERROR" or len(line)>350 else "NO"
        events.append({"level":level,"anomaly":anomaly,"message":line})
    # Isolation Forest is optional; use numeric line features as an additional anomaly signal.
    model_note="Pattern-based analysis"
    try:
        from sklearn.ensemble import IsolationForest
        if len(lines)>=8:
            X=[[len(x),sum(ch.isdigit() for ch in x),x.count(":"),x.count(" ")] for x in lines]
            pred=IsolationForest(contamination="auto",random_state=42,n_estimators=100).fit_predict(X)
            for i,label in enumerate(pred):
                if label==-1 and events[i]["anomaly"]=="NO": events[i]["anomaly"]="POSSIBLE"
            model_note="Pattern rules + Isolation Forest unsupervised signal"
    except Exception: pass
    errors=sum(e["level"]=="ERROR" for e in events)
    flagged=sum(e["anomaly"]!="NO" for e in events)
    risk="CRITICAL" if errors>=4 or flagged>=7 else ("HIGH" if errors>=2 else ("MEDIUM" if errors or flagged else "LOW"))
    recs=[]
    joined="\n".join(lines).lower()
    if "timeout" in joined: recs.append("Inspect database/network latency, connection pool limits and timeout configuration.")
    if "memory" in joined or "out of memory" in joined: recs.append("Inspect memory consumption, heap limits and possible memory leaks.")
    if "connection" in joined: recs.append("Verify service availability, credentials and network connectivity for dependent services.")
    if errors: recs.append("Correlate error timestamps with recent commits and deployment events.")
    if not recs: recs.append("No strong error pattern detected. Continue monitoring and compare with a known-good baseline.")
    summary=f"{len(lines)} log lines analyzed. {errors} error-level entries and {flagged} flagged or possible anomalies. Analysis mode: {model_note}. Risk: {risk}."
    return {"total_lines":len(lines),"error_count":errors,"anomaly_count":flagged,"risk":risk,"summary":summary,"events":events,"recommendations":recs}

def assess_health(cpu,memory,errors,latency):
    cpu_part=cpu*.25
    mem_part=memory*.25
    error_part=min(errors*5,30)
    latency_part=min(latency/50,20)
    score=min(100,round(cpu_part+mem_part+error_part+latency_part))
    status="CRITICAL" if score>=75 else ("WARNING" if score>=45 else "HEALTHY")
    factors=[]
    if cpu>=80: factors.append("CPU utilization is high; inspect expensive processes and request load.")
    if memory>=80: factors.append("Memory utilization is high; inspect memory growth and container limits.")
    if errors>=5: factors.append("Recent error volume is elevated; inspect application and dependency logs.")
    if latency>=1000: factors.append("Response latency is high; inspect database queries and downstream services.")
    if not factors: factors.append("No major threshold breach detected from the supplied telemetry.")
    return {"score":score,"status":status,"factors":factors,"explanation":"Risk score is calculated from weighted CPU, memory, recent errors and latency inputs. It is a heuristic baseline, not a trained predictive model."}

def execute_demo_pipeline(project,commit_summary,profile):
    stages=[
      ("Source validation","Repository metadata checked locally"),
      ("Build","Demo build validation completed"),
      ("Unit tests","Demo test suite passed"),
      ("Security review","Dependency/security scan step represented in demo"),
      ("Package","Container packaging step represented in demo"),
      ("Release","Deployment step represented in demo; no remote environment modified")
    ]
    if profile=="Extended validation": stages.insert(4,("Integration tests","Integration-test stage represented in demo"))
    result=[]
    for i,(name,msg) in enumerate(stages):
        result.append({"name":name,"status":"SUCCESS","message":msg,"duration_ms":random.randint(40,260)})
    return {"status":"SUCCESS","duration_seconds":round(sum(x["duration_ms"] for x in result)/1000,2),
            "commit_summary":commit_summary,"profile":profile,"stages":result}
def generate_recommendations(health, logs=None, pipeline=None):
    recommendations = []

    if isinstance(health, dict):
        score = health.get("score", health.get("health_score", 100))

        if score < 50:
            recommendations.append(
                "Critical system health: investigate failing services immediately."
            )
        elif score < 80:
            recommendations.append(
                "System health needs attention: inspect resource usage and errors."
            )
        else:
            recommendations.append(
                "System health is good: continue monitoring."
            )

    if logs:
        recommendations.append(
            "Review recent error and warning logs to identify recurring problems."
        )

    if pipeline:
        recommendations.append(
            "Review failed pipeline stages before approving the next deployment."
        )

    if not recommendations:
        recommendations.append(
            "Collect more system telemetry to generate useful recommendations."
        )

    return recommendations
