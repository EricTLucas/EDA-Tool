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


    .details-toggle-row {{
        display: flex;
        justify-content: flex-end; /* button goes to the right */
        margin-top: 10px;
        margin-bottom: 10px; /* space before details panel */
    }}

    .more-details-btn {{
        background: #e0e0e0;
        color: #333;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
        transition: background 0.2s;
    }}

    .more-details-btn:hover {{
        background: #d0d0d0;
    }}


    .details-panel {{
        display: none; /* hidden by default */
        margin-top: 15px;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 6px;
        background: #fafafa;
    }}

    .details-panel.open {{
        display: block;
    }}

    .details-tabs {{
        margin-bottom: 10px;
    }}

    .anchor-target {{
        scroll-margin-top: 45px; 
    }}

    .freq-table {{
        width: 100%;
        border-collapse: collapse;
    }}

    .freq-table th {{
        text-align: left;
        font-weight: bold;
        padding: 6px 8px;
        border-bottom: 1px solid #ccc;
    }}

    .freq-table td {{
        padding: 6px 8px;
        vertical-align: middle;
    }}

    .freq-value {{
        width: 60%;
    }}

    .freq-count {{
        width: 30%;
        text-align: right;
        padding-right: 12px;
    }}

    .freq-bar-cell {{
        width: 10%;
        position: relative;
    }}

    .freq-bar {{
        height: 100%;
        background: #4a90e2;
        position: absolute;
        left: 0;
        top: 0;
    }}

    .freq-percent-text {{
        position: relative;
        z-index: 2;
        font-size: 12px;
        text-align: right;
        padding-right: 4px;
    }}

    .inner-tabs {{
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
    }}

    .inner-tab-button {{
        background: #eee;
        border: none;
        padding: 10px 15px;
        cursor: pointer;
        font-weight: bold;
        border-radius: 6px 6px 0 0;
        color: #555;
    }}

    .inner-tab-button.active {{
        background: white;
        border-bottom: 2px solid white;
        color: #000;
    }}

    .inner-tab-content {{
        display: none;
    }}

    .inner-tab-content.active {{
        display: block;
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
        {'<a class="nav-link" href="#missing">Missing</a>' if profile['summary'].data['num_missing_cells'] > 0 else ''}
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

document.addEventListener("click", function(e) {
    if (e.target.classList.contains("more-details-btn")) {
        const panelId = e.target.getAttribute("data-target");
        const panel = document.getElementById(panelId);

        // Toggle panel visibility
        const isOpen = panel.classList.toggle("open");

        // Update button text
        e.target.textContent = isOpen ? "Less details" : "More details";
    }
});

// Tab system that works for nested panels
document.addEventListener("click", function(e) {
    if (!e.target.classList.contains("tab-button")) return;

    const tabId = e.target.getAttribute("data-tab");

    // Scope: find nearest container that holds tab-content
    const container = e.target.closest(".details-panel") || 
                      e.target.closest(".section-box");

    // Deactivate all tabs in this container
    container.querySelectorAll(".tab-button").forEach(btn => {
        btn.classList.remove("active");
    });
    container.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // Activate clicked tab + its content
    e.target.classList.add("active");
    container.querySelector("#" + tabId).classList.add("active");
});

// Inner tab system (Extreme Values)
document.addEventListener("click", function(e) {
    if (!e.target.classList.contains("inner-tab-button")) return;

    const tabId = e.target.getAttribute("data-inner-tab");
    if (!tabId) return;

    // Scope: nearest inner-tabs container
    const tabsContainer = e.target.closest(".inner-tabs");
    if (!tabsContainer) return;

    // Content scope: parent that holds inner-tabs + inner-tab-content
    const contentScope = tabsContainer.parentElement;

    // Deactivate all inner buttons in this group
    tabsContainer.querySelectorAll(".inner-tab-button").forEach(btn => {
        btn.classList.remove("active");
    });

    // Deactivate all inner contents in this scope
    contentScope.querySelectorAll(".inner-tab-content").forEach(tab => {
        tab.classList.remove("active");
    });

    // Activate clicked button
    e.target.classList.add("active");

    // Activate matching content
    const targetContent = contentScope.querySelector("#" + tabId);
    if (targetContent) {
        targetContent.classList.add("active");
    }
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
                if alert.startswith("high_correlation_"):
                        rdict[ data[col][alert] ] = ["High Correlation", "grey", col]
                if alert == "negatives":
                        rdict[ data[col][alert] ] = ["Negatives", "blue", col]
                if alert == "zeros":
                        rdict[ data[col][alert] ] = ["Zeros", "blue", col]
                if alert == "infinity":
                        rdict[ data[col][alert] ] = ["Infinity", "blue", col]

        return rdict, num_alerts

    def linkColInAlert(alerts_data):
        new_alerts_data = {}
        for alert in alerts_data:
            if "is highly overall correlated with " in alert:
                
                col1 = alerts_data[alert][2]
                col2 = alert.split(" is highly overall correlated with ")[1]
                new_alert = f'<a class="nav-link" href="#v-{col1}">{col1}</a>' + " is highly overall correlated with " + f'<a class="nav-link" href="#v-{col2}">{col2}</a>' 
            else:
                col = alerts_data[alert][2]
                new_alert = f'<a class="nav-link" href="#v-{col}">{col}</a>' + alert.split(f"{col}")[-1]
            new_alerts_data[new_alert] = alerts_data[alert]
        return new_alerts_data

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
    new_alerts_data = linkColInAlert(alerts_data)


    overview_html = build_table_component(overview_data, "Dataset Statistics", "1/2")
    col_html = build_table_component(col_data, "Variable Types", "1/2")
    alerts_html = build_alert_table(new_alerts_data)

    alerts_data = alerts_data.values()

    

    # ---- Build tabbed section ----
    section_html = f"""
    <div class="section anchor-target" id="overview">
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
    rows = profile["summary"].data['rows']
    html_sections = []

    col_alerts = {}

    for col in columns:
        col_alerts[col] = []

    for alert in var_alerts:
        if (alert[0], alert[1]) in col_alerts[alert[2]]:
            continue
        col_alerts[alert[2]].append( (alert[0], alert[1]) ) 

    for col in columns:
        col_data = columns[col]
        dtype = col_data["type"]

        col_alert_html = ""

        for col_alert_entries in col_alerts[col]:
                
            col_alert_html += f"""
            <div class='value-{col_alert_entries[1]}'>{col_alert_entries[0]}</div>
            """

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

           

            stats_table_data1 = {
                    "Minimum": col_data["min"],
                    "5-th percentile" : col_data["5thp"],
                    "Q1" : col_data["Q1"],
                    "Median" : col_data["median"],
                    "Q3": col_data["Q3"],
                    "95-th percentile": col_data["95thp"],
                    "Maximum": col_data["max"],
                    "Range": col_data["range"],
                    "Interquartile range (IQR)" : col_data["IQR"]
                }

            stats_table_data2 = {
                    "Standard deviation": col_data["std"],
                    "Coefficient of variation (CV)": col_data["coefficient_of_variation"],
                    "Kurtosis": col_data["kurtosis"],
                    "Mean": col_data["mean"],
                    "Median Absolute Deviation (MAD)": col_data["MAD"],
                    "Skewness": col_data["skew"],
                    "Sum": col_data["sum"],
                    "Variance": col_data["variance"],
                    "Monotonicity": col_data["monotonicity"]
                }
            
            cvs = col_data["common_values"]
            common_values_data = [
                cvs[0],
                cvs[1],
                cvs[2],
                cvs[3],
                cvs[4],
                cvs[5],
                cvs[6],
                cvs[7],
                cvs[8],
                cvs[9]
                ]
            total_common_values = sum([i[1] for i in common_values_data])
            if col_data["num_missing"] > 0:
                common_values_data.append( ["Missing Values", col_data["num_missing"], col_data["pct_missing"]] )
            common_values_data.append([
                f"Other Values({col_data["num_unique"] - 10})", 
                rows - total_common_values - col_data['num_missing'], 
                (rows - total_common_values) / rows
                ])
            minevs = col_data["min_values"]
            maxevs = col_data["max_values"]
            extreme_values_min_data = [
                minevs[0],
                minevs[1],
                minevs[2],
                minevs[3],
                minevs[4],
                minevs[5],
                minevs[6],
                minevs[7],
                minevs[8],
                minevs[9],
            ]
            extreme_values_max_data = [
                maxevs[0],
                maxevs[1],
                maxevs[2],
                maxevs[3],
                maxevs[4],
                maxevs[5],
                maxevs[6],
                maxevs[7],
                maxevs[8],
                maxevs[9],
            ]

            stats_table_html1 = build_table_component(stats_table_data1, "Quantile Statistics", "1/2")
            stats_table_html2 = build_table_component(stats_table_data2, "Descriptive Statistics", "1/2")

            common_values_table_html = build_frequency_table(common_values_data, "", "1")
            extreme_values_min_table_html = build_frequency_table(extreme_values_min_data, "", "1")
            extreme_values_max_table_html = build_frequency_table(extreme_values_max_data, "", "1")

            section_html = f"""
            <div class="section-box variable-box anchor-target" id="v-{col}">
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

                <div class="details-toggle-row">
                    <div class="more-details-btn" data-target="details-{col}">
                        More details
                    </div>
                </div>

                <div class="details-panel" id="details-{col}">
        
                    <div class="tabs details-tabs">
                        <button class="tab-button active" data-tab="stats-{col}">Statistics</button>
                        <button class="tab-button" data-tab="common-{col}">Common Values</button>
                        <button class="tab-button" data-tab="extreme-{col}">Extreme Values</button>
                    </div>

                    <div class="tab-content active" id="stats-{col}">
                        <div class="row-flex">
                            {stats_table_html1}
                            {stats_table_html2}
                        </div>
                    </div>

                    <div class="tab-content" id="common-{col}">
                        {common_values_table_html}
                    </div>

                    <div class="tab-content" id="extreme-{col}">

                        

                        <div class="tabs inner-tabs">
                            <button class="inner-tab-button active" data-inner-tab="extreme-min-{col}">Minimum Values</button>
                            <button class="inner-tab-button" data-inner-tab="extreme-max-{col}">Maximum Values</button>
                        </div>
    
                        <div class="inner-tab-content active" id="extreme-min-{col}">
                            {extreme_values_min_table_html}
                        </div>

                        <div class="inner-tab-content" id="extreme-max-{col}">
                            {extreme_values_max_table_html}
                        </div>

                    
 
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

            freq_table_data = [
                    [entry, col_data["counts"][entry], col_data["percentages"][entry]] for entry in col_data["counts"].keys()
                ]

            freq_table_html = build_frequency_table(freq_table_data, "", "1")


            section_html = f"""
            <div class="section-box variable-box anchor-target" id="v-{col}">
                <div class="variable-title">{col}</div>
                <div class="variable-type">Categorical</div>
                {col_alert_html}
                <div class="row-flex">
                        {col_sum_table_html}
                        <div class="graph-container">
                            <img src="{bar_path}" alt="{col} Histograph">
                        </div>
                </div>
                <div class="details-toggle-row">
                    <div class="more-details-btn" data-target="details-{col}">
                        More details
                    </div>
                </div>

                <div class="details-panel" id="details-{col}">

                    {freq_table_html}
              
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

            section_html = f"""
            <div class="section-box variable-box anchor-target" id="v-{col}">
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
    <div class="section anchor-target" id="variables">
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
    <div class="section anchor-target" id="interactions">
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
    <div class="section anchor-target" id="correlations">
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
    <div class="section anchor-target" id="missing">
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
    <div class="section anchor-target" id="sample">
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

def build_frequency_table(data: list, title: str, width: str = "1/2") -> str:
    """
    data: list of tuples (value, count, percent)
          percent should be a float between 0 and 1
    """

    width_class = {
        "1": "table-w1",
        "1/2": "table-w2",
        "1/3": "table-w3"
    }.get(width, "table-w2")

    rows_html = ""
   
    for value, count, pct in data:
        pct_percent = f"{pct*100:.1f}%"
        pct_width = pct * 100  

        rows_html += f"""
        <tr>
            <td class="freq-value">{value}</td>
            <td class="freq-count">{count}</td>
            <td class="freq-bar-cell">
                <div class="freq-bar" style="width:{pct_width}%;"></div>
                <div class="freq-percent-text">{pct_percent}</div>
            </td>
        </tr>
        """

    return f"""
    <div class="table-wrapper {width_class}">
        <div class="table-title">{title}</div>
        <div class="table-box">
            <table class="freq-table">
                <thead>
                    <tr>
                        <th>Value</th>
                        <th style="text-align:right;">Count</th>
                        <th style="text-align:right;">Frequency</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """
