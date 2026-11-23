from io import BytesIO
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
def make_pdf(meta,df):
    b=BytesIO(); doc=SimpleDocTemplate(b,pagesize=landscape(A4)); s=getSampleStyleSheet()
    story=[Paragraph("Urban Water Consumption Anomaly Report",s["Title"]),Paragraph(f"Dataset: {meta['dataset_name']} | Detection: {meta['method']}",s["Normal"]),Spacer(1,12)]
    rows=[["Metric","Value"],["Records",meta["total_records"]],["Normal",meta["normal_count"]],["Anomalies",meta["anomaly_count"]],["Anomaly rate",f"{meta['anomaly_percent']}%"],["Mean consumption",f"{meta['mean']} L"],["Min / Max",f"{meta['minimum']} / {meta['maximum']} L"],["Total consumption",f"{meta['total']} L"]]
    t=Table(rows,colWidths=[180,220]); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17324d")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.4,colors.grey),("PADDING",(0,0),(-1,-1),6)])); story += [t,Spacer(1,14),Paragraph("Anomaly records (first 40)",s["Heading2"])]
    a=df[df.Status=="Anomaly"].head(40); data=[["Consumer","Location","Date","Liters","Severity"]]+[[str(r.Consumer_ID),str(r.Location),str(r.Date),f"{r.Water_Consumption_Liters:.1f}",str(r.Severity)] for _,r in a.iterrows()]
    if len(data)==1:data.append(["—","—","—","—","No anomalies"])
    t2=Table(data,repeatRows=1); t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17324d")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.3,colors.grey),("FONTSIZE",(0,0),(-1,-1),8)])); story.append(t2); doc.build(story); return b.getvalue()
