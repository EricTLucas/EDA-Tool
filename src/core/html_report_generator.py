from pathlib import Path
import html
import pandas as pd


def generate_html_report(
    df: pd.DataFrame,
    profile: dict,
    output_dir: str,
    report_name: str = "eda_report.html",
):
    """
    Build a standalone HTML EDA report.

    Assumes:
    - All plots have already been saved as PNGs into output_dir
      (e.g., missing_values.png, correlation_heatmap.png, sample_entry.png, column_summary.png, etc.)
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / report_name

    # Discover all PNGs in the output_dir
    images = sorted(p for p in out.glob("*.png"))

    summary_images = ["Dataset_Info.png", "Sample_Entry.png", "Column_Summary.png", "Missing_By_Index.png"]

    summary_images = [img for img in summary_images if (out / img).exists()]

    write_html_report(report_path, summary_images, output_dir, html_content="")

    images = [str(img) for img in images if str(img) not in summary_images]

    sig_cols = [str(col).split("_Distribution.png")[0] for col in out.glob("*_Distribution.png")]

    sig_cols += [str(col).split("_Categories.png")[0] for col in out.glob("*_Categories.png")]

    sig_cols = [col.split("\\")[1] for col in sig_cols]

    for col in sig_cols:
        title = col.replace("_", " ")
        col_images = [img for img in images if col in img]
        col = col + "_report.html"
        
        col_report_path = out / col
        
        write_html_report(col_report_path, col_images, output_dir, html_content=title)


    return report_path

def write_html_report(report_path: Path, images: list, output_dir: str, html_content="Exploratory Data Analysis Report"):
    out = Path(output_dir)

    html_parts = []
    html_parts.append("<!DOCTYPE html>")
    html_parts.append("<html>")
    html_parts.append("<head>")
    html_parts.append("<meta charset='utf-8'>")
    html_parts.append("<title>EDA Report</title>")
    html_parts.append(
        "<style>"
        "body { font-family: Arial, sans-serif; margin: 20px; }"
        "h1, h2 { font-family: Arial, sans-serif; }"
        ".row { display: flex; flex-direction: row; margin-bottom: 30px; }"
        ".cell { flex: 1; padding-right: 20px; }"
        "img { width: 100%; height: auto; border: 1px solid #ccc; border-radius: 4px; }"
        "pre { background: #f5f5f5; padding: 10px; border-radius: 4px; }"
        "</style>"
    )
    html_parts.append("</head>")
    html_parts.append("<body>")

    # Title
    html_parts.append(f"<h1>{html_content}</h1>")

    for i in range(0, len(images), 2):
        html_parts.append("<div class='row'>")

        # First image in the row
        img1 = images[i]
        img1_path = out / img1
        title1 = img1_path.stem.replace("_", " ")
        html_parts.append("<div class='cell'>")
        html_parts.append(f"<h2>{html.escape(title1)}</h2>")
        html_parts.append(f"<img src='{img1_path.name}' alt='{html.escape(title1)}'>")
        html_parts.append("</div>")

        # Second image in the row (if exists)
        if i + 1 < len(images):
            img2 = images[i + 1]
            img2_path = out / img2
            title2 = img2_path.stem.replace("_", " ")
            html_parts.append("<div class='cell'>")
            html_parts.append(f"<h2>{html.escape(title2)}</h2>")
            html_parts.append(f"<img src='{img2_path.name}' alt='{html.escape(title2)}'>")
            html_parts.append("</div>")
        else:
            # If odd number of images, add an empty cell for alignment
            html_parts.append("<div class='cell'></div>")

        html_parts.append("</div>")  # end row

    html_parts.append("</body>")
    html_parts.append("</html>")

    report_path.write_text("\n".join(html_parts), encoding="utf-8")
    return report_path
