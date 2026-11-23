import sqlite3
from pathlib import Path
from datetime import datetime
DB_PATH=Path(__file__).parent/"data"/"nexus_devops.db"

def connect():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(DB_PATH,timeout=20)
    con.row_factory=sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def now(): return datetime.now().isoformat(timespec="seconds")

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS projects(
          id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,repo_url TEXT,branch TEXT NOT NULL,
          description TEXT,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS pipeline_runs(
          id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER NOT NULL,status TEXT NOT NULL,
          duration_seconds REAL NOT NULL,commit_summary TEXT,profile TEXT,stages_json TEXT,created_at TEXT NOT NULL,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS log_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER,level TEXT,anomaly TEXT,message TEXT,created_at TEXT,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS metrics(
          id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER NOT NULL,cpu REAL,memory REAL,errors INTEGER,
          latency REAL,risk_score INTEGER,status TEXT,created_at TEXT,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS deployments(
          id INTEGER PRIMARY KEY AUTOINCREMENT,project_id INTEGER NOT NULL,environment TEXT,version TEXT,
          status TEXT,notes TEXT,created_at TEXT,
          FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE);
        """)
def _rows(sql,args=()):
    with connect() as c: return [dict(r) for r in c.execute(sql,args).fetchall()]
def create_project(name,repo,branch,description):
    with connect() as c: c.execute("INSERT INTO projects(name,repo_url,branch,description,created_at) VALUES(?,?,?,?,?)",(name,repo,branch,description,now()))
def list_projects():
    return _rows("SELECT * FROM projects ORDER BY id DESC")
def delete_project(pid):
    with connect() as c: c.execute("DELETE FROM projects WHERE id=?",(pid,))
def create_pipeline_run(pid,result):
    import json
    with connect() as c:
        c.execute("INSERT INTO pipeline_runs(project_id,status,duration_seconds,commit_summary,profile,stages_json,created_at) VALUES(?,?,?,?,?,?,?)",
        (pid,result["status"],result["duration_seconds"],result["commit_summary"],result["profile"],json.dumps(result["stages"]),now()))
def list_pipeline_runs(project_id=None,limit=50):
    sql="SELECT r.id,p.name AS project_name,r.status,r.duration_seconds,r.commit_summary,r.profile,r.created_at FROM pipeline_runs r JOIN projects p ON p.id=r.project_id"
    return _rows(sql+(" WHERE r.project_id=?" if project_id else "")+" ORDER BY r.id DESC LIMIT ?",((project_id,limit) if project_id else (limit,)))
def add_log_events(pid,events):
    with connect() as c:
        c.executemany("INSERT INTO log_events(project_id,level,anomaly,message,created_at) VALUES(?,?,?,?,?)",
        [(pid,e["level"],e["anomaly"],e["message"],now()) for e in events])
def list_log_events(project_id=None,limit=100):
    sql="SELECT l.id,p.name AS project_name,l.level,l.anomaly,l.message,l.created_at FROM log_events l LEFT JOIN projects p ON p.id=l.project_id"
    return _rows(sql+(" WHERE l.project_id=?" if project_id else "")+" ORDER BY l.id DESC LIMIT ?",((project_id,limit) if project_id else (limit,)))
def save_metrics(pid,cpu,memory,errors,latency,score,status):
    with connect() as c: c.execute("INSERT INTO metrics(project_id,cpu,memory,errors,latency,risk_score,status,created_at) VALUES(?,?,?,?,?,?,?,?)",(pid,cpu,memory,errors,latency,score,status,now()))
def list_metrics(project_id=None,limit=100):
    sql="SELECT m.*,p.name AS project_name FROM metrics m JOIN projects p ON p.id=m.project_id"
    return _rows(sql+(" WHERE m.project_id=?" if project_id else "")+" ORDER BY m.id DESC LIMIT ?",((project_id,limit) if project_id else (limit,)))
def create_deployment(pid,env,version,status,notes):
    with connect() as c: c.execute("INSERT INTO deployments(project_id,environment,version,status,notes,created_at) VALUES(?,?,?,?,?,?)",(pid,env,version,status,notes,now()))
def list_deployments(limit=100):
    return _rows("SELECT d.*,p.name AS project_name FROM deployments d JOIN projects p ON p.id=d.project_id ORDER BY d.id DESC LIMIT ?",(limit,))
def dashboard_summary():
    with connect() as c:
        return {"projects":c.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
                "runs":c.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0],
                "logs":c.execute("SELECT COUNT(*) FROM log_events").fetchone()[0],
                "deployments":c.execute("SELECT COUNT(*) FROM deployments").fetchone()[0]}
