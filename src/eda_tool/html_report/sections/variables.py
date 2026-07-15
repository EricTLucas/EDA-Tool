import os
from .utils import build_table_component, build_frequency_table

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
            common_values_data.append([
                f"Other Values({col_data["num_unique"] - 10})", 
                rows - total_common_values, 
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