import os
def build_interactions_section(profile, output_dir):
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