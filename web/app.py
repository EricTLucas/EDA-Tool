from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.concurrency import run_in_threadpool
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

    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)

    app.mount("/plots", StaticFiles(directory=output_dir), name="plots")

    # Run heavy pipeline in thread
    html_filename = await run_in_threadpool(build_html_report, tmp_path, output_dir)

    # Redirect to a GET route that can safely open a new tab
    return RedirectResponse(url=f"/report-ready?file={html_filename}", status_code=303)


@app.get("/report-ready")
async def report_ready(file: str):
    return HTMLResponse(f"""
        <html>
            <body>
                <script>
                    // Browser allows this because it's a GET navigation
                    window.open('/plots/{file}', '_blank');

                    // Return user to upload page
                    window.location.href = '/upload';
                </script>
                <p>Opening report...</p>
            </body>
        </html>
    """)