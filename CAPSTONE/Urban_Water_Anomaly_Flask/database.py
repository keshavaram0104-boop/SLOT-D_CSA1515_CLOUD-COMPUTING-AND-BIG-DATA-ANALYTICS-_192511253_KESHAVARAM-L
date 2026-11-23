import sqlite3,json
from pathlib import Path
from datetime import datetime
import pandas as pd
DB=Path(__file__).resolve().parent/"data"/"water_analytics.db"
def conn():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS analyses(
        id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, dataset_name TEXT,
        total_records INTEGER, normal_count INTEGER, anomaly_count INTEGER,
        anomaly_percent REAL, mean REAL, minimum REAL, maximum REAL, total REAL,
        method TEXT, results_json TEXT)""")
def save_analysis(meta,df):
    with conn() as c:
        cur=c.execute("""INSERT INTO analyses(created_at,dataset_name,total_records,normal_count,anomaly_count,anomaly_percent,mean,minimum,maximum,total,method,results_json)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),meta["dataset_name"],meta["total_records"],meta["normal_count"],meta["anomaly_count"],meta["anomaly_percent"],meta["mean"],meta["minimum"],meta["maximum"],meta["total"],meta["method"],df.to_json(orient="records",date_format="iso")))
        return cur.lastrowid
def list_analyses():
    with conn() as c: return [dict(x) for x in c.execute("SELECT id,created_at,dataset_name,total_records,normal_count,anomaly_count,anomaly_percent,method FROM analyses ORDER BY id DESC")]
def load_analysis(aid):
    with conn() as c: row=c.execute("SELECT * FROM analyses WHERE id=?",(aid,)).fetchone()
    if not row:return None
    d=dict(row); df=pd.read_json(d["results_json"])
    meta={k:d[k] for k in ["id","created_at","dataset_name","total_records","normal_count","anomaly_count","anomaly_percent","mean","minimum","maximum","total","method"]}
    return {"meta":meta,"df":df}
def get_alerts():
    saved=list_analyses()
    if not saved:return []
    loaded=load_analysis(saved[0]["id"])
    return loaded["df"].query("Status == 'Anomaly'").to_dict("records")
