# NEXUS — Intelligent DevOps System (Advanced UI Prototype)

A software-only final-year engineering project built with Streamlit, Python, SQLite and Plotly.

## Run on Windows
1. Install Python 3.10+ and select **Add Python to PATH**.
2. Extract the ZIP and open this folder in VS Code.
3. In VS Code: Terminal → New Terminal.
4. Run:
```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```
5. Open the local URL printed in the terminal, usually http://localhost:8501.

## Modules
- Command Center: operational KPIs, pipeline activity and latest releases.
- Project Hub: create and delete projects.
- Pipeline Studio: local pipeline workflow demonstration with stage records.
- AI Log Intelligence: severity classification, anomaly flags and investigation suggestions.
- Health Analytics: explainable risk score, saved telemetry and trend chart.
- Release Center: deployment/release record management.

## Docker
```bash
docker build -t nexus-devops .
docker run --rm -p 8501:8501 nexus-devops
```

## Important scope statement
This is an advanced local software prototype. Pipeline stages are simulated locally; the application does not yet clone Git repositories, invoke Jenkins, build/push real Docker images, deploy to Kubernetes or ingest live Prometheus metrics. The health score is a transparent heuristic, not a validated model trained on historical failures. The log analyzer uses pattern rules and optionally Isolation Forest as an unsupervised anomaly signal. Do not present future integrations as completed functionality.

## Next engineering phase
Implement GitHub App/webhooks, Jenkins API with secret storage, controlled Docker runner, Kubernetes service account, Prometheus ingestion, authentication/RBAC, tests and a labelled historical incident dataset for model training/evaluation.
