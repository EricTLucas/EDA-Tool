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