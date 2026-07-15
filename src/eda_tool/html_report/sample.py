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
