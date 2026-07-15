from pathlib import Path
from typing import Dict
from .style_string import style_string
from .script_string import script_string
from .overview import build_overview_section
from .variables import build_variables_section
from .interactions import build_interactions_section
from .correlations import build_correlations_section
from .missing import build_missing_section
from .sample import build_sample_section

def build_html_report(profile: Dict, output_dir: str) -> str:
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

</head>
{style_string}

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
    html += build_interactions_section(profile, output_dir)
    html += build_correlations_section(profile["correlations"].data, output_dir)
    html += build_missing_section(profile, output_dir)
    html += build_sample_section(profile)
    html += f"""
</div>
</body>
{script_string}
</html>
"""
    return html