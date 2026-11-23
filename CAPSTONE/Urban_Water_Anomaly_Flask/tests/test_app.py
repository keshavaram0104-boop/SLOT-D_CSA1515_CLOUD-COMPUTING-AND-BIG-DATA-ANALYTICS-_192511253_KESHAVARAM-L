import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import app
def test_pages():
    c=app.test_client()
    for path in ["/","/upload","/alerts","/history","/reports","/system"]:
        r=c.get(path); assert r.status_code==200, path
def test_sample_workflow():
    c=app.test_client()
    r=c.post("/sample",follow_redirects=True)
    assert r.status_code==200
    assert b"Analysis summary" in r.data
    assert c.get("/export/csv").status_code==200
    assert c.get("/export/pdf").status_code==200
