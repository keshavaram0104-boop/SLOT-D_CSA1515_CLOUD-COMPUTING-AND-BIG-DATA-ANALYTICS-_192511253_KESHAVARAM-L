# Urban Water Consumption Anomaly Detection — Flask Website

A conventional browser-based website built with Flask, HTML, CSS and JavaScript (not Streamlit).

## Run on Windows
1. Extract the ZIP.
2. Open the extracted folder.
3. Double-click `run_windows.bat`.
4. Wait for package installation and the local server to start.
5. Open `http://127.0.0.1:5000` in Chrome. Keep the terminal open.

Python 3.10+ (64-bit) is recommended. Python 3.13 is supported by current Flask/Pandas/NumPy wheels.

## Features
- Responsive HTML/CSS web interface with sidebar navigation.
- CSV upload, schema validation and data cleaning.
- Synthetic sample generator with inserted high consumption events.
- IQR and Z-score statistical detection plus sudden increase rule (>=100% from previous reading).
- Severity and reason labels.
- Dashboard charts generated from processed records using Chart.js.
- Search, status, location and severity filters.
- Persistent SQLite analysis history.
- CSV and PDF exports.
- Alerts and system architecture page.

## CSV columns
`Consumer_ID, Location, Date, Water_Consumption_Liters, Previous_Consumption_Liters`

## Manual run
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## Optional Spark
`requirements-spark.txt` lists optional PySpark. Install Java 17 and configure JAVA_HOME first. The Flask version currently uses local Pandas for its functional processing path; the System Information page explicitly identifies this. PySpark is not represented as a cloud cluster.

## Test
```powershell
pip install pytest
pytest -q
```
## Cloud deployment note
This is a locally running Flask web app with local SQLite storage. It is not deployed to a cloud provider. Cloud deployment, managed database, object storage, authentication and multi-node Spark require separate configuration.
