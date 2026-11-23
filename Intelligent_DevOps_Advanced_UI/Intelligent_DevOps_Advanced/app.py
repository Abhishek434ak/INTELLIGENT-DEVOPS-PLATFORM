import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from database import (
    init_db, create_project, list_projects, create_pipeline_run, list_pipeline_runs,
    add_log_events, list_log_events, save_metrics, list_metrics, create_deployment,
    list_deployments, dashboard_summary, delete_project
)
from engine import analyze_logs, assess_health, execute_demo_pipeline, generate_recommendations

st.set_page_config(page_title="NEXUS | Intelligent DevOps", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
init_db()

# ---------- Visual system ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#080d18; --panel:#101a2b; --panel2:#132139; --line:#22334d; --muted:#8fa4c2; --text:#edf4ff; --cyan:#55d6e8; --blue:#648cff; --green:#3ddc97; }
html, body, [class*="css"] { font-family:'Manrope',sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #142743 0%, #080d18 48%); color:var(--text); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0e192a,#09111e); border-right:1px solid #20314a; }
[data-testid="stSidebar"] * { color:#dce8fa; }
.block-container { padding-top:1.5rem; max-width:1500px; }
h1,h2,h3 { letter-spacing:-.04em; color:#f4f8ff; }
p, label, span { color:inherit; }
.hero { background:linear-gradient(115deg,rgba(30,60,100,.85),rgba(15,29,49,.92)); border:1px solid #2a4569; border-radius:22px; padding:26px 30px; margin-bottom:22px; box-shadow:0 18px 55px rgba(0,0,0,.18); }
.hero-kicker { color:#70d9e8; font-size:11px; letter-spacing:.18em; font-weight:800; text-transform:uppercase; }
.hero-title { font-size:32px; font-weight:800; line-height:1.15; margin:7px 0; color:#f4f8ff; }
.hero-sub { color:#a9bdd7; font-size:13px; }
.panel { background:linear-gradient(145deg,#111e31,#0e1929); border:1px solid #243650; border-radius:17px; padding:18px 20px; }
.metric-label { color:#93a9c6; font-size:11px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
.metric-value { color:#f4f8ff; font-size:29px; font-weight:800; margin-top:4px; }
.metric-foot { color:#7f96b6; font-size:11px; margin-top:3px; }
.section-label { color:#6ed8e8; font-size:11px; font-weight:800; letter-spacing:.16em; text-transform:uppercase; margin:12px 0 8px; }
.status-pill { display:inline-block; border-radius:999px; padding:5px 10px; font-size:10px; font-weight:800; letter-spacing:.08em; background:#163c36; color:#70efb7; border:1px solid #286653; }
.small-muted { color:#91a5c1; font-size:12px; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#14243a,#101b2d); border:1px solid #253b59; padding:15px 17px; border-radius:16px; }
div[data-testid="stMetric"] label { color:#94abc9; font-size:11px; text-transform:uppercase; letter-spacing:.08em; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#f4f8ff; font-weight:800; }
.stButton>button { border-radius:10px; border:1px solid #36547a; background:linear-gradient(100deg,#2563eb,#0e9fba); color:white; font-weight:800; padding:.55rem 1rem; }
.stButton>button:hover { border-color:#6be3ee; color:white; box-shadow:0 0 20px rgba(85,214,232,.18); }
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox div[data-baseweb="select"] { background:#0c1727!important; color:#edf4ff!important; border-color:#2a405e!important; border-radius:10px!important; }
[data-testid="stDataFrame"] { border:1px solid #243650; border-radius:12px; overflow:hidden; }
hr { border-color:#233650; }
</style>
""", unsafe_allow_html=True)

def hero(kicker, title, subtitle):
    st.markdown(f'<div class="hero"><div class="hero-kicker">{kicker}</div><div class="hero-title">{title}</div><div class="hero-sub">{subtitle}</div></div>', unsafe_allow_html=True)

def metric_card(label, value, foot=""):
    st.markdown(f'<div class="panel"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>', unsafe_allow_html=True)

def project_selector(key="project_select"):
    projects = list_projects()
    if not projects:
        st.info("No projects registered yet. Create a project in Project Hub to get started.")
        return None
    return st.selectbox("Select project", projects, format_func=lambda p: f"{p['name']} · {p['branch']}", key=key)

with st.sidebar:
    st.markdown("## ⚡ NEXUS")
    st.caption("INTELLIGENT DEVOPS PLATFORM")
    st.markdown("---")
    page = st.radio("WORKSPACE", ["Command Center", "Project Hub", "Pipeline Studio", "AI Log Intelligence", "Health Analytics", "Release Center"], label_visibility="visible")
    st.markdown("---")
    st.markdown("**SYSTEM STATUS**")
    st.markdown('<span class="status-pill">● LOCAL SYSTEM ONLINE</span>', unsafe_allow_html=True)
    st.caption("Build 2.0 · Software-only")
    st.markdown("---")
    st.caption("NEXUS DevOps · Advanced prototype")

if page == "Command Center":
    summary = dashboard_summary()
    hero("OPERATIONS OVERVIEW", "Command Center", "A unified view of software delivery, runtime signals and release activity.")
    cols=st.columns(4)
    values=[("PROJECTS",summary["projects"],"Registered applications"),("PIPELINE RUNS",summary["runs"],"Recorded executions"),("LOG EVENTS",summary["logs"],"Analyzed log records"),("DEPLOYMENTS",summary["deployments"],"Release records")]
    for c,(label,val,foot) in zip(cols,values):
        with c: metric_card(label,val,foot)
    st.markdown('<div class="section-label">DELIVERY INTELLIGENCE</div>',unsafe_allow_html=True)
    left,right=st.columns([1.45,1])
    runs=list_pipeline_runs(limit=30)
    with left:
        st.markdown("### Pipeline activity")
        if runs:
            df=pd.DataFrame(runs)
            df["created_at"]=pd.to_datetime(df["created_at"])
            fig=px.histogram(df,x="created_at",color="status",nbins=12,barmode="stack",template="plotly_dark",color_discrete_map={"SUCCESS":"#3ddc97","FAILED":"#ff6b7a"})
            fig.update_layout(height=300,margin=dict(l=10,r=10,t=15,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend_title_text="")
            st.plotly_chart(fig,use_container_width=True)
        else: st.markdown('<div class="panel small-muted">No pipeline activity yet. Open Pipeline Studio to run your first workflow.</div>',unsafe_allow_html=True)
    with right:
        st.markdown("### Latest releases")
        deps=list_deployments(limit=6)
        if deps:
            for d in deps:
                st.markdown(f'<div class="panel" style="padding:12px 14px;margin-bottom:9px"><b>{d["project_name"]}</b><br><span class="small-muted">{d["environment"]} · {d["version"]}</span><br><span class="status-pill">{d["status"]}</span></div>',unsafe_allow_html=True)
        else: st.markdown('<div class="panel small-muted">No releases recorded.</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-label">RECENT EXECUTIONS</div>',unsafe_allow_html=True)
    if runs: st.dataframe(pd.DataFrame(runs)[["project_name","status","duration_seconds","created_at"]].head(8),use_container_width=True,hide_index=True)
    else: st.caption("Pipeline run history will appear here.")

elif page == "Project Hub":
    hero("WORKSPACE MANAGEMENT","Project Hub","Register and manage the applications monitored by NEXUS.")
    with st.expander("＋ Register a new project",expanded=not bool(list_projects())):
        with st.form("create_project",clear_on_submit=True):
            c1,c2=st.columns(2)
            name=c1.text_input("Project name",placeholder="Customer Portal")
            branch=c2.text_input("Default branch",value="main")
            repo=st.text_input("Git repository URL",placeholder="https://github.com/organization/repository")
            description=st.text_area("Description",placeholder="Short project purpose and technology details")
            if st.form_submit_button("Create project",use_container_width=True):
                if name.strip():
                    create_project(name.strip(),repo.strip(),branch.strip(),description.strip())
                    st.success("Project registered successfully.")
                    st.rerun()
                else: st.error("Project name is required.")
    projects=list_projects()
    st.markdown(f"### Registered applications · {len(projects)}")
    if projects:
        for p in projects:
            with st.container(border=True):
                c1,c2,c3=st.columns([3,2,1])
                c1.markdown(f"**{p['name']}**")
                c1.caption(p["description"] or "No description provided")
                c2.markdown(f"`{p['branch']}`")
                c2.caption(p["repo_url"] or "Repository not connected")
                if c3.button("Delete",key=f"del_{p['id']}"):
                    delete_project(p["id"]); st.rerun()
    else: st.info("Register your first project above.")

elif page == "Pipeline Studio":
    hero("CONTINUOUS DELIVERY","Pipeline Studio","Execute a controlled local pipeline workflow and inspect every stage result.")
    p=project_selector()
    if p:
        c1,c2=st.columns([2,1])
        with c1: commit=st.text_input("Change / commit summary",value="feat: update application service")
        with c2: profile=st.selectbox("Execution profile",["Standard validation","Extended validation"])
        if st.button("▶  Execute pipeline",type="primary",use_container_width=True):
            with st.spinner("Executing pipeline stages..."):
                result=execute_demo_pipeline(p,commit,profile)
                create_pipeline_run(p["id"],result)
            if result["status"]=="SUCCESS": st.success("Pipeline completed successfully.")
            else: st.error("Pipeline completed with failures.")
            for stage in result["stages"]:
                st.markdown(f'<div class="panel" style="margin:7px 0;padding:12px 16px"><b>{stage["name"]}</b> &nbsp; <span class="status-pill">{stage["status"]}</span><br><span class="small-muted">{stage["message"]} · {stage["duration_ms"]} ms</span></div>',unsafe_allow_html=True)
        st.markdown("### Execution history")
        history=list_pipeline_runs(project_id=p["id"],limit=20)
        if history: st.dataframe(pd.DataFrame(history),use_container_width=True,hide_index=True)
        else: st.caption("No runs for this project.")
    st.warning("Scope note: this build executes a local workflow demonstration. It does not call a live Jenkins server, build/push an image or deploy to Kubernetes.")

elif page == "AI Log Intelligence":
    hero("AI OPERATIONS","AI Log Intelligence","Detect severity patterns, surface unusual events and produce an investigation summary.")
    p=project_selector("log_project")
    sample="""2026-11-23 09:00:01 INFO API service started
2026-11-23 09:01:12 INFO Health check passed
2026-11-23 09:02:14 WARNING Retry connecting to cache
2026-11-23 09:02:20 ERROR Database connection timeout
2026-11-23 09:02:22 ERROR Request failed with exception
2026-11-23 09:03:00 INFO Worker restarted successfully"""
    raw=st.text_area("Paste application logs",value=sample,height=210)
    uploaded=st.file_uploader("Or upload a .log / .txt file",type=["log","txt"])
    if st.button("Analyze log stream",type="primary"):
        content=uploaded.getvalue().decode("utf-8",errors="replace") if uploaded else raw
        result=analyze_logs(content)
        if p: add_log_events(p["id"],result["events"])
        a,b,c=st.columns(3)
        a.metric("Risk classification",result["risk"])
        b.metric("Lines analyzed",result["total_lines"])
        c.metric("Flagged anomalies",result["anomaly_count"])
        st.markdown("### AI investigation summary")
        st.markdown(f'<div class="panel">{result["summary"]}</div>',unsafe_allow_html=True)
        if result["recommendations"]:
            st.markdown("### Suggested investigation actions")
            for rec in result["recommendations"]: st.markdown(f"- {rec}")
        st.markdown("### Event analysis")
        st.dataframe(pd.DataFrame(result["events"]),use_container_width=True,hide_index=True)
    st.markdown("### Stored log events")
    logs=list_log_events(project_id=p["id"] if p else None,limit=100)
    if logs: st.dataframe(pd.DataFrame(logs),use_container_width=True,hide_index=True)

elif page == "Health Analytics":
    hero("PREDICTIVE OPERATIONS","Health Analytics","Assess operational risk from service telemetry and inspect contributing signals.")
    p=project_selector("health_project")
    c1,c2=st.columns(2)
    with c1:
        cpu=st.slider("CPU utilization",0,100,42,format="%d%%")
        memory=st.slider("Memory utilization",0,100,55,format="%d%%")
    with c2:
        errors=st.number_input("Errors in the last 5 minutes",0,10000,1)
        latency=st.slider("Average response latency",0,5000,180,step=10,format="%d ms")
    if st.button("Run health assessment",type="primary",use_container_width=True):
        result=assess_health(cpu,memory,errors,latency)
        a,b=st.columns([1,2])
        a.metric("Risk score",f"{result['score']}/100",result["status"])
        with b:
            st.markdown("### Assessment")
            st.markdown(result["explanation"])
            st.progress(result["score"]/100)
        st.markdown("### Contributing factors")
        for factor in result["factors"]:
            st.markdown(f"- {factor}")
        if p:
            save_metrics(p["id"],cpu,memory,errors,latency,result["score"],result["status"])
            st.success("Telemetry snapshot saved to project history.")
    metrics=list_metrics(project_id=p["id"] if p else None,limit=100)
    if metrics:
        st.markdown("### Telemetry history")
        df=pd.DataFrame(metrics)
        st.dataframe(df,use_container_width=True,hide_index=True)
        if len(df)>1:
            fig=px.line(df.sort_values("created_at"),x="created_at",y=["cpu","memory","risk_score"],markers=True,template="plotly_dark",title="Resource and risk trends")
            fig.update_layout(height=330,margin=dict(l=10,r=10,t=45,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig,use_container_width=True)
    st.caption("The current risk engine is an explainable heuristic baseline, not a validated model trained on historical incidents.")

elif page == "Release Center":
    hero("RELEASE MANAGEMENT","Release Center","Maintain an auditable record of application releases by environment and version.")
    p=project_selector("release_project")
    if p:
        with st.form("new_release"):
            c1,c2=st.columns(2)
            env=c1.selectbox("Target environment",["Development","Staging","Production"])
            version=c2.text_input("Release version",value="v1.0.0")
            status=st.selectbox("Release status",["SUCCESS","FAILED","ROLLED BACK"])
            notes=st.text_area("Release notes",placeholder="Changes included in this release")
            if st.form_submit_button("Record release",use_container_width=True):
                create_deployment(p["id"],env,version,status,notes)
                st.success("Release record saved.")
                st.rerun()
    deps=list_deployments(limit=100)
    if deps: st.dataframe(pd.DataFrame(deps),use_container_width=True,hide_index=True)
    else: st.info("No release records yet.")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#7187a5;font-size:11px">NEXUS INTELLIGENT DEVOPS · LOCAL SOFTWARE PROTOTYPE · NO HARDWARE REQUIRED</div>',unsafe_allow_html=True)
