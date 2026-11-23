import pandas as pd,numpy as np
REQUIRED=["Consumer_ID","Location","Date","Water_Consumption_Liters","Previous_Consumption_Liters"]
def clean_data(df):
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: raise ValueError("Missing required columns: "+", ".join(missing))
    if df.empty: raise ValueError("CSV contains no records.")
    x=df[REQUIRED].copy()
    x["Consumer_ID"]=x.Consumer_ID.astype(str).str.strip()
    x["Location"]=x.Location.astype(str).str.strip()
    x["Date"]=pd.to_datetime(x.Date,errors="coerce")
    for c in REQUIRED[3:]: x[c]=pd.to_numeric(x[c],errors="coerce")
    before=len(x)
    x=x.dropna(subset=["Consumer_ID","Location","Date","Water_Consumption_Liters"])
    x=x[(x.Water_Consumption_Liters>=0)&(x.Previous_Consumption_Liters.fillna(0)>=0)]
    x["Previous_Consumption_Liters"]=x.Previous_Consumption_Liters.fillna(x.Water_Consumption_Liters)
    if x.empty: raise ValueError("No valid records remain after cleaning.")
    return x.reset_index(drop=True),{"input":before,"valid":len(x),"removed":before-len(x)}
def analyze_data(df,name,method="IQR",multiplier=1.5):
    x=df.copy(); vals=x.Water_Consumption_Liters.astype(float)
    if method=="Z-score":
        mean=vals.mean(); sd=vals.std(ddof=0)
        score=(vals-mean)/sd if sd else pd.Series(0,index=x.index)
        low,high=mean-3*sd,mean+3*sd
        stat=(score.abs()>3)
    else:
        q1,q3=vals.quantile(.25),vals.quantile(.75); iqr=q3-q1
        low,high=q1-multiplier*iqr,q3+multiplier*iqr
        score=(vals-q3)/iqr if iqr else pd.Series(0,index=x.index)
        stat=(vals<low)|(vals>high)
    pct=((vals-x.Previous_Consumption_Liters)/x.Previous_Consumption_Liters.replace(0,np.nan)).replace([np.inf,-np.inf],np.nan).fillna(0)*100
    sudden=pct>=100; flag=stat|sudden
    x["Anomaly_Score"]=score.round(3); x["Change_Percent"]=pct.round(1)
    x["Status"]=np.where(flag,"Anomaly","Normal")
    x["Severity"]=np.select([flag&((vals>high*1.5)|(pct>=200)),flag],["High","Medium"],default="None")
    x["Reason"]=["; ".join((["Outside statistical threshold"] if bool(stat.loc[i]) else [])+(["Consumption increased at least 100% vs previous reading"] if bool(sudden.loc[i]) else [])) or "Within expected range" for i in x.index]
    x["Date"]=pd.to_datetime(x.Date).dt.strftime("%Y-%m-%d")
    n=len(x); a=int(flag.sum())
    meta={"dataset_name":name,"total_records":n,"normal_count":n-a,"anomaly_count":a,"anomaly_percent":round(a/n*100,2),"mean":round(float(vals.mean()),2),"minimum":round(float(vals.min()),2),"maximum":round(float(vals.max()),2),"total":round(float(vals.sum()),2),"method":method}
    return x,meta
