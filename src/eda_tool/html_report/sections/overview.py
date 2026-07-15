from .utils import build_table_component

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