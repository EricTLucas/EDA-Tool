from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from eda_tool import build_html_report
import tempfile
import os

app = FastAPI()

@app.get("/")
async def home():
    return HTMLResponse("""
        <html>
            <body>
                <h2>EDA Automation Tool</h2>
                <p><a href="/upload">Upload a CSV file</a></p>
            </body>
        </html>
    """)

@app.get("/upload")
async def upload_form():
    return HTMLResponse("""
        <html>
            <body>
                <h2>Upload a CSV file</h2>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".csv">
                    <button type="submit">Generate Report</button>
                </form>
            </body>
        </html>
    """)

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    plot_dir = tempfile.mkdtemp()

    app.mount("/plots", StaticFiles(directory=plot_dir), name="plots")

    _ = build_html_report(tmp_path, output_dir="/plots")

    return HTMLResponse("""
        <html>
            <body>
                <script>
                    window.location.href = "/upload";
                </script>
                <p>Report generated in a new tab.</p>
            </body>
        </html>
    """)