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
    - You call this AFTER visualize_dataset / other visualizers.
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / report_name

    # Discover all PNGs in the output_dir
    images = sorted(p for p in out.glob("*.png"))

    # Optional: build some text blocks from profile
    text_blocks = {
        "Dataset Shape": f"Rows: {df.shape[0]}\nColumns: {df.shape[1]}",
        "Column Types": _profile_column_types_text(profile),
        "Warnings": _profile_warnings_text(profile),
    }

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
        "img { max-width: 100%; height: auto; margin-bottom: 20px; }"
        "pre { background: #f5f5f5; padding: 10px; border-radius: 4px; }"
        "</style>"
    )
    html_parts.append("</head>")
    html_parts.append("<body>")

    # Title
    html_parts.append("<h1>EDA Report</h1>")

    # Text sections
    for title, text in text_blocks.items():
        if not text:
            continue
        html_parts.append(f"<h2>{html.escape(title)}</h2>")
        html_parts.append("<pre>")
        html_parts.append(html.escape(text))
        html_parts.append("</pre>")

    # Image sections (one section per file)
    for img_path in images:
        section_title = img_path.stem.replace("_", " ").title()
        html_parts.append(f"<h2>{html.escape(section_title)}</h2>")
        html_parts.append(f"<img src='{img_path.name}' alt='{html.escape(section_title)}'>")

    html_parts.append("</body>")
    html_parts.append("</html>")

    report_path.write_text("\n".join(html_parts), encoding="utf-8")
    return report_path


def _profile_column_types_text(profile: dict) -> str:
    cols = profile.get("columns", {})
    lines = []
    for name, info in cols.items():
        dtype = info.get("dtype", "unknown")
        lines.append(f"{name}: {dtype}")
    return "\n".join(lines)


def _profile_warnings_text(profile: dict) -> str:
    warnings = profile.get("warnings", [])
    if not warnings:
        return "None"
    return "\n".join(f"- {w}" for w in warnings)