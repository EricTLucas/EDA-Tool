import os

def build_correlations_section(corr_df, output_dir, width="1"):
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