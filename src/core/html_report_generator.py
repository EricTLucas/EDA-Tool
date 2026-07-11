import os
from pathlib import Path
from typing import Dict, List
import pandas as pd

def generate_eda_html(df: pd.DataFrame, profile: Dict, output_dir: str) -> str:
    """
    Generate a full HTML EDA report with:
    - Header navigation
    - Sections with titles + boxed content
    - Images loaded from output_dir
    """

    output_dir = Path(output_dir)

    
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>EDA Report</title>

<style>
    body {{
        font-family: Arial, sans-serif;
        background-color: #f7f7f7;
        margin: 0;
        padding-top: 40px;
    }}

    .container {{
        margin-left: 10%;
        margin-right: 10%;
    }}

    .header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: white;
        border-bottom: 1px solid #ccc;
        z-index: 100;

        /* No padding that mimics body margins */
        padding: 15px 0;

        /* Full-width flex container */
        display: flex;
        justify-content: flex-end;
    }}

    
    .header-content {{
        width: 100%;
        max-width: 100%;
        display: flex;
        justify-content: flex-end;
        gap: 20px;
        font-size: 16px;

        padding-right: 20px;
    }}


    .nav-link {{
        text-decoration: none;
        color: #0077cc;
        font-weight: bold;
        font-size: 16px;
    }}

    .section {{
        margin-top: 40px;
    }}

    .section-title {{
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 10px;
    }}

    .section-box {{


        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}

    .image-box {{
        margin-bottom: 20px;
        text-align: center;
    }}

    .image-box img {{
        max-width: 100%;
        border-radius: 6px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
    }}

    .image-caption {{
        margin-top: 5px;
        font-size: 14px;
        color: #555;
    }}
    /* Tabs container */
    .tabs {{
        display: flex;
        gap: 10px;
        border-bottom: 1px solid #ccc;
        margin-bottom: 15px;
    }}

    /* Tab buttons */
    .tab-button {{
        background: #eee;
        border: none;
        padding: 10px 15px;
        cursor: pointer;
        font-weight: bold;
        border-radius: 6px 6px 0 0;
        color: #555;
    }}

    .tab-button.active {{
        background: white;
        border-bottom: 2px solid white;
        color: #000;
    }}

    /* Tab content */
    

    .tab-content {{
        display: block;        /* always block so width is real */
        visibility: hidden;    /* hide when inactive */
        height: 0;             /* collapse height */
        overflow: hidden;      /* prevent showing content */
    }}

    .tab-content.active {{
        visibility: visible;
        height: auto;
        overflow: visible;
    }}

    .table-box {{
        width: auto;
        border-radius: 6px;
        border: 1px solid #ccc;
        margin-bottom: 20px;
        overflow: hidden; /* no scroll unless container forces it */

    }}

    /* width options */
    .table-w1  {{ flex: 0 0 100%; }}
    .table-w2  {{ flex: 1 1 0; max-width: 50%; }}
    .table-w3  {{ flex: 1 1 0; max-width: 33.333%; }}


    .table-box table {{
        width: 100%;
        border-collapse: collapse;
    }}

    .table-box tr {{
        height: 38px;              
    }}

    .table-box td {{
        padding: 8px 12px;
        vertical-align: middle;
    }}

    .table-box .label {{
        font-weight: bold;
        width: 80%;
    }}

    .table-box .value {{
        width: 20%;
        
    }}

    .table-box .avalue {{
        width: 80%;
    }}

    .value-red {{
        background: #d9534f;   
        color: white; 
        text-align: center;
        padding: 2px 4px;
        border-radius: 7px;
        display: inline-block;
    }}

    .value-blue {{
        background: #00A8FF;   
        color: white; 
        text-align: center;
        padding: 2px 4px;
        border-radius: 7px;
        display: inline-block;
    }}

    .value-grey {{
        background: #2B2B2B;   
        color: white; 
        text-align: center;
        padding: 2px 4px;
        border-radius: 7px;
        display: inline-block;
    }}


    /* alternating row colors */
    .table-box tr:nth-child(odd) {{
        background: #f2f2f2;
    }}

    .table-box tr:nth-child(even) {{
        background: #ffffff;
    }}

    .table-wrapper {{
        display: flex;
        flex-direction: column;
    }}

    .table-title {{
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 20px; 
    }}

    .row-flex {{
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
    }}

    .flex-item {{
        display: block;
    }}

    .alert-badge {{
        display: inline-block;
        min-width: 18px;
        padding: 2px 6px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        background: #d9534f; /* red */
        border-radius: 12px;
        margin-left: 6px;
        line-height: 1;
    }}

    /* horizontal scroll */
    

    .scroll-x {{
        display: block;
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
    }}

    /* index column styling */
    .index-col {{
        font-weight: bold;
        background: #f0f0f0;
        width: 60px;
        text-align: center;
        border-right: 1px solid #ccc;
    }}

    /* header cells */
    .df-head-table th {{
        font-weight: bold;
        background: #f0f0f0;
        padding: 8px 12px;
        border-bottom: 1px solid #ccc;
    }}

    /* ensure table cells don't wrap */
    .df-head-table td {{
        white-space: nowrap;
    }}


    .graph-container {{
        width: 100%;
        max-width: 600px;

        /* REMOVE height constraints */
        height: auto;

        /* REMOVE max-height: 400px; */
        /* REMOVE overflow: hidden; */

        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        text-align: center;
    }}

    .graph-container img {{
        width: auto;
        height: auto;
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }}

    .graph-container-third {{
        width: 33.333%;          
        max-width: 100%;         
        height: auto;
        max-height: 400px;       
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        text-align: center;
    }}

    .graph-container-third img {{
        width: auto;
        height: auto;
        max-width: 100%;         /* shrink proportionally to container width */
        max-height: 100%;        /* shrink proportionally to container height */
        object-fit: contain;     /* never crop, never distort */
    }}


    .interactions-tabs,
    .interactions-subtabs {{
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }}

    .interactions-tab-button,
    .interactions-subtab-button {{
        padding: 0.25rem 0.5rem;
        cursor: pointer;
    }}

    .interactions-tab-button-active,
    .interactions-subtab-button-active {{
        background-color: #ddd;
    }}

    .interactions-tab-content,
    .interactions-subtab-content {{
        display: none;
    }}

    .interactions-tab-content-active,
    .interactions-subtab-content-active {{
        display: block;
    }}
    #variables .variable-box {{
        margin-bottom: 20px;   
    }}

    .variable-title {{
        font-size: 30px;
    }}

    .variable-type {{
        font-size: 20px;
        color: grey;
        padding-bottom: 10px;
        padding-top: 10px;
    }}


</style>
</head>

<body>

<div class="header">
    <div class="header-content">
        <a class="nav-link" href="#overview">Overview</a>
        <a class="nav-link" href="#variables">Variables</a>
        <a class="nav-link" href="#interactions">Interactions</a>
        <a class="nav-link" href="#correlations">Correlations</a>
        <a class="nav-link" href="#missing">Missing</a>
        <a class="nav-link" href="#sample">Sample</a>
    </div>
</div>
<div class="container">

"""
    ohtml, var_alerts = build_overview_section(profile)
    html += ohtml
    html += build_variables_section(profile, var_alerts, output_dir)
    html += build_interactions_section_html(profile, output_dir)
    html += corr_table_to_html(profile["correlations"].data, output_dir, width="1")
    html += build_missing_section(profile, output_dir)
    html += build_sample_section(profile)

    html += """
</div>
</body>
<script>

document.addEventListener("click", function(e) {
    if (!e.target.classList.contains("tab-button")) return;

    const tabId = e.target.dataset.tab;

    // Scope = the nearest .tabs container
    const tabsContainer = e.target.closest(".tabs");

    // Deactivate only buttons inside this tabs container
    tabsContainer.querySelectorAll(".tab-button").forEach(btn => {
        btn.classList.remove("active");
    });

    // Activate clicked button
    e.target.classList.add("active");

    // Find the parent section-box that contains the content blocks
    const sectionBox = tabsContainer.closest(".section-box");

    // Deactivate only content blocks inside this section-box
    sectionBox.querySelectorAll(".tab-content").forEach(cnt => {
        cnt.classList.remove("active");
    });

    // Activate the matching content
    const content = sectionBox.querySelector("#" + tabId);
    if (content) content.classList.add("active");
});


document.addEventListener("DOMContentLoaded", function() {
    // Top-level interactions tabs (col1)
    const interactionsBox = document.querySelector(".interactions-box");
    if (!interactionsBox) return;

    const topButtons = interactionsBox.querySelectorAll(".interactions-tab-button");
    const topContents = interactionsBox.querySelectorAll(".interactions-tab-content");

    topButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.dataset.interactionsTab;

            // deactivate all top-level
            topButtons.forEach(b => b.classList.remove("interactions-tab-button-active"));
            topContents.forEach(c => c.classList.remove("interactions-tab-content-active"));

            // activate clicked
            btn.classList.add("interactions-tab-button-active");
            const targetContent = interactionsBox.querySelector("#" + targetId);
            if (targetContent) {
                targetContent.classList.add("interactions-tab-content-active");

                // inside this content, activate FIRST nested subtab by default
                const nestedButtons = targetContent.querySelectorAll(".interactions-subtab-button");
                const nestedContents = targetContent.querySelectorAll(".interactions-subtab-content");

                nestedButtons.forEach(b => b.classList.remove("interactions-subtab-button-active"));
                nestedContents.forEach(c => c.classList.remove("interactions-subtab-content-active"));

                if (nestedButtons.length > 0 && nestedContents.length > 0) {
                    nestedButtons[0].classList.add("interactions-subtab-button-active");
                    nestedContents[0].classList.add("interactions-subtab-content-active");
                }
            }
        });
    });

    // Nested interactions subtabs (col2)
    interactionsBox.querySelectorAll(".interactions-tab-content").forEach(topContent => {
        const nestedButtons = topContent.querySelectorAll(".interactions-subtab-button");
        const nestedContents = topContent.querySelectorAll(".interactions-subtab-content");

        nestedButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetId = btn.dataset.interactionsSubtab;

                nestedButtons.forEach(b => b.classList.remove("interactions-subtab-button-active"));
                nestedContents.forEach(c => c.classList.remove("interactions-subtab-content-active"));

                btn.classList.add("interactions-subtab-button-active");
                const targetContent = topContent.querySelector("#" + targetId);
                if (targetContent) {
                    targetContent.classList.add("interactions-subtab-content-active");
                }
            });
        });
    });
});


</script>
</html>
"""
    return html

def build_table_component(data: dict, title: str, width: str = "1/2") -> str:
    width_class = {
        "1": "table-w1",
        "1/2": "table-w2",
        "1/3": "table-w3"
    }.get(width, "table-w2")

    
    if not data:
        rows_html = "<tr><td class='label'>No data</td><td class='value'></td></tr>"
    else:
        rows_html = "".join(
            f"<tr><td class='label'>{k}</td><td class='value'>{v}</td></tr>"
            for k, v in data.items()
        )

    return f"""
    <div class="table-wrapper {width_class}">
        <div class="table-title">{title}</div>
        <div class="table-box">
            <table>
                {rows_html}
            </table>
        </div>
    </div>
    """


def build_overview_section(profile: dict) -> str:
    """
    Build the HTML for the Overview section, including tabs:
    - Overview
    - Alerts
    Returns a string of HTML to be inserted into the main document.
    """

    # ---- Extract content ----

    raw_overview_data = profile["summary"].data
    raw_col_data = profile["columns"].data
    raw_alerts_data = profile["warnings"].data
    def prepOverviewData(data:dict) -> dict:
        return {
            "Number of Variables" : data["cols"],
            "Number of Observations" : data["rows"],
            "Missing Cells" : data["num_missing_cells"],
            "Missing Cells (%)" : f"{(data["percent_missing_cells"] * 100):.2f}%",
            "Duplicate Rows" : data["num_duplicates"],
            "Duplicate Rows (%)" : f"{(data["percent_duplicates"]*100):.2f}%",
            "Total Size in Memory" :  f"{data['total_memory_usage'] / 1024:.2f} KiB"
,
            }
    
    def prepOverviewCol(data:dict) -> dict:
        num_count = cat_count = text_count = 0
        for col in data:
            dtype = data[col]["type"]
            if dtype == "numeric":
                num_count += 1
            elif dtype == "category":
                cat_count += 1
            elif dtype == "text":
                text_count += 1
        rdict = {}
        if num_count > 0:
            rdict["Numeric"] = num_count
        if cat_count > 0:
            rdict["Category"] = cat_count
        if text_count > 0:
            rdict["Text"] = text_count
        return rdict

    def prepAlertData(data: dict):
        rdict = {}
        num_alerts = 0
        for col in data:
            for alert in data[col]:
                num_alerts += 1
                if alert == "missing":
                        rdict[ data[col][alert] ]= ["Missing Values", "blue", col]
                if alert == "unique":
                        rdict[ data[col][alert]] = ["Unique", "red", col]
                if alert == "uniform_dist":
                        rdict[data[col][alert]] = ["Uniform", "red", col]
                if alert == "high_correlation":
                        rdict[ data[col][alert] ] = ["High Correlation", "grey", col]
                if alert == "negatives":
                        rdict[ data[col][alert] ] = ["Negatives", "blue", col]
                if alert == "zeros":
                        rdict[ data[col][alert] ] = ["Zeros", "blue", col]
                if alert == "infinity":
                        rdict[ data[col][alert] ] = ["Infinity", "blue", col]

        return rdict, num_alerts

    def build_alert_table(data: dict) -> str:
       
        width_class = "table-w1"

        if not data:
            rows_html = "<tr><td class='label'>No Alerts</td><td class='value'></td></tr>"
        else:
            rows_html = "".join(
                f"<tr><td class='avalue'>{k}</td><td class='value-{v[1]}'>{v[0]}</td></tr>"
                for k, v in data.items()
            )

        return f"""
        <div class="table-wrapper {width_class}">
            <div class="table-title">Alerts</div>
            <div class="table-box">
                <table>
                    {rows_html}
                </table>
            </div>
        </div>
        """

    overview_data = prepOverviewData(raw_overview_data)
    col_data = prepOverviewCol(raw_col_data)
    alerts_data, alert_count = prepAlertData(raw_alerts_data)


    overview_html = build_table_component(overview_data, "Dataset Statistics", "1/2")
    col_html = build_table_component(col_data, "Variable Types", "1/2")
    alerts_html = build_alert_table(alerts_data)

    alerts_data = alerts_data.values()

    

    # ---- Build tabbed section ----
    section_html = f"""
    <div class="section" id="overview">
        <div class="section-title">Overview</div>

        <div class="section-box">

            <div class="tabs">
                <button class="tab-button active" data-tab="overview-tab">Overview</button>
                <button class="tab-button" data-tab="alerts-tab">
                    Alerts <span class="alert-badge">{alert_count}</span>
                </button>
            </div>

            <div class="tab-content active" id="overview-tab">
                <div class="row-flex">
                    {overview_html}
                    {col_html}
                </div>
            </div>


            <div class="tab-content" id="alerts-tab">
                {alerts_html}
            </div>

        </div>
    </div>
    """

    return section_html, alerts_data


def build_variables_section(profile, var_alerts, output_dir):
    """
    Variables section:
    For each column in profile["columns"].data, display:
      numeric:
        - 1/3 summary table
        - 1/3 more summary table
        - 1/3 histogram image
      categorical:
        - 1/2 summary table
        - 1/2 bar chart image

    """

    columns = profile["columns"].data
    html_sections = []

    col_alerts = {}

    for col in columns:
        col_alerts[col] = []

    for alert in var_alerts:
        col_alerts[alert[2]].append( (alert[0], alert[1]) ) 
    
    for col in columns:
        col_data = columns[col]
        dtype = col_data["type"]

        if dtype == "numeric":
            col_sum_table1 = {
                    "Distinct": col_data["num_unique"],
                    "Distinct (%)": f"{col_data['pct_unique']*100:.2f}%",
                    "Missing": col_data["num_missing"],
                    "Missing (%)": f"{col_data['pct_missing']*100:.2f}%",
                    "Infinite": col_data["num_infinity"],
                    "Infinite (%)": f"{col_data['pct_infinity']*100:.2f}%",
                    "Mean": f"{col_data['mean']:.2f}",
                }
            col_sum_table2 = {
                    "Minimum": col_data["min"],
                    "Maximum": col_data["max"],
                    "Zeros": col_data["num_zeros"],
                    "Zeros (%)": f"{col_data['pct_zeros']*100:.2f}%",
                    "Negative": col_data["num_neg"],
                    "Negative (%)": f"{col_data['pct_neg']*100:.2f}%",
                    "Memory size (KiB)": f"{col_data['memory_size'] / 1024:.2f}",
                }
            col_sum_table1_html = build_table_component(col_sum_table1, "", "1/3")
            col_sum_table2_html = build_table_component(col_sum_table2, "", "1/3")
            hist_path = os.path.join(output_dir, f"hist_{col}.png")

            col_alert_html = ""

            for col_alert_entries in col_alerts[col]:
                
                col_alert_html += f"""
                <div class='value-{col_alert_entries[1]}'>{col_alert_entries[0]}</div>
                """

            section_html = f"""
            <div class="section-box variable-box">
                <div class="variable-title">{col}</div>
                <div class="variable-type">Real Number</div>
                {col_alert_html}
                <div class="row-flex">
                        {col_sum_table1_html}
                        {col_sum_table2_html}
                        <div class="graph-container-third">
                            <img src="{hist_path}" alt="{col} Histograph">
                        </div>
                </div>
            </div>
            """

            html_sections.append(section_html)

        elif dtype == "category":
            col_sum_table = {
                    "Distinct": col_data["num_unique"],
                    "Distinct (%)": f"{col_data['pct_unique']*100:.2f}%",
                    "Missing": col_data["num_missing"],
                    "Missing (%)": f"{col_data['pct_missing']*100:.2f}%",
                    "Memory size (KiB)": f"{col_data['memory_size'] / 1024:.2f}",
                }
            col_sum_table_html = build_table_component(col_sum_table, "", "1/2")
            bar_path = os.path.join(output_dir, f"cat_{col}.png")

            col_alert_html = ""

            for col_alert_entries in col_alerts[col]:
                
                col_alert_html += f"""
                <div class='value-{col_alert_entries[1]}'>{col_alert_entries[0]}</div>
                """

            section_html = f"""
            <div class="section-box variable-box">
                <div class="variable-title">{col}</div>
                <div class="variable-type">Categorical</div>
                {col_alert_html}
                <div class="row-flex">
                        {col_sum_table_html}
                        <div class="graph-container">
                            <img src="{bar_path}" alt="{col} Histograph">
                        </div>
                </div>
            </div>
            """

            html_sections.append(section_html)

        elif dtype == "text":
            col_sum_table = {
                    "Distinct": col_data["num_unique"],
                    "Distinct (%)": f"{col_data['pct_unique']*100:.2f}%",
                    "Missing": col_data["num_missing"],
                    "Missing (%)": f"{col_data['pct_missing']*100:.2f}%",
                    "Memory size (KiB)": f"{col_data['memory_size'] / 1024:.2f}",
                }
            col_sum_table_html = build_table_component(col_sum_table, "", "1/2")
            cloud_path = os.path.join(output_dir, f"wordcloud_{col}.png")

            col_alert_html = ""

            for col_alert_entries in col_alerts[col]:
                
                col_alert_html += f"""
                <div class='value-{col_alert_entries[1]}'>{col_alert_entries[0]}</div>
                """

            section_html = f"""
            <div class="section-box variable-box">
                <div class="variable-title">{col}</div>
                <div class="variable-type">Text</div>
                {col_alert_html}
                <div class="row-flex">
                        {col_sum_table_html}
                        <div class="graph-container">
                            <img src="{cloud_path}" alt="{col} WordCloud">
                        </div>
                </div>
            </div>
            """

            html_sections.append(section_html)

    final_html = f"""
    <div class="section" id="variables">
        <div class="section-title">Variables</div>
        {''.join(html_sections)}
    </div>
    """

    return final_html


def build_interactions_section_html(profile, output_dir):
    """
    Interactions section:
    - profile["interactions"].data["pairs"] = [(col1, col2), ...]
    - Top-level interactions-tab (col1)
    - Nested interactions-subtab (col2)
    """

    pairs = profile["interactions"].data["pairs"]

    # Group by col1
    interactions = {}
    for col1, col2 in pairs:
        interactions.setdefault(col1, []).append(col2)

    top_tabs_html = ""
    top_contents_html = ""

    col1_list = list(interactions.keys())

    # Top-level tabs (col1)
    for i, col1 in enumerate(col1_list):
        active_class = "interactions-tab-button-active" if i == 0 else ""
        top_tabs_html += f"""
            <button class="interactions-tab-button {active_class}" data-interactions-tab="interact-{col1}">
                {col1}
            </button>
        """

    # Contents per col1
    for i, (col1, col2_list) in enumerate(interactions.items()):
        top_active_class = "interactions-tab-content-active" if i == 0 else ""

        nested_tabs_html = ""
        nested_contents_html = ""

        for j, col2 in enumerate(col2_list):
            nested_active_btn = "interactions-subtab-button-active" if j == 0 else ""
            nested_active_content = "interactions-subtab-content-active" if j == 0 else ""

            nested_tabs_html += f"""
                <button class="interactions-subtab-button {nested_active_btn}" data-interactions-subtab="interact-{col1}-{col2}">
                    {col2}
                </button>
            """

            img_path = os.path.join(output_dir, f"scatter_{col1}_vs_{col2}.png")

            nested_contents_html += f"""
                <div class="interactions-subtab-content {nested_active_content}" id="interact-{col1}-{col2}">
                    <div class="graph-container">
                        <img src="{img_path}" alt="Scatter {col1} vs {col2}">
                    </div>
                </div>
            """

        top_contents_html += f"""
            <div class="interactions-tab-content {top_active_class}" id="interact-{col1}">
                <div class="section-box interactions-inner-box">
                    <div class="interactions-subtabs">
                        {nested_tabs_html}
                    </div>
                    <div class="interactions-subtab-contents">
                        {nested_contents_html}
                    </div>
                </div>
            </div>
        """

    html = f"""
    <div class="section" id="interaction">
        <div class="section-title">Interactions</div>

        <div class="section-box interactions-box">
            <div class="interactions-tabs">
                {top_tabs_html}
            </div>
            <div class="interactions-tab-contents">
                {top_contents_html}
            </div>
        </div>
    </div>
    """

    return html


def corr_table_to_html(corr_df, output_dir, width="1"):
    """
    Convert a correlation DataFrame into a scrollable HTML table
    with index column and 2-decimal formatting.
    """

    heatmap_path = os.path.join(output_dir, "correlation_heatmap.png")

    # Width class mapping
    width_class = {
        "1": "table-w1",
        "1/2": "table-w2",
        "1/3": "table-w3"
    }.get(width, "table-w1")

    # Build header row (index + columns)
    header_html = "<th class='index-col'>Column</th>" + "".join(
        f"<th>{col}</th>" for col in corr_df.columns
    )

    # Build body rows
    body_html = ""
    for idx, row in corr_df.iterrows():
        row_html = f"<td class='index-col'>{idx}</td>" + "".join(
            f"<td>{val:.2f}</td>" for val in row.values
        )
        body_html += f"<tr>{row_html}</tr>"

    # Wrap in scrollable container
    return f"""
    <div class="section" id="correlation">
        <div class="section-title">Correlations</div>

        <div class="section-box">

            <div class="tabs">
                <button class="tab-button active" data-tab="heatmap">Heatmap</button>
                <button class="tab-button" data-tab="corrtable">Table</button>
            </div>

            <div class="tab-content active" id="heatmap">
                <div class="graph-container">
                    <img src="{heatmap_path}" alt="Graph">
                </div>
            </div>

            <div class="tab-content" id="corrtable">
                <div class="table-wrapper {width_class}">
                    <div class="table-title">Correlation Matrix</div>

                    <div class="table-box scroll-x">
                        <table class="df-head-table">
                            <thead>
                                <tr>{header_html}</tr>
                            </thead>
                            <tbody>
                                {body_html}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>

        </div>
    </div>
    """


def build_missing_section(profile: dict, output_dir) -> str:
    if profile["summary"].data["num_missing_cells"] == 0:
        return ""

    count_path = os.path.join(output_dir, "missing_barchart.png")
    matrix_path = os.path.join(output_dir, "missing_matrix_bars.png")

    section_html = f"""
    <div class="section" id="missing">
        <div class="section-title">Missing Values</div>

        <div class="section-box">

            <div class="tabs">
                <button class="tab-button active" data-tab="count">Count</button>
                <button class="tab-button" data-tab="matrix">Matrix</button>
            </div>

            <div class="tab-content active" id="count">
                <div class="graph-container">
                    <img src="{count_path}" alt="Graph">
                </div>
            </div>


            <div class="tab-content" id="matrix">
                <div class="graph-container">
                    <img src="{matrix_path}" alt="Graph">
                </div>
            </div>

        </div>
    </div>
    """
    return section_html

def build_sample_section(profile: dict) -> str:

    def df_head_to_html(head, width="1"):
        """
        Convert df.head(n) into a horizontally scrollable HTML table.
        Automatically adds an index column on the left.
        """

        # Width class mapping
        width_class = {
            "1": "table-w1",
            "1/2": "table-w2",
            "1/3": "table-w3"
        }.get(width, "table-w1")

        # Build header row (index + columns)
        header_html = "<th class='index-col'>Index</th>" + "".join(
            f"<th>{col}</th>" for col in head.columns
        )

        # Build body rows
        body_html = ""
        for idx, row in head.iterrows():
            row_html = f"<td class='index-col'>{idx}</td>" + "".join(
                f"<td>{row[col]}</td>" for col in head.columns
            )
            body_html += f"<tr>{row_html}</tr>"

        # Wrap in scrollable container
        return f"""
        <div class="table-wrapper {width_class}">
        
            <div class="table-box scroll-x">
                <table class="df-head-table">
                    <thead>
                        <tr>{header_html}</tr>
                    </thead>
                    <tbody>
                        {body_html}
                    </tbody>
                </table>
            </div>
        </div>
        """

    head_html = df_head_to_html(profile["summary"].data["sample_values_first"], width="1")
    tail_html = df_head_to_html(profile["summary"].data["sample_values_last"], width="1")

    section_html = f"""
    <div class="section" id="sample">
        <div class="section-title">Sample</div>

        <div class="section-box">

            <div class="tabs">
                <button class="tab-button active" data-tab="first_sample">First 10</button>
                <button class="tab-button" data-tab="last_sample">Last 10</button>
            </div>

            <div class="tab-content active" id="first_sample">
                {head_html}
            </div>


            <div class="tab-content" id="last_sample">
                {tail_html}
            </div>

        </div>
    </div>
    """
    return section_html