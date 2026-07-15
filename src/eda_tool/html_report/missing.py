import os
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