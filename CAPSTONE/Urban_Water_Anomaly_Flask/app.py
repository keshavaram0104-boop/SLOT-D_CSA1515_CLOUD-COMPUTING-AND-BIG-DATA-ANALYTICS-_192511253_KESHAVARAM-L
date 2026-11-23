from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from io import BytesIO
import pandas as pd, json, os
from datetime import datetime
from database import init_db, save_analysis, list_analyses, load_analysis, get_alerts
from processing import clean_data, analyze_data, REQUIRED
from reports import make_pdf

ROOT=Path(__file__).resolve().parent
UPLOAD=ROOT/"data"/"uploads"
UPLOAD.mkdir(parents=True,exist_ok=True)
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","local-development-key-change-me")
app.config["MAX_CONTENT_LENGTH"]=25*1024*1024
init_db()

def current_result():
    aid=request.args.get("analysis_id",type=int)
    if aid:
        saved=load_analysis(aid)
        if saved: return saved
    rows=list_analyses()
    return load_analysis(rows[0]["id"]) if rows else None

@app.route("/")
def dashboard():
    saved=current_result()
    if saved:
        df=saved["df"]; meta=saved["meta"]
        byloc=df.groupby("Location")["Water_Consumption_Liters"].mean().sort_values(ascending=False).round(1).to_dict()
        byday=df.assign(Date=pd.to_datetime(df.Date)).groupby(df.Date.astype(str))["Water_Consumption_Liters"].sum().to_dict()
        recent=df[df.Status=="Anomaly"].sort_values("Water_Consumption_Liters",ascending=False).head(6).to_dict("records")
    else:
        meta=None; byloc={}; byday={}; recent=[]
    return render_template("dashboard.html",meta=meta,byloc=byloc,byday=byday,recent=recent,history=list_analyses()[:5])

@app.route("/upload",methods=["GET","POST"])
def upload():
    preview=None
    if request.method=="POST":
        f=request.files.get("dataset")
        if not f or not f.filename:
            flash("Choose a CSV file first.","error")
            return redirect(url_for("upload"))
        if Path(f.filename).suffix.lower()!=".csv":
            flash("Only CSV files are accepted.","error")
            return redirect(url_for("upload"))
        try:
            df=pd.read_csv(f)
            missing=[c for c in REQUIRED if c not in df.columns]
            if missing: raise ValueError("Missing required columns: "+", ".join(missing))
            safe=secure_filename(f.filename) or "dataset.csv"
            dest=UPLOAD/(datetime.now().strftime("%Y%m%d_%H%M%S_")+safe)
            df.to_csv(dest,index=False)
            session_name=safe
            cleaned,clean_stats=clean_data(df)
            result,meta=analyze_data(cleaned,session_name,request.form.get("method","IQR"),float(request.form.get("multiplier",1.5)))
            aid=save_analysis(meta,result)
            flash(f"Dataset processed successfully. Analysis #{aid} saved.","success")
            return redirect(url_for("dashboard",analysis_id=aid))
        except Exception as e:
            flash(f"Could not process dataset: {e}","error")
    return render_template("upload.html",sample_count=240)

@app.route("/sample",methods=["POST"])
def sample():
    import numpy as np
    from datetime import timedelta
    rng=np.random.default_rng(42); zones=["North Zone","South Zone","East Zone","West Zone","Central Zone"]
    rows=[]; start=datetime(2026,1,1)
    for i in range(240):
        prev=float(max(150,rng.normal(420,70))); cur=float(max(80,rng.normal(prev,42)))
        if i in [17,58,101,177,221]: cur=prev*3.5
        rows.append({"Consumer_ID":f"C{1000+i:04d}","Location":zones[i%5],"Date":(start+timedelta(days=i%90)).strftime("%Y-%m-%d"),"Water_Consumption_Liters":round(cur,2),"Previous_Consumption_Liters":round(prev,2)})
    df=pd.DataFrame(rows)
    result,meta=analyze_data(df,"sample_water_consumption.csv",request.form.get("method","IQR"),1.5)
    aid=save_analysis(meta,result)
    df.to_csv(UPLOAD/"sample_water_consumption.csv",index=False)
    flash(f"Sample dataset processed: {len(result)} records; {meta['anomaly_count']} anomalies detected.","success")
    return redirect(url_for("dashboard",analysis_id=aid))

@app.route("/analysis")
def analysis():
    saved=current_result()
    if not saved:
        flash("Upload or generate a dataset to begin.","info")
        return redirect(url_for("upload"))
    df=saved["df"]
    q=request.args.get("q","").strip().lower()
    status=request.args.get("status","All")
    location=request.args.get("location","All")
    severity=request.args.get("severity","All")
    view=df.copy()
    if q: view=view[view.astype(str).apply(lambda col: col.str.lower().str.contains(q,na=False)).any(axis=1)]
    if status!="All": view=view[view.Status==status]
    if location!="All": view=view[view.Location==location]
    if severity!="All": view=view[view.Severity==severity]
    return render_template("analysis.html",rows=view.head(500).to_dict("records"),meta=saved["meta"],locations=sorted(df.Location.unique()),filters={"q":q,"status":status,"location":location,"severity":severity},analysis_id=saved["meta"]["id"])

@app.route("/alerts")
def alerts():
    saved=current_result()
    if not saved: return render_template("alerts.html",rows=[],meta=None)
    df=saved["df"]; anomalies=df[df.Status=="Anomaly"].sort_values("Water_Consumption_Liters",ascending=False)
    sev=request.args.get("severity","All")
    if sev!="All": anomalies=anomalies[anomalies.Severity==sev]
    return render_template("alerts.html",rows=anomalies.to_dict("records"),meta=saved["meta"],severity=sev)

@app.route("/history")
def history():
    return render_template("history.html",items=list_analyses())

@app.route("/reports")
def reports():
    saved=current_result()
    return render_template("reports.html",saved=saved)

@app.route("/export/csv")
def export_csv():
    saved=current_result()
    if not saved: return redirect(url_for("upload"))
    buf=BytesIO(saved["df"].to_csv(index=False).encode("utf-8"))
    return send_file(buf,mimetype="text/csv",as_attachment=True,download_name="urban_water_analysis.csv")

@app.route("/export/pdf")
def export_pdf():
    saved=current_result()
    if not saved: return redirect(url_for("upload"))
    data=make_pdf(saved["meta"],saved["df"])
    return send_file(BytesIO(data),mimetype="application/pdf",as_attachment=True,download_name="urban_water_analysis_report.pdf")

@app.route("/system")
def system():
    return render_template("system.html")

@app.route("/api/summary")
def api_summary():
    saved=current_result()
    if not saved: return jsonify({"ready":False})
    return jsonify({"ready":True,"meta":saved["meta"]})

if __name__=="__main__":
    app.run(host="127.0.0.1",port=int(os.environ.get("PORT",5000)),debug=False)
